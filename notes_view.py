from setup import *


class notesView:
    def __init__(self,screen):
        self._screen = screen

        curses.init_pair(2, settings["fgColorNotesView"],settings["bkColorNotesView"])
        self._color=2

        # curses.init_pair(5, settings["fgColorNotesView"],settings["bkColorNotesView"])
        # self._color=5

        self._scrollPos = 0
        self._noteName = None

        self._headerHeight = 4


        self.update()

        # self._screen.bkgd(' ', settings["bkColorNotesView"] | curses.A_BOLD | curses.A_REVERSE)


    def _text(self,y,x,s,color=None,bold=False,reverse=False,underline=False):
        utils._move(self._screen,int(y),int(x))
        if color==None:
            color = self._color

        label=str(s)
        color = curses.color_pair(color)
        # if bold: color |= curses.A_UNDERLINE
        if bold: color |= curses.A_BOLD
        if reverse: color |= curses.A_REVERSE
        if underline: color |= curses.A_UNDERLINE

        self._screen.addstr(label,color)


    
    def load(self,noteName=None):
        """ Load given note name
        """
        xprint("Loading NV",noteName,"exists",os.path.exists(noteName))
        if noteName:
            self._noteDir  = os.path.join(settings["dataPath"],noteName)
            if os.path.exists(self._noteDir):
                self._notePath = os.path.join(self._noteDir,"note.md")
                self._filesPath = os.path.join(self._noteDir,"data")
                self._noteData = os.path.join(self._noteDir,"meta.pickle")
                self._metaData = pickle.load(open(self._noteData))
                self._noteName=noteName
                self._noteText = open(self._notePath,"r").readlines()
            else:
                self._noteName=None
                # quit()

        self._display()

    def ping(self):
        """ Redraw display
        """
        self.load(self._noteName)

    def curPath(self):
        """ Return current path of editable file
        """
        ret={}
        ret["files"] = self._filesPath
        ret["note"] = self._notePath
        ret["data"] = self._noteData
        return ret

    def _trimLine(self,line):
        """ Trim line to window size
        """
        trimmed=len(line)>self._screenX-3
        line = line[:self._screenX-3]
        # add trailing indicator of cut line
        if trimmed:
            line+=">"
        return line

    def _display(self):
        """ Update display
        """
        self.update()
        if self._noteName==None:
            line = "[No note to load]"
            self._text(1,1,self._trimLine(line))
            self._screen.refresh()
            return

        # Header text
        line = "Name: {}".format(self._metaData["displayName"])
        self._text(1,1,self._trimLine(line),bold=True)
        line = "Tags: {}".format(", ".join(self._metaData["tags"]))
        self._text(2,1,self._trimLine(line),bold=True)
        line = "Created: {}".format(self._metaData["displayCreated"])
        self._text(3,1,self._trimLine(line),bold=True)
        line = "Path: {}".format(self._metaData["dirPath"])
        self._text(4,1,self._trimLine(line),bold=True)

        # trim text based on screen height and scrolling
        trimmedText = list(self._noteText)
        trimmedText = trimmedText[self._scrollPos:]
        trimmedText = trimmedText[:self._noteTextY-2]
        for iLine,line in enumerate(trimmedText):
            trimmedLine = self._trimLine(line.replace("\n",""))
            # decide if header text in Markdown
            header = (trimmedLine!="" and trimmedLine[0]=="#")
            header |= (len(trimmedText)>iLine+1 and trimmedText[iLine+1] and trimmedText[iLine+1][0] in ["=","-"])
            self._text(iLine+self._headerHeight+2,1,trimmedLine,reverse=header)

        if len(trimmedText)<len(self._noteText):
            if self._scrollPos<len(self._noteText)-self._noteTextY+2:
                self._text(self._screenY-1,2,"...")
            else:
                self._text(self._screenY-1,2,"xxx")

        self._screen.refresh()


    def processCharacter(self,char):
        """ Process each character
        """
        # char = self._screen.getch()
        if False:
            quit()
        elif char==ord("G"): # bottom
            self._scrollPos=len(self._noteText)-self._noteTextY+2
            self._display()
        elif char==ord("g"): # top
            self._scrollPos=0
            self._display()
        elif char==ord("u"): # scroll down
            self._scrollPos-=10
            self._scrollPos = max(0,self._scrollPos)
            self._display()
        elif char==ord("d"): # scroll up
            self._scrollPos+=10
            self._scrollPos =  min(len(self._noteText)-self._noteTextY+2,self._scrollPos)
            self._display()
        elif char==ord("j"): # scroll down
            self._scrollPos+=1
            self._scrollPos = min(len(self._noteText)-self._noteTextY+2,self._scrollPos)
            self._display()
        elif char==ord("k"): # scroll up
            self._scrollPos-=1
            self._scrollPos = max(0,self._scrollPos)
            self._display()
        elif char==ord("\t"):
            return 0

        self._text(0,self._screenX-3,self._scrollPos)
        self._text(0,self._screenX-8,len(self._noteText)-1)
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


    def update(self,screen=None):
        """ Update
        """
        if screen==None: screen=self._screen
        else: self._screen=screen
        self._screenY,self._screenX = self._screen.getmaxyx()
        self._noteTextY = self._screenY-(self._headerHeight+1)
        utils._drawBox(self._screen,0,0,self._screenY,self._screenX," ",self._color)
        # self._screen.bkgd(' ', self._color )

        utils._drawBoxOutline(self._screen,0,0,self._screenY-1,self._screenX-1," ",self._color)
        utils._drawBoxLine(self._screen,self._headerHeight+1,0,self._screenX-1," ",self._color)


