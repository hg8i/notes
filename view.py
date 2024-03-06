from setup import *
import drawing

class view:
    def __init__(self,screen,inputq=None,outputq=None):
        self._screen = screen
        self._input = inputq
        self._output = outputq
        self._lastScreenY,self._lastScreenX = None,None

        self._commandColor = 1
        curses.init_pair(self._commandColor, settings["fgColorCommandView"],settings["bkColorCommandView"])

        self._notesColor = 2
        curses.init_pair(self._notesColor, settings["fgColorNotesView"],settings["bkColorNotesView"])

        self._filesColor = 3
        curses.init_pair(self._filesColor, settings["fgColorFilesView"],settings["bkColorFilesView"])

        self._filesHighlight = 5
        curses.init_pair(self._filesHighlight, settings["fgColorFilesViewHighlight"],settings["bkColorFilesViewHighlight"])

        self._dialogColor = 6
        curses.init_pair(self._dialogColor, settings["fgColorDialog"],settings["bkColorDialog"])

        self._dialogHighlightColor = 7
        curses.init_pair(self._dialogHighlightColor, settings["fgColorDialogHighlight"],settings["bkColorDialogHighlight"])

        self._commandState = None
        self._notesState = None
        self._dialogState = None
        self._filesState = None
        self._dialogActive = False
        self._pause = False

        self._headerHeight = 4 # height of notes header

        self._filesScroll = 0

        # Make screens
        self.rescaleCheck()
        # self.rescaleCheck(force=True)



    def _makeScreens(self):
        log("VIEW: making screens")
        self._screen.clear()
        screenY,screenX = self._screen.getmaxyx()
        # subwin(nlines, ncols, begin_y, begin_x)
        # self._testScreen = self._screen.subwin(screenY,screenX,0,0)
        self._commandScreen = self._screen.subwin(1,screenX-0,screenY-1,0)
        # self._commandScreen = self._screen.subwin(2,screenX-0,screenY-3,1)
        # files view
        fsWidth = settings["filesWidth"]
        # self._filesScreen = self._screen.subwin(1,screenX-0,screenY-3,0)
        self._filesScreen = self._screen.subwin(screenY-1,fsWidth,0,0)
        # notes view
        nvWidth = screenX-fsWidth
        self._notesScreen = self._screen.subwin(screenY-1,nvWidth,0,fsWidth)

        self._lastScreenY,self._lastScreenX = screenY,screenX

        # self._commandScreen.clear()
        # self._notesScreen.clear()
        # self._filesScreen.clear()

        if self._dialogActive: self._makeDialogScreen()

        self._commandScreen.refresh()
        self._notesScreen.refresh()
        self._filesScreen.refresh()


    def _makeDialogScreen(self):
        screenY,screenX = self._screen.getmaxyx()
        h = min(self._dialogH,screenY-4)
        w = min(self._dialogW,screenX-4)
        log("Creating dialog screen:",h,w,int(screenY/2)-h,int(screenX/2)-w)
        self._dialogScreen = self._screen.subwin(h,w,int((screenY-h)/2),int((screenX-w)/2))
        self._dialogScreen.refresh()

    def updateDialogScreen(self):
        """ Update command view
        """
        log("VIEW: updateDialogScreen")
        update = self._dialogState
        if update==None: return
        log("Updating dialog screen",update)

        if update["instruction"] == "closedialog":
            self._dialogActive = False
            self._dialogScreen.clear()
            self.updateNotesScreen()
            self.updateFilesScreen()
            return

        log("Processing dialog instructions")
        if "updatevalue" in update["instruction"]:
            if update["instruction"].split("-")[1]=="activeField":
                # update the current active field
                self._dialogActiveField = update["value"]
            if update["instruction"].split("-")[1]=="fieldData":
                # update the value of a particular field
                # TODO: clean up
                name = update["field"]["name"]
                content = update["field"]["content"]
                showCursor = update["field"]["showCursor"]
                log(update["field"])
                activeField = update["activeField"]
                cursorPos = update["field"]["cursorPos"]
                self._dialogFields[activeField]["content"] = content
                self._dialogFields[activeField]["cursorPos"] = cursorPos
                self._dialogFields[activeField]["showCursor"] = showCursor

        if update["instruction"] == "newdialog":
            # self._dialogActive = True
            self._dialogInputMode = update["inputs"]
            self._dialogFields = update["fields"]
            self._dialogActiveField = update["activeField"]
            self._dialogLongestName = max([len(n["name"]) for n in self._dialogFields])
            self._dialogName = update["name"]
            self._dialogW = 80
            self._dialogH = 2+len(self._dialogFields)*[1,3][self._dialogInputMode]
            self._makeDialogScreen()

        # self._dialogState = None

        log("Drawing dialog boxes")
        screenY,screenX = self._dialogScreen.getmaxyx()
        drawing._drawBox(self._dialogScreen,0,0,screenY,screenX," ",self._dialogColor)
        drawing._drawBoxOutline(self._dialogScreen,0,0,screenY-1,screenX-1," ",self._dialogColor)
        if self._dialogName:
            fancyDialogName = f" :{self._dialogName}: "
            self._text(self._dialogScreen,0,int((self._dialogW-len(fancyDialogName))/2),fancyDialogName,color=self._dialogColor)

        fieldHeight=3 if self._dialogInputMode else 1
        if self._dialogInputMode:
            nameLength = self._dialogLongestName+6
        else:
            nameLength = self._dialogLongestName+10+6
        contentLength = self._dialogW-nameLength-2

        # draw dialog
        for iField,field in enumerate(self._dialogFields):
            log("Writing field",field)
            yPos = fieldHeight*iField+1+self._dialogInputMode
            if "content" in field.keys():
                name = " "+field["name"]+":"
                content = field["content"]
                cursorPos = field["cursorPos"]
                showCursor = "showCursor" in field.keys() and field["showCursor"]
                content = str(content)[:self._dialogW-nameLength]
                self._text(self._dialogScreen,yPos,1,name,color=self._dialogColor)
                self._text(self._dialogScreen,yPos,nameLength,content,color=self._dialogColor)
                if showCursor:
                    self._text(self._dialogScreen,yPos,nameLength+cursorPos,"_",color=self._dialogHighlightColor)
                    # self._text(self._dialogScreen,yPos,nameLength+cursorPos,content[cursorPos],color=self._dialogHighlightColor)
                if self._dialogInputMode:
                    if iField==self._dialogActiveField:
                        drawing._drawBoxOutline(self._dialogScreen,yPos-1,nameLength-1,2,contentLength," ",self._dialogHighlightColor)
                    else:
                        drawing._drawBoxOutline(self._dialogScreen,yPos-1,nameLength-1,2,contentLength," ",self._dialogColor)
            elif "divider" in field.keys():
                name = field["name"]+" "
                divider = field["divider"]*(self._dialogW-2-len(name))
                line = f"{name}{divider}"[:self._dialogW-2]
                self._text(self._dialogScreen,yPos,1,line,color=self._dialogColor)



        # self.updateNotesData()
        self._dialogScreen.refresh()

    def updateNotesScreen(self):
        """ Update command view
        """
        log("VIEW: updateNotesScreen")
        self._notesScreen.erase()
        screenY,screenX = self._notesScreen.getmaxyx()
        drawing._drawBox(self._notesScreen,0,0,screenY,screenX," ",self._notesColor)
        drawing._drawBoxOutline(self._notesScreen,0,0,screenY-1,screenX-1," ",self._notesColor)
        drawing._drawBoxLine(self._notesScreen,self._headerHeight+1,0,screenX-1," ",self._notesColor)
        self.updateNotesData()
        self._notesScreen.refresh()

    def updateCommandScreen(self):
        """ Update command view
        """
        log("VIEW: updateCommandScreen")
        self._commandScreen.erase()
        screenY,screenX = self._commandScreen.getmaxyx()
        drawing._drawBox(self._commandScreen,0,0,screenY,screenX," ",self._commandColor)
        self.updateCommandData()
        self._commandScreen.refresh()

    def updateFilesScreen(self):
        """ Update command view
        """
        log("VIEW: updateFilesScreen")
        self._filesScreen.erase()
        screenY,screenX = self._filesScreen.getmaxyx()
        drawing._drawBox(self._filesScreen,0,0,screenY,screenX," ",self._filesColor)
        drawing._drawBoxOutline(self._filesScreen,0,0,screenY-1,screenX-1," ",self._filesColor)
        drawing._drawBoxLine(self._filesScreen,self._headerHeight+1,0,screenX-1," ",self._filesColor)
        self.updateFilesData()
        self._filesScreen.refresh()

    def rescaleCheck(self,force=False):
        """ Rescale """
        log(f"VIEW: ---------------------------------------")
        log(f"VIEW: rescale (forced={force})")
        screenY,screenX = self._screen.getmaxyx()
        if self._lastScreenY!=screenY or self._lastScreenX!=screenX or force:
            self._makeScreens()
            self.updateCommandScreen()

            self.updateNotesScreen()
            # self.updateNotesData()

            self.updateFilesScreen()
            self.updateFilesData()

            self.updateDialogScreen()


    def updateCommandData(self):
        update = self._commandState
        if update==None: return
        if update["instruction"] == "textentry":
            leaderLen = len(update["leader"])
            # Could put an overflow check here for long commands (currently crashes)
            self._text(self._commandScreen,0,0,update["leader"],color=self._commandColor)
            self._text(self._commandScreen,0,leaderLen,update["content"],color=self._commandColor)
        elif update["instruction"] == "notify":
            text = update["content"][:self._lastScreenX-1]
            self._text(self._commandScreen,0,0,text,color=self._commandColor)
        elif update["instruction"] == "clear":
            pass

        # trim text to fit

    def updateFilesData(self):
        log("VIEW: updateFilesData")
        update = self._filesState
        screenY,screenX = self._filesScreen.getmaxyx()
        if update==None: return
        if update["filter"]==None:
            update["filter"]="None"
        pos = update["pos"]

        # Header lines
        self._text(self._filesScreen,1,1,f"Filter: {update['filter']}",color=self._filesColor)
        self._text(self._filesScreen,2,1,f"Sort:   {update['sort']}",color=self._filesColor)
        self._text(self._filesScreen,3,1,f"Key:    {update['key']}",color=self._filesColor)

        maxLines = screenY-self._headerHeight-3

        # Adjust scrolling
        self._filesScroll = max(self._filesScroll,pos-maxLines+1)
        self._filesScroll = min(self._filesScroll,pos)
        self._filesScroll = max(self._filesScroll,0)

        scroll = self._filesScroll

        # To debug scrolling
        self._text(self._filesScreen,4,1,f"Scroll/pos: {scroll}/{pos}",color=self._filesColor)

        lines = update["names"][scroll:scroll+maxLines]
        for iLine,line in enumerate(lines):
            yLoc = self._headerHeight+2+iLine
            text = f"{iLine+scroll}: {line}"
            text = text.replace("_"," ")
            # truncation
            if len(text)>screenX-2:
                text = text[:screenX-3]+settings["overflowSymbol"]
            # text = str(pos)
            if iLine+scroll==pos:
                self._text(self._filesScreen,yLoc,1,text,color=self._filesHighlight)
            else:
                self._text(self._filesScreen,yLoc,1,text,color=self._filesColor)

            # if iLine>maxLines: break


    def updateNotesData(self):
        update = self._notesState
        screenY,screenX = self._filesScreen.getmaxyx()
        if update==None: return

        screenY,screenX = self._notesScreen.getmaxyx()
        self._text(self._notesScreen,1,1,f"Name:     {update['name']}",color=self._notesColor)
        self._text(self._notesScreen,2,1,f'Tags:     {", ".join(update["tags"])}',color=self._notesColor)
        self._text(self._notesScreen,3,1,f"Created:  {update['created']}",color=self._notesColor)
        self._text(self._notesScreen,4,1,f"Modified: {update['modified']}",color=self._notesColor)
        # temporary
        self._text(self._notesScreen,5,screenX-13,f"Scroll: {update['scroll']}",color=self._notesColor)

        lo = update["scroll"]
        hi = lo+screenY-3-self._headerHeight
        for iLine,line in enumerate(update["noteText"][lo:hi]):
            pos = self._headerHeight+2+iLine
            text = line.strip()
            overflow = len(text)>screenX-2
            if overflow:
                text = text[:screenX-3]
            self._text(self._notesScreen,pos,1,text,color=self._notesColor)
            if overflow:
                self._text(self._notesScreen,pos,screenX-2,settings["overflowSymbol"],color=self._notesColor)

    def pause(self):
        """ Pause view output """
        log("VIEW: pausing")
        self._output.put({"type":"confirm_pause"})
        log("VIEW: pause confirmed")
        while self._input.get()["type"]!="resume":
            log("VIEW: pause waiting")
            time.sleep(0.05)
        log("VIEW: resume")
        self._output.put({"type":"confirm_resume"})

    def run(self):

        while True:
            log("VIEW: run loop")
            update = self._input.get()

            if update["type"]=="quit":
                return

            if update["type"]=="pause": # pause writing until resume
                self.pause()
                time.sleep(0.05) # not sure why needed, otherwise doesn't work
                self.rescaleCheck(force=True)

            if update["type"]=="forceUpdate":
                self.rescaleCheck(force=True)

            if update["type"]=="commandview":
                self._commandState = update
                self.updateCommandScreen() # check if required?

            if update["type"]=="filesview":
                self._filesState = update
                self.updateFilesScreen() # check if required?

            if update["type"]=="notesview":
                self._notesState = update
                self.updateNotesScreen() # check if required?

            if update["type"]=="dialogview":
                self._dialogState = update
                self.updateDialogScreen() # check if required?

            # always update possible dialog screen after
            self.updateDialogScreen() # check if required?
            self.rescaleCheck()

            curses.curs_set(0)


    def _text(self,window,y,x,s,color=3,bold=False,reverse=False,underline=False,sema=None):
        self._move(window,int(y),int(x))
        label=str(s)

        color = curses.color_pair(color)

        # if bold: color |= curses.A_UNDERLINE
        if bold: color |= curses.A_BOLD
        if reverse: color |= curses.A_REVERSE
        if underline: color |= curses.A_UNDERLINE

        window.addstr(label,color)

    def _move(self,window,y,x):
        try:
            window.move(int(y),int(x))
        except:
            raise BaseException("Failed moving x={0}, y={1}".format(x,y))
            quit()

