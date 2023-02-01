from setup import *
# from subprocess import call


class filesView:
    def __init__(self,screen,noteview,index):
        self._screen = screen
        self._index = index
        self._nv = noteview
        screenY,screenX = self._screen.getmaxyx()

        curses.init_pair(3, settings["fgColorFilesView"],settings["bkColorFilesView"])
        self._color=3

        curses.init_pair(4, settings["fgColorFilesViewHighlight"],settings["bkColorFilesViewHighlight"])
        self._colorHighlight=4

        self._filterMode = "path"
        self._filterTags = None

        self._scroll = 0

        # file list info
        self._relpath = ""
        self._fileIndex =0
        self._nv.load(0)

        self._screenY,self._screenX = self._screen.getmaxyx()
        self._nPerScroll = self._screenY-4


        self.ping()

    def ping(self):
        """ Ping and update file list
        """
        # TODO: Update so that it only loads a note when the index changes
        # self._fileIndex=min(self._fileIndex,len(self._index)-1)
        self._display()
        self._nv.load(self._fileIndex)

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

    def setMode(self,mode,tags=None):
        """ Set mode for updating list of files
        """ 
        self._filterMode=mode
        if mode=="tags":
            self._filterTags = tags

    def refreshIndex(self):
        self._fileIndex = 0
        self.ping()

    def getCurrentFileName(self):
        if not len(self._index): return None
        return self._index[self._fileIndex]

    def _display(self):
        """ Update display with list of files
        """

        self.update()

        if len(self._index)==0:
            self._text(1,1,"[No Notes in Selection]")

        scroll = self._scroll
        lo = scroll
        hi = scroll+self._nPerScroll
        for iName,shortname in enumerate(self._index[lo:hi]):
            if iName>self._screenY-3: 
                self._text(self._screenY-1,self._screenX-4,"...")
                break

            name = self._index.fullName(shortname)
            line = "{}: {}".format(int(lo+iName),name)
            line = line[:self._screenX-1]

            if iName+lo==self._fileIndex:
                self._text(iName+1,1,line,color=self._colorHighlight)
            else:
                self._text(iName+1,1,line)


        # draw index counter at top of screen
        self._text(0,self._screenX-3,self._fileIndex)

        self._text(0,self._screenX-9,self._scroll)

        # draw search pattern at top of the screen
        cleanSearchPattern = self._index.getPattern()
        if cleanSearchPattern:
            self._text(0,1,cleanSearchPattern)

            # draw search key at top of the screen
            cleanSearchKey = " | "+self._index.getSearchKey()
            self._text(0,len(cleanSearchPattern)+1,cleanSearchKey)

        # draw sorting mechanism
        cleanSort = f"Sort: {self._index.getSort()}"
        self._text(self._screenY-1,1,cleanSort)

        self._screen.refresh()

    def selectName(self,name):
        """ Select this name """
        if not name: return
        self.ping()
        self.goto(self._index.getIndexOf(name))

    def goto(self,number):
        self._fileIndex=min(number,len(self._index)-1)
        self._fileIndex = max(0,self._fileIndex)
        self._scrollToFileIndex()


    def test(self,char):
        log("test")
        # log("test",char)
        # log("LOG:",0,self._screenX-3,self._fileIndex)
        # quit()
        # return

    def goNext(self):
        self._fileIndex+=1
        if self._fileIndex>=len(self._index):
            self._fileIndex=0
        self._protectIndexBounds()
        self._scrollToFileIndex()

    def goPrev(self):
        self._fileIndex-=1
        if self._fileIndex<0:
            self._fileIndex=len(self._index)-1
        self._protectIndexBounds()
        self._scrollToFileIndex()

    def _scrollToFileIndex(self):
        while self._fileIndex<self._scroll:
            self._scroll-=1
        while self._fileIndex>self._scroll+self._nPerScroll-1:
            self._scroll+=1

    def _protectIndexBounds(self):
        self._fileIndex = max(0,self._fileIndex)
        if len(self._index):
            self._fileIndex=min(self._fileIndex,len(self._index)-1)

    def scrollDn(self):
        self._scroll+=10
        self._scroll = min(len(self._index),self._scroll)
        if self._fileIndex<self._scroll:
            self._fileIndex=self._scroll

    def scrollUp(self):
        self._scroll-=10
        self._scroll = max(0,self._scroll)
        if self._fileIndex>self._scroll+self._nPerScroll-1:
            self._fileIndex=self._scroll+self._nPerScroll-1

    def processCharacter(self,char):
        """ Process each character
        """

        if char==ord("q"):
            quit()
        elif char==ord("j"): # scroll down
            self.goNext()
        elif char==ord("k"): # scroll up
            self.goPrev()
        elif char==ord("d"): # scroll down
            self.scrollDn()
        elif char==ord("u"): # scroll up
            self.scrollUp()


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

        self.ping()

        return 1

    # def select(self,val):
    #     """ Indicate this view is selected
    #     """
    #     if val:
    #         self._text(0,1,"x")
    #         self._screen.refresh()
    #     else:
    #         self._display()
    #         self._screen.refresh()


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

        self._nPerScroll = self._screenY-4
