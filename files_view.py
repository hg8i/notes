from setup import *
# from subprocess import call


class filesView:
    def __init__(self,screen,nv):
        self._screen = screen
        self._nv = nv
        screenY,screenX = self._screen.getmaxyx()

        curses.init_pair(3, settings["fgColorFilesView"],settings["bkColorFilesView"])
        self._color=3

        curses.init_pair(4, settings["fgColorFilesViewHighlight"],settings["bkColorFilesViewHighlight"])
        self._colorHighlight=4

        self._filterMode = "path"
        self._filterTags = None

        # file list info
        self._listOfFiles = []
        self._relpath = ""
        self._index =0

        self.ping()

    def ping(self):
        """ Ping and update file list
        """
        self._updateListOfFiles()
        self._display()

        # self.update()

    def _text(self,y,x,s,color=None):
        utils._move(self._screen,int(y),int(x))
        if color==None:
            color = self._color
        try:
            label=str(s)
            self._screen.addstr(label,curses.color_pair(color))
        except:
            label=repr(s)
            self._screen.addstr(label,curses.color_pair(color))

    def _prepName(self,path):
        """ Return dictionary with convienant name info
        """
        ret = {}
        ret["path"] = path
        ret["name"] = os.path.basename(path)
        ret["sname"] = ret["name"][7:].split(".")[0]
        ret["date"] = ret["name"][:6]
        # display name from pickle path
        noteData = pickle.load(open(os.path.join(path,"meta.pickle")))
        ret["displayName"] = noteData["displayName"]


        # reversed date int for sorting
        ret["rdate"] = int(ret["name"][4:6]+ret["name"][2:4]+ret["name"][0:2])
        return ret

    def _updateListOfFiles(self):
        """ Update list of files,
            Either relevant path
            Or via some pattern
        """
        if self._filterMode=="path":
            path = os.path.join(settings["dataPath"],self._relpath)
            allDirs = os.listdir(path)
            allDirs = [os.path.join(path,p) for p in allDirs]
            # allNames = [os.path.basename(i) for i in allDirs]
            self._listOfFiles = [self._prepName(n) for n in allDirs]
            # reverse sort by date in file name
            self._listOfFiles = sorted(self._listOfFiles, key=lambda x:x["rdate"],reverse=1)
        elif self._filterMode=="tags":
            # use index file to only add lists via tags
            index = pickle.load(open(settings["indexPath"]))
            noteNamesByTag = [ set(index[tag]) for tag in self._filterTags if tag in index.keys()]
            if noteNamesByTag:
                namesWithEachTag = functools.reduce(lambda a,b: a&b, noteNamesByTag)
            else:namesWithEachTag=[]
            # reverse sort by date in file name
            path = os.path.join(settings["dataPath"],self._relpath)
            paths = [os.path.join(path,i) for i in namesWithEachTag]
            self._listOfFiles = [self._prepName(n) for n in paths]
            self._listOfFiles = sorted(self._listOfFiles, key=lambda x:x["rdate"],reverse=1)


        self._index = 0

    def setMode(self,mode,tags=None):
        """ Set mode for updating list of files
        """ 
        self._filterMode=mode
        if mode=="tags":
            self._filterTags = tags

    def _display(self):
        """ Update display with list of files
        """
        self.update()

        if len(self._listOfFiles)==0:
            self._text(1,1,"[No Notes in Selection]")

        for iEntry,entry in enumerate(self._listOfFiles):
            line = "{}: {}".format(iEntry,entry["displayName"])
            line = line[:self._screenX-1]
            if iEntry==self._index:
                self._text(iEntry+1,1,line,color=self._colorHighlight)
            else:
                self._text(iEntry+1,1,line)

        self._screen.refresh()

    def _curName(self):
        """ Return currently selected name
        """
        if not self._listOfFiles: return None
        return self._listOfFiles[self._index]["name"]

    def goTo(self,target):
        """ Go to entry in index
            If invalid, skip
        """
        if target<0: return
        if target>=len(self._listOfFiles): return
        self._index = target
        self._display()
        self._nv.load(self._curName())

    def processCharacter(self,char):
        """ Process each character
        """
        if False:
            quit()

        elif char==ord("n"): # scroll down
            self._index+=1
            if self._index>=len(self._listOfFiles):
                self._index=0
            self._display()
            self._nv.load(self._curName())
        elif char==ord("N"): # scroll up
            self._index-=1
            if self._index<0:
                self._index=len(self._listOfFiles)-1
            self._index = max(0,self._index)
            self._display()
            self._nv.load(self._curName())

        # elif char==ord("j"): # scroll down
        #     self._index+=1
        #     if self._index>=len(self._listOfFiles):
        #         self._index=0
        #     self._display()
        # elif char==ord("k"): # scroll up
        #     self._index-=1
        #     if self._index<0:
        #         self._index=len(self._listOfFiles)-1
        #     self._index = max(0,self._index)
        #     self._display()
        # elif char==ord("\t"):
        #     return 0
        # elif char==10: # enter key
        #     # ping the Note View to update to this
        #     self._nv.load(self._curName())

        self._text(0,self._screenX-3,self._index)
        self._screen.refresh()
        return 1

    def select(self,val):
        """ Indicate this view is selected
        """
        if val:
            self._text(0,1,"x")
            self._screen.refresh()
        else:
            self._display()
            self._screen.refresh()


    def update(self,screen=None):
        """ Update
        """
        if screen==None: screen=self._screen
        else: self._screen=screen
        self._screenY,self._screenX = self._screen.getmaxyx()
        utils._drawBox(self._screen,0,0,self._screenY,self._screenX," ",self._color)
        # self._screen.bkgd(' ', color )
        # self._screen.bkgd(' ', color | curses.A_BOLD | curses.A_REVERSE)
        utils._drawBoxOutline(self._screen,0,0,self._screenY-1,self._screenX-1," ",self._color)

