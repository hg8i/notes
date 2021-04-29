from __future__ import division
from setup import *

from functions import *
from command_view import *
from notes_view import *
from files_view import *

# ==================================================
# Note viewing app
# ==================================================

class interface:
    def __init__(self,screen):
        """ Interface handels creating
            1) Calendar view
            2) Text details view
            3) Text input window
        """
        self._screen = screen
        curses.curs_set(0)
        os.popen("rm log.txt")

        if not os.path.exists(settings["indexPath"]):
            index = {}
            data = pickle.dump(index,open(settings["indexPath"],"w"))


        # set up subscreens
        self._makeScreens()
        self._cv = commandView(self._commandScreen)
        self._nv = notesView(self._notesScreen)
        self._fv = filesView(self._filesScreen,self._nv)
        self._functions = functions(self._nv,self._fv)

        self._selectedWindow = "files"

        # self._nv.load("290421-abc.note")
        self._nv.load(self._fv._curName())


        # setup

        self.run()

    def _makeScreens(self):
        """ Make screen for text details object """
        screenY,screenX = self._screen.getmaxyx()
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

    def _parseCommand(self,command):
        """ Process a given command
        """
        command=command.split(" ")
        if len(command)==0: return
        function = command[0]
        args = list(command[1:])

        if function in ["newNote","n"]:
            noteName = self._functions.newNote(args)
            if noteName: self._nv.load(noteName)
            # update file list
            self._fv.ping()

        elif function in ["editAttributes","e"]:
            noteName = self._functions.editAttributes(self._screen,args)
            # if noteName: self._nv.load(noteName)
            # update file list
            self._fv.ping()
            self._nv.ping()

        elif function in ["cancelFilter","f"]:
            noteName = self._functions.filterNotes()
        elif function in ["filterNotes","f"]:
            noteName = self._functions.filterNotes(args)

        elif function in ["deleteNote","rm"]:
            # insert media
            noteName = self._functions.deleteNote(args)

        elif function in ["insertMedia","i"]:
            # insert media
            noteName = self._functions.insertMedia(args)

        elif function in ["quit","q"]:
            quit()

    def _edit(self):
        """ Edit current file
        """
        notePath = self._nv.curPath()["note"]
        curses.endwin()
        EDITOR = os.environ.get("EDITOR","vim")
        call([EDITOR, notePath])
        # call([EDITOR, "-c 'set filetype=md'", notePath])
        # call([EDITOR, "-c ':set filetype=md'", notePath])
        self._screen.refresh()
        # tell note view to update
        self._nv.ping()

        # update database
        db = pickle.load(open(self._nv.curPath()["data"]))
        db["lastEdited"] = time.time()
        if "allEditTimes" not in db.keys(): db["allEditTimes"]=[]
        db["allEditTimes"].append(time.time())

    def _processCharacter(self,char):
        """ Process each character
        """
        if char==ord("q"):
            self._parseCommand("q")

        # edit a file settings
        elif char==ord("e"):
            self._parseCommand("e")

        # edit a file
        elif char==ord("c"):
            self._edit()

        # run a search
        elif char==ord("/"):
            cmd = self._cv.run(init="/")
            utils._text(self._screen,1,1,cmd,color=utils.color_red)

        # run a command
        elif char==ord(":"):
            cmd = self._cv.run(init=":")
            self._parseCommand(cmd)

        # control note view
        elif char==ord("\t"):
            self._selectedWindow = ["notes","files"][self._selectedWindow=="notes"]
            if self._selectedWindow=="notes": 
                self._nv.select(1)
                self._fv.select(0)
            elif self._selectedWindow=="files": 
                self._nv.select(0)
                self._fv.select(1)



        elif char == curses.KEY_RESIZE:
            self._commandScreen.clear()
            self._filesScreen.clear()
            self._screen.clear()
            self._makeScreens()
            # update views with new screens
            self._cv.update(screen=self._commandScreen)
            self._fv.update(screen=self._filesScreen)
            self._nv.update(screen=self._notesScreen)
            # refill data
            self._nv.ping()
            self._fv.ping()
            self._cv.ping()
            # refresh screens
            # self._commandScreen.refresh()
            # self._filesScreen.refresh()
            self._screen.refresh()

        elif char in [ord("n"),ord("N")]:
            self._fv.processCharacter(char)

        else:
            if self._selectedWindow=="notes":
                self._nv.processCharacter(char)
            elif self._selectedWindow=="files":
                self._fv.processCharacter(char)
                


    def run(self):
        """ Run loop for main program """
        while True:
            char = self._screen.getch()
            self._processCharacter(char)




def main(screen):
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)
    i = interface(screen)

if __name__=="__main__":
    wrapper(main)


