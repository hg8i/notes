#!/bin/env python3

from setup import *
from command_view import commandView
from notes_view import notesView
from files_view import filesView
from index import noteindex
import editDialog

class interface:
    def __init__(self,screen,index):

        self._screen = screen
        self._index = index
        curses.curs_set(0)

        if not os.path.exists(settings["delPath"]):
            os.makedirs(settings["delPath"])
        if not os.path.exists(settings["tmpPath"]):
            os.makedirs(settings["tmpPath"])

        self._shortcutMap = settings["shortcutMap"]
        self._helpMessage = settings["helpMessage"]
        self._hotkeyMap   = settings["hotkeyMap"]

        # map commands onto functions
        self._commandMap = {}
        self._commandMap["sort"]   = lambda cmds: self._changeSort(cmds)
        self._commandMap["pickle"] = lambda cmds: self._savePickle()
        self._commandMap["key"]    = lambda cmds: self._setSearchKey(cmds)
        self._commandMap["new"]    = lambda cmds: self._newNote(cmds)
        self._commandMap["delete"] = lambda cmds: self._deleteNote()
        self._commandMap["change"] = lambda cmds: self._changeNote()
        self._commandMap["edit"]   = lambda cmds: self._editMeta()
        self._commandMap["help"]   = lambda cmds: self._showHelp()
        self._commandMap["search"] = lambda cmds: self._performSearch()
        self._commandMap["cfocus"] = lambda cmds: self._changeFocus()
        self._commandMap["command"] = lambda cmds: self._launchCommand()
        self._commandMap["quit"] = lambda cmds: quit()

        # set up subscreens
        self._resize()

        self.run()

    def _resize(self):
        # set up subscreens
        self._makeScreens()

        self._views = {}
        self._cv = commandView(self._commandScreen)
        self._views["nv"] = notesView(self._notesScreen,self._index)
        self._views["fv"] = filesView(self._filesScreen,self._views["nv"],self._index)
        self._viewNames = ["fv","nv"]
        self._focus = 0


    def run(self):
        """ Run loop for main program """

        while True:
            char = self._screen.getch()
            self._processCharacter(char)

    def _performSearch(self):
        name = self._views["fv"].getCurrentFileName()
        cmd = self._cv.run(init="/")
        log("-"*50)
        log("Searching for ",cmd)
        log("-"*50)
        if len(cmd)==0:
            self._index.clearSearch()
            self._cv.setStatus(f"Search cleared")
        else:
            log("Starting search")
            self._index.search(cmd)
            self._cv.setStatus(f"Searching for: {cmd}")
            log("Done search")

        self._views["fv"].selectName(name)
        self._views["fv"].ping()

    def _dialogPopup(self,fields):
        """ Popup to get a single string reply
        """
        nFields = len(fields)

        screenY,screenX = self._screen.getmaxyx()
        height = 7+(nFields-1)*3
        width = 60
        x = int((screenX-width)/2)
        y = int((screenY-height)/2)
        dialogScreen = self._screen.subwin(height,width,y,x)

        edits = editDialog.editDialog(dialogScreen,fields)
        return edits.run()

    def _newNote(self,cmds):
        """ Create new note
        """
        if len(cmds)==1:
            changed,info = self._dialogPopup({"name":"","tags":""})
            name = info["name"].split()
            tags = info["tags"].split(",")
            for k,v in self._views.items(): v.ping()
            name = " ".join(name)
        else:
            name = " ".join(cmds[1:])
            tags = []
        shortname = name.replace(" ","_")
        status = self._index.createNote(name=name,shortname=shortname,tags=tags)

        self.ping()

        self._cv.setStatus(status)

    def _setSearchKey(self,cmds):
        """ Set key for search results
        """
        if len(cmds)==2:
            self._index.setSearchKey(cmds[1])
            self._cv.setStatus(f"Search key set to {cmds[1]}")
        else:
            self._index.setSearchKey("all")
            self._cv.setStatus(f"Search key set to all")
        self.ping()

    def _showHelp(self):
        lines = defaultdict(lambda:defaultdict(lambda:" "))
        for shortcut,name in self._shortcutMap.items():
            lines[name]["shortcut"] = shortcut
            lines[name]["help"] = self._helpMessage[name]
        for hotkey,name in self._hotkeyMap.items():
            lines[name]["hotkey"] = hotkey
            lines[name]["help"] = self._helpMessage[name]

        screenY,screenX = self._screen.getmaxyx()
        height = 7+(len(lines))*1
        width = 70
        x = int((screenX-width)/2)
        y = int((screenY-height)/2)
        dialogScreen = self._screen.subwin(height,width,y,x)

        edits = editDialog.popupDialog(dialogScreen,lines)
        return edits.run()

    def _editMeta(self):
        """ Edit metadata for existing note
        """
        # get name of current note
        name = self._views["fv"].getCurrentFileName()
        # get meta data
        meta = self._index.getMeta(name)
        # turn tags into list
        meta["tags"] = ",".join(meta["tags"])
        changed,meta = self._dialogPopup(meta)
        meta["tags"] = meta["tags"].split(",")
        # update file
        meta = self._index.setMeta(name,meta)
        self._views["fv"].selectName(name)
        self._views["fv"].ping()
        self._cv.setStatus(f"Changed name is still {name}")

    def _safeCopyDir(self,copyFrom,copyTo):
        os.popen(f"rm -rf {copyTo}")
        while os.path.exists(copyTo): time.sleep(0.1)
        os.popen(f"cp -r {copyFrom} {copyTo}")
        while not os.path.exists(copyTo): time.sleep(0.1)


    def _changeNote(self):
        """ Edit the note
        """

        name = self._views["fv"].getCurrentFileName()
        path = self._index.getPath(name)

        # check note's meta for a block
        if self._index.isBlocked(name):
            self._cv.setStatus(f"Unable to edit {name} due to an editing block")
            return

        # put block in note's meta
        self._index.block(name)

        # copy note to tmp directory
        tmpPath = os.path.join(settings["tmpPath"],os.path.basename(path))
        tmpNotePath = os.path.join(tmpPath,"note.md")
        self._safeCopyDir(path,tmpPath)

        # edit note
        curses.endwin()
        EDITOR = os.environ.get("EDITOR","vim")
        call([EDITOR, tmpNotePath])

        # copy back
        self._safeCopyDir(tmpPath,path)

        # remove block
        self._index.unblock(name)

        # set file index to this file
        self._views["fv"].selectName(name)

        self._cv.setStatus(f"Edited note")
        self.ping()


    def ping(self):
        # should be done in order
        self._views["fv"].ping()
        self._views["nv"].ping()


    def _deleteNote(self):
        name = self._views["fv"].getCurrentFileName()
        status = self._index.deleteNote(name)
        self._cv.setStatus(status)
        self.ping()

    def _changeSort(self,cmds):
        # Sorts the index by argument
        name = self._views["fv"].getCurrentFileName()
        log("Storing",name)
        if len(cmds)==2:
            self._index.setSort(cmds[1])
            # self._views["fv"].refreshIndex()
            self._cv.setStatus(f"Sorting by: {cmds[1]}")
        else:
            self._cv.setStatus(f"Unable to sort")
        self._views["fv"].selectName(name)
        self._views["fv"].ping()

    def _savePickle(self):
        log("Saving pickle file")
        self._cv.setStatus(f"Wrote pickle {self._index.getPicklePath()}")
        self._index.pickle()


    def _parseCommand(self,cmd):
        cmds = cmd.split()
        if len(cmd)==0: return
        first = cmds[0]
        log("-"*50)
        log("Processing command",cmds)
        log("-"*50)
    
        shortcutMap = self._shortcutMap

        if first in self._commandMap.keys():
            self._commandMap[first](cmds)
        elif shortcutMap[first] in self._commandMap.keys():
            # use shortcut letter
            self._commandMap[shortcutMap[first]](cmds)
        else:
            self._cv.setStatus(f"Invalid command")

    def _jumpTo(self,number):
        log("NUMBER",number)
        self._views["fv"].goto(int(number))
        self.ping()

    def _changeFocus(self):
        self._focus+=1

    def _launchCommand(self):
        cmd = self._cv.run(init=":")
        self._parseCommand(cmd)

    def _processCharacter(self,char):
        """ Process each character
        """

        # run a command
        if chr(char) in self._hotkeyMap.keys():
            command = self._hotkeyMap[chr(char)]
            self._commandMap[command](None)
        elif chr(char) in string.digits:
            number = self._cv.run(init=chr(char))
            self._jumpTo(chr(char)+number)
        elif char == curses.KEY_RESIZE:
            name = self._views["fv"].getCurrentFileName()
            self._resize()
            self._views["fv"].selectName(name)
            self._views["fv"].ping()
        else:
            log("Processing character",chr(char))
            view = self._viewNames[self._focus%len(self._viewNames)]
            log("For view",view)
            self._views[view].processCharacter(char)
            log("Done processing character",chr(char))


    def _makeScreens(self):
        """ Make screen for text details object """
        screenY,screenX = self._screen.getmaxyx()
        # if 1:
        try:
            # command screen, line at bottom
            # height width, y, x
            self._commandScreen = self._screen.subwin(1,screenX-0,screenY-1,0)
            # files view
            fsWidth = settings["filesWidth"]
            self._filesScreen = self._screen.subwin(screenY-1,fsWidth,0,0)
            # notes view
            nvWidth = screenX-fsWidth
            self._notesScreen = self._screen.subwin(screenY-1,nvWidth,0,fsWidth)

        except:
            # The screen is probably too small. Wait for a new size
            while self._screen.getch()!=curses.KEY_RESIZE:
                pass
            self._makeScreens()



def main(screen):
    curses.start_color()
    curses.use_default_colors()

    index = noteindex(loadPickle=0)

    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)
    i = interface(screen,index)

if __name__=="__main__":
    wrapper(main)

