from setup import *
import controller
import view
import noteloader
import editWatcher
# import dialog

class model:

    def __init__(self,screen,index):
        self._screen = screen
        self._index  = index
        # thread communication
        self._manager = multiprocessing.Manager()
        self._controller_i = self._manager.Queue()
        self._controller_o = self._manager.Queue()
        self._view_i = self._manager.Queue()
        self._view_o = self._manager.Queue()
        self._note_i = self._manager.Queue()
        self._note_o = self._manager.Queue()
        self._file_i = self._manager.Queue()
        self._file_o = self._manager.Queue()
        self._markdown_o = self._manager.Queue()
        self._char_queue = self._manager.Queue() # input from controller
        curses.curs_set(0)

        self.queues_i = {
            "controller":self._controller_i,
            "view":self._view_i,
            "note":self._note_i,
            "file":self._file_i,
        }

        self.queues_o = {
            "controller":self._controller_o,
            "view":self._view_o,
            "note":self._note_o,
            "file":self._file_o,
        }

        # Events (for pausing threads)
        # self._controller_e = multiprocessing.Event()
        # self._view_e       = multiprocessing.Event()
        # self._note_e       = multiprocessing.Event()
        # self._file_e       = multiprocessing.Event()
        self._event        = self._manager.Event()

        # # set events
        # self._controller_e.set()
        # self._view_e.set()
        # self._note_e.set()
        # self._file_e.set()

        # objects
        self._controller = controller.controller(self._screen,inputq=self._controller_i,outputq=self._controller_o,charq=self._char_queue,event=self._event)
        self._view = view.view(self._screen,inputq=self._view_i,outputq=self._view_o)

        self.noteloaderThreads = []
        self.markdownThreads = []

        self._commandBuffer=""
        self._commandLeader=":"
        self._curserPos=0

        self._filePos = 0
        self._noteScrollPos = 0

        self._iFocus = 0
        self._focus = "filesview"

        # TODO: fill in all these commands!
        # map commands onto functions
        self._hotkeyMap   = settings["hotkeyMap"]
        self._shortcutMap = settings["shortcutMap"]
        self._helpMessage = settings["helpMessage"]
        self._commandMap = {}
        self._commandMap["publish"]= lambda cmds: self._publishWebsite()
        self._commandMap["webview"]= lambda cmds: self._webview()
        self._commandMap["sort"]   = lambda cmds: self._changeSort(cmds)
        self._commandMap["key"]    = lambda cmds: self._setSearchKey(cmds)
        self._commandMap["search"] = lambda cmds: self._performSearch()
        self._commandMap["new"]    = lambda cmds: self._newNote(cmds)
        self._commandMap["delete"] = lambda cmds: self._deleteNote()
        self._commandMap["change"] = lambda cmds: self._changeNote()
        self._commandMap["edit"]   = lambda cmds: self._editMeta()
        self._commandMap["help"]   = lambda cmds: self._showHelp()
        self._commandMap["cfocus"] = lambda cmds: self._changeFocus()
        self._commandMap["command"]= lambda cmds: self._launchCommand()
        self._commandMap["quit"]   = lambda cmds: self._quit()

        self._updateFileView()
        self._updateNotesView()

        # Hopefully helps with garbage printed on start
        self._view_i.put({"type":"forceUpdate"})

    def _updateCommand(self):
        # Updates command view with the current command being entered
        data = {}
        data["type"] = "commandview"
        data["instruction"] = "textentry"
        data["leader"] = self._commandLeader
        data["content"] = self._commandBuffer
        data["curser"] = self._curserPos
        self._view_i.put(data)

    def _runDialog(self,fields,inputs=False,name=None):
        # Runs the given dialog
        activeField = 0

        # Setup dialog window
        data = {}
        data["type"] = "dialogview"
        data["instruction"] = "newdialog"
        data["fields"] = fields
        data["activeField"] = activeField
        data["inputs"] = inputs
        data["name"] = name
        self._view_i.put(data)

        while True:
            data = {}
            data["type"] = "dialogview"
            char = self._char_queue.get()
            if char in [settings["escapeChar"],settings["enterChar"],ord("h"),ord("q"),ord("n")]:
                data["instruction"] = "closedialog"
                self._view_i.put(data)
                return fields
            elif char == ord("j"):
                activeField=(activeField+1)%len(fields)
                data["instruction"] = "updatevalue-activeField"
                data["value"] = activeField
                self._view_i.put(data)
            elif char == ord("k"):
                activeField=(activeField-1)%len(fields)
                data["instruction"] = "updatevalue-activeField"
                data["value"] = activeField
                self._view_i.put(data)
            elif char == ord("i"):
                fields[activeField]["content"] = self._runDialogEditText(fields[activeField],activeField)
            elif char == ord("c"):
                fields[activeField]["cursorPos"] = 0
                fields[activeField]["content"] = ""
                fields[activeField]["content"] = self._runDialogEditText(fields[activeField],activeField)


    def _runDialogEditText(self,field,activeField):
        # note: field has name, content, cursorPos
        # refresh value in case of clear
        field["showCursor"]=True
        data = {}
        data["type"] = "dialogview"
        data["instruction"] = "updatevalue-fieldData"
        data["activeField"] = activeField
        data["field"] = field
        self._view_i.put(data)

        while True:
            data = {}
            data["type"] = "dialogview"
            data["instruction"] = "updatevalue-fieldData"
            data["activeField"] = activeField
            char = self._char_queue.get()
            if char in [settings["enterChar"],settings["escapeChar"]]:
                # Remove cursor
                data = {}
                field["showCursor"]=False
                data["type"] = "dialogview"
                data["instruction"] = "updatevalue-fieldData"
                data["activeField"] = activeField
                data["field"] = field
                self._view_i.put(data)
                return field["content"]
            field["content"],field["cursorPos"]=updateBuffer(field["content"],char,pos=field["cursorPos"])
            data["field"] = field

            self._view_i.put(data)
            # return


    def _clearCommand(self):
        # Clears command view of text
        data = {}
        data["type"] = "commandview"
        data["instruction"] = "clear"
        self._view_i.put(data)

    def _notify(self,message):
        # Puts a notification message in command view
        data = {}
        data["type"] = "commandview"
        data["instruction"] = "notify"
        data["content"] = message
        self._view_i.put(data)

    def _getCommandText(self,init=":"):
        curses.curs_set(1)
        self._commandLeader = init
        self._commandBuffer = ""
        self._curserPos = 0
        self._updateCommand()
        curses.curs_set(0)

        # capture command
        while True:
            char = self._char_queue.get()
            # emplace commandview frame
            if char==settings["enterChar"]:
                return self._commandBuffer
            self._commandBuffer,self._curserPos=updateBuffer(self._commandBuffer,char,pos=self._curserPos)
            self._updateCommand()


    def _parseCommand(self,cmd):
        cmds = cmd.split()
        if len(cmd)==0: return
        first = cmds[0]
        log("-"*50)
        log("MODEL: Processing command",cmds)
        log("-"*50)
    
        shortcutMap = self._shortcutMap

        if first in self._commandMap.keys():
            self._commandMap[first](cmds)
        elif shortcutMap[first] in self._commandMap.keys():
            # use shortcut letter
            self._commandMap[shortcutMap[first]](cmds)
        else:
            self._notify(f"Invalid command: {cmd}")

    # ================ CLI functions ===================

    def _newNote(self,cmds=None):
        if cmds and len(cmds)>1:
            name = " ".join(cmds[1:])
            shortname = "_".join(cmds[1:])
            tags = []
        else:
            fields = []
            fields.append({"name":"name","content":"","cursorPos":0,"showCursor":False})
            fields.append({"name":"tags","content":"","cursorPos":0,"showCursor":False})
            fields = self._runDialog(fields,inputs=True,name="New Note")
            # parse response
            name = [f["content"] for f in fields if f["name"]=="name"][0]
            tags = [f["content"] for f in fields if f["name"]=="tags"][0].split(",")
            shortname = name.replace(" ","_")

        # if "name" not provided, don't make new note
        nameGiven = [f["content"] for f in fields if f["name"]=="name"]
        if any(nameGiven):
            # make new note with index
            status = self._index.createNote(name=name,shortname=shortname,tags=tags)
            self._notify(status)
        self._updateFileView()
        self._updateNotesView()

    def _editMeta(self,cmds=None):
        name = self._index[self._filePos]
        meta = self._index.getMeta(name)
        meta["tags"] = ",".join(meta["tags"])
        # prepare fields
        fields = []
        for name,content in meta.items():
            if isinstance(content,datetime):
                content = self._index.dateToS(content)
            else:
                content = str(content)
            # d = datetime.datetime.strptime(s,"%d/%m/%y %H:%M::%S")
            x = len(content)
            fields.append({"name":name,"content":content,"cursorPos":x,"showCursor":False})
        fields = self._runDialog(fields,inputs=1,name="Edit Metadata")
        # parse response
        meta = {f["name"]:f["content"] for f in fields}
        meta["tags"] = meta["tags"].split(",")
        # update meta data
        status = self._index.setMeta(meta)
        self._notify(status)

        self._updateFileView()
        self._updateNotesView()


    def _deleteNote(self):
        name = self._index[self._filePos]
        status = self._index.deleteNote(name)
        self._notify(status)
        self._updateFileView()
        self._updateNotesView()

    def _webview(self):
        name = self._index[self._filePos]
        meta = self._index.getMeta(name)
        fullname = meta["dirName"]

        md = markdown(fullname,self._markdown_o,self._event)
        self.markdownThreads.append(multiprocessing.Process(target=md.run_view))
        self.markdownThreads[-1].start()


    def _publishWebsite(self):
        name = self._index[self._filePos]
        meta = self._index.getMeta(name)
        fullname = meta["dirName"]

        md = markdown(fullname,self._markdown_o,self._event)
        self.markdownThreads.append(multiprocessing.Process(target=md.run_publish))

        self.markdownThreads[-1].start()

        # status = f"Publishing to {settings['siteUrl'].format(fullname)}"
        # self._notify(status)

        # mdThread.join()
        # status = f"Published to {settings['siteUrl'].format(fullname)}"
        # self._notify(status)


    def _showHelp(self):
        fields = []
        fields.append({"name":"Commands","divider":"-"})
        for shortcut,name in self._shortcutMap.items():
            data = {}
            data["name"] = f"{shortcut}, {name}"
            data["content"] = self._helpMessage[name]
            data["cursorPos"] = 0
            fields.append(data)
        fields.append({"name":"Hotkeys","divider":"-"})
        for hotkey,name in self._hotkeyMap.items():
            data = {}
            data["name"] = f"{hotkey}, {name}".replace("\t","tab")
            data["content"] = self._helpMessage[name]
            data["cursorPos"] = 0
            fields.append(data)
        fields.append({"name":"Info","divider":"-"})
        fields.append({"name":"dataPath","cursorPos":0,"content":settings["dataPath"]})
        fields.append({"name":"htmlPath","cursorPos":0,"content":settings["htmlPath"]})
        fields.append({"name":"indexPath","cursorPos":0,"content":settings["indexPath"]})
        fields.append({"name":"tmpPath","cursorPos":0,"content":settings["tmpPath"]})
        self._runDialog(fields,name="Help Menu")

    def _changeSort(self,cmds):
        if len(cmds)<=1:
            self._index.setSort("modified")
            self._notify(f"Sorting: modified")
        elif cmds[1].lower() in ["modified","created","name","tag"]:
            self._index.setSort(cmds[1].lower())
            self._notify(f"Sorting: {cmds[1]}")
        else:
            self._notify(f"Invalid sort key: {cmds[1]}")
        self._updateFileView()
        self._updateNotesView()

    def _performSearch(self):
        # note current selected file name
        oldSelectedName = self._index[self._filePos]
        cmd = self._getCommandText(init="/")
        if len(cmd)==0:
            self._index.clearSearch()
            self._notify(f"Search cleared")
        else:
            self._notify(f"Searching: {cmd}")
            log("Starting search")
            self._index.search(cmd)
            log("Done search")
        # TODO: try to update cursor to have same file selected
        indexOfOldName = self._index.getIndexOfName(oldSelectedName)
        if indexOfOldName!=None: self._filePos = indexOfOldName
        self._notify(f"index {indexOfOldName}")
        self._updateFileView()
        self._updateNotesView()

    def _setSearchKey(self,cmds):
        """ Set key for search results
        """
        if len(cmds)==2:
            self._index.setSearchKey(cmds[1])
            self._notify(f"Search key set to {cmds[1]}")
        else:
            self._index.setSearchKey("all")
            self._notify(f"Search key set to all")
        # update file view
        self._updateFileView()

    def _launchCommand(self,init=None):

        # get command
        cmd = self._getCommandText(init=":")

        # parse command
        self._parseCommand(cmd)

        # # save new commend into history
        # if init==":":
        #     self._history.append(text)
        #     # open(settings["commandHistoryPath"],"a").write(text+"\n") # TODO run in thread
        # log("Command history:"+str(self._history))

    # def _threadScreenPause(self):
    #     log("MODEL: threadScreenPause")
    #     # log("MODEL: pausing screen")
    #     # Stop the printing threads from printing
    #     # empty character queue 
    #     # while not self._char_queue.empty(): self._char_queue.get()
    #     # curses.curs_set(0)
    #     # self.sendPause("controller")
    #     # log("MODEL: paused controller")
    #     # self._controller_e.clear()
    #     # self._view_e.clear()
    #     log("MODEL: pausing view")
    #     self.sendPause("view")
    #     log("MODEL: paused view")
    #     curses.endwin() # comes after pausing so "x" still sent

    # def _threadScreenStart(self,name):
    #     # Resume the printing threads printing
    #     log("MODEL: threadScreenStart")
    #     curses.doupdate()
    #     # self._view_i.put({"type":"resume"})
    #     # self._controller_e.set()
    #     log("MODEL: update index")
    #     # self._view_e.set()
    #     self._filePos = self._index.getIndexOfName(name,resort=False)
    #     # empty character queue before returning to interface
    #     while not self._char_queue.empty():
    #         self._char_queue.get()
    #     log("MODEL: resume view")
    #     self.sendResume("view")
    #     self._updateFileView()
    #     self._updateNotesView()
    #     self._view_i.put({"type":"forceUpdate"})
    #     log("MODEL: threadScreenStart done")


    def sendPause(self,queue):
        log(f"MODEL: pausing {queue}")
        i = self.queues_i[queue]
        o = self.queues_o[queue]
        i.put({"type":"pause"})
        while o.get()["type"]!="confirm_pause":
            self._screen.addch(ord('x')) # to un-stick controller getch()
            time.sleep(0.05)

    def sendResume(self,queue):
        log(f"MODEL: resuming {queue}")
        i = self.queues_i[queue]
        o = self.queues_o[queue]
        i.put({"type":"resume"})
        while o.get()["type"]!="confirm_resume":
            time.sleep(0.05)

    def _changeNote(self):
        name = self._index[self._filePos]
        meta = self._index.getMeta(name)
        noteDir  = os.path.join(settings["dataPath"],meta["dirName"])
        notePath = os.path.join(noteDir,"note.md")
        log(f"MODEL: cange note {name}")


        tmpDir = os.path.join(settings["tmpPath"],meta["dirName"]+"_"+str(time.time()))
        tmpNotePath = os.path.join(tmpDir,"note.md")


        # copy files to temporary directory
        cmd = f"cp -r {noteDir} {tmpDir}"
        os.popen(cmd)
        self._notify("Copying remote to local")
        while not os.path.exists(tmpDir):
            time.sleep(0.01)
        self._notify("Checking note file copied")
        while not os.path.exists(tmpNotePath):
            time.sleep(0.05)

        # Make sure file isn't empty
        copiedSize = os.path.getsize(tmpNotePath)
        remoteSize = os.path.getsize(notePath)
        notePath = os.path.join(noteDir,"note.md")
        while copiedSize!=remoteSize:
            copiedSize = os.path.getsize(tmpNotePath)
            self._notify(f"Checking note file copied: {copiedSize}b")
            time.sleep(0.05)
        time.sleep(0.05)

        # Launch file watcher
        inputq = self._manager.Queue()
        outputq = self._manager.Queue()
        ew = editWatcher.editwatcher(noteDir,tmpDir,inputq=inputq,outputq=outputq)
        ewThread = multiprocessing.Process(target=ew.run)
        ewThread.start()

        # ===============================================
        self.sendPause("view")
        self.stopController()
        # self._threadScreenPause() # pause gui

        curses.endwin()

        # EDITOR="/home/prime/dev/notes/debug/echo.py"
        EDITOR = os.environ.get("EDITOR","vim")
        curses.curs_set(1)
        code = call([EDITOR, tmpNotePath])
        curses.curs_set(0)

        curses.doupdate()

        self.startController()

        self._filePos = self._index.getIndexOfName(name,resort=False)
        while not self._char_queue.empty():
            log("MODEL: non-empty queue!")
            self._char_queue.get()
        log("MODEL: resume view")
        self.sendResume("view")
        log("MODEL: threadScreenStart done")

        # ===============================================

        # close filewatcher
        inputq.put({"type":"close"})
        ewThread.join()

        # Message from edit watcher
        ewMessage = f"Syncing may have failed. Check {tmpNotePath}"
        while outputq.qsize():
            ewMessage = outputq.get()["message"]

        log("Edit watcher result:",str(ewMessage))
        self._notify(ewMessage)

        log(f"MODEL: cange note {name} done")

    def _changeFocus(self):
        self._iFocus+=1
        self._focus = ["filesview","notesview"][self._iFocus%2]

    def _quit(self):
        self._notify("Closing index")
        self._index.quit()
        self._notify("Closing view")
        self._view_i.put({"type":"quit"})
        # self._controller_i.put({"type":"quit"}) # TODO

        # consider terminate()
        for thread in self.noteloaderThreads:
            self._notify("Closing noteloader thread")
            thread.join()

        self._notify("Closing view thread")
        self.viewThread.join()
        self.controllerThread.terminate()

        quit()


    # =============== /CLI functions ===================

    def _updateNotesView(self):
        # Update the contents of notesview, in another thread

        # selected note name
        noteName = self._index[self._filePos]
        if noteName:
            path = self._index.getPath(noteName)
            n = noteloader.noteloader(path,self._view_i,scrollPos=self._noteScrollPos)
        else:
            self._notify(f"No note number {self._filePos}")
            n = noteloader.noteloader(None,self._view_i,scrollPos=None)

        self.noteloaderThreads.append(multiprocessing.Process(target=n.run))
        self.noteloaderThreads[-1].start()

    def _updateFileView(self):
        # check sanity of cursor position
        if self._filePos<0: self._filePos=0
        if self._filePos>=len(self._index)-1:
            self._filePos=len(self._index)-1


        # emplace filesview frame
        data = {}
        data["type"] = "filesview"
        data["pos"] = self._filePos
        data["names"] = [ n for n in self._index ]
        data["key"] = self._index.getSearchKey()
        data["filter"] = self._index.getPattern()
        data["sort"] = self._index.getSort()
        self._view_i.put(data)

    def processInputFilesview(self,char):
        data = {}

        if False: pass
        elif char==ord("j"): # scroll down
            self._filePos+=1
        elif char==ord("k"): # scroll up
            self._filePos-=1
        elif char==ord("u"): # jump up
            self._filePos-=10
        elif char==ord("d"): # jump down
            self._filePos+=10

        self._updateFileView()
        self._updateNotesView()

    def processInputNumbers(self,char):
        # Numbers for jumping to note
        buffer = chr(char)
        self._notify(buffer)
        while True:
            char = self._char_queue.get()
            if char == settings["enterChar"]:
                try:
                    log("\tJumping",buffer)
                    jump=int(buffer)
                    log("\tJumping",jump)
                    self._filePos = int(jump)
                    self._notify(f"Jumped to {jump}")
                    self._updateNotesView()
                    self._updateFileView()
                    return
                except:
                    self._notify(f"Invalid jump {buffer}")
            elif chr(char) in "0123456789":
                buffer+=chr(char)
                self._notify(buffer)
            else:
                self._notify("No jump")
                return
        self._notify("")

    def processInputNotesView(self,char):
        data = {}

        if False: pass
        elif char==ord("d"): # jump down
            self._noteScrollPos+=10
        elif char==ord("u"): # jump up
            self._noteScrollPos-=10
        elif char==ord("j"): # scroll down
            self._noteScrollPos+=1
        elif char==ord("k"): # scroll up
            self._noteScrollPos-=1
        self._noteScrollPos=max(0,self._noteScrollPos)


        # Don't just update full view, just update the scroll!
        self._updateNotesView()

    def startController(self):
        log("MODEL: Starting controller")
        self.controllerThread = multiprocessing.Process(target=self._controller.run)
        self.controllerThread.start()

    def stopController(self):
        log("MODEL: Stopping controller")
        self.controllerThread.terminate()

    def startView(self):
        log("MODEL: Starting view")
        self.viewThread = multiprocessing.Process(target=self._view.run)
        self.viewThread.start()

    def stopView(self):
        log("MODEL: Stopping view")
        self.viewThread.terminate()

    def run(self):

        # launch threads
        self.startController()
        self.startView()

        while True:
            # time.sleep(0.1) # fix this, bad for performance
            # log("Model loop")


            # transfer queues
            # while self._char_queue.qsize():

            self._event.wait()
            self._event.clear()

            while not self._char_queue.empty():

                char = self._char_queue.get()
                log(f"Processing char: {chr(char)}")

                if chr(char) in self._hotkeyMap.keys():
                    command = self._hotkeyMap[chr(char)]
                    self._commandMap[command](None)

                elif chr(char) in "0123456789":
                    self.processInputNumbers(char)

                elif self._focus=="filesview":
                    self.processInputFilesview(char)
                elif self._focus=="notesview":
                    self.processInputNotesView(char)
                # elif self._focus=="dialog":
                #     self.processInputDialogView(char)


            while not self._markdown_o.empty():
                update = self._markdown_o.get()
                self._notify(update["message"])

            # time.sleep(0.1)

            # # emplace commandview frame
            # if char==settings["deleteChar"]:
            #     self._commandBuffer=self._commandBuffer[:-1]
            # elif char==settings["ctrlUChar"]:
            #     self._commandBuffer=""
            # else:
            #     self._commandBuffer+=chr(char)
            #     # self._commandBuffer+=str(char)
            # f = {}
            # f["type"] = "commandview"
            # f["leader"] = self._commandLeader
            # f["content"] = self._commandBuffer
            # f["curser"] = 2
            # self._view_i.put(f)

            # # emplace notesView frame
            # f = {}
            # f["type"]     = "notesview"
            # f["name"]     = "Example note"
            # f["tags"]     = ["lhc","p1","nsw"]
            # f["created"]  = "08/03/23 11:31::36"
            # f["modified"] = "08/03/23 11:31::36"
            # f["noteText"] = [f"lorem {i} ipsum" for i in range(10*self._filePos)]
            # # f["noteText"] = ["lorem ipsum\n"]*(self._filePos+1)
            # f["scroll"]   = 5
            # self._view_i.put(f)

