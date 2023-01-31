from setup import *
import textpad

def checkInput(k):
    # 32 is space
    # 27 is escape
    # 10 is enter
    # _print(k)
    if k == 27: return 10
    # if k == 32: return "_"
    return k

class commandView:
    def __init__(self,screen):
        self._screen = screen
        screenY,screenX = self._screen.getmaxyx()

        curses.init_pair(1, settings["fgColorCommandView"],settings["bkColorCommandView"])
        self._color=1

        self._text = textpad.Textbox(screen,screenX-3,color=self._color)
        self.update()
        # self.run()

        if os.path.exists(settings["commandHistoryPath"]):
            self._history = open(settings["commandHistoryPath"]).readlines()
            self._history = [i.rstrip() for i in self._history]
        else:
            self._history = []

    def ping(self):
        """ Fix display
        """
        self._screen.refresh()

    def run(self,init=None):
        """ Get input from command line, and return
        """
        curses.curs_set(1)

        # add initial string if given
        if init: self._text.set(init)

        text = self._text.edit(checkInput,history=list(self._history))
        self._text.reset()
        # self.update()
        curses.curs_set(0)
        self._text._move(0,0)
        self._screen.refresh()

        # remove initial string
        if init: text=text[len(init):]

        # save new commend into history
        if text and init==":":
            self._history.append(text)
            open(settings["commandHistoryPath"],"a").write(text+"\n")
        log("Command history:"+str(self._history))

        return text

    def setStatus(self,string):
        """ Set content of view with status string
        """
        self._text.set(string)
        self.ping()

    def update(self,screen=None):
        """ Update
        """
        if screen==None: screen=self._screen
        else: self._screen=screen
        self._screenY,self._screenX = self._screen.getmaxyx()
        utils._drawBox(self._screen,0,0,self._screenY,self._screenX," ",self._color)
        # self._screen.bkgd(' ', self._color)

