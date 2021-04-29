"""Based on from /usr/lib/python2.7/curses/textpad.py"""
"""But with scrolling"""

import curses
import curses.ascii

def _print(*string):
    string = [str(s) for s in string]
    string = " ".join(string)
    f = open("log.txt","a")
    f.write(string+"\n")
    f.close()



class Textbox:

    def __init__(self, window,ncols, insert_mode=False,color=8,commandMode=True):
        pass
        self._commandMode=commandMode
        self._window=window
        self._buffer=[]
        self._cur = 0
        self._scrollPos = 0
        self._y, self._x = window.getyx()
        self._ncols = ncols-2
        self._window.keypad(1) # needed for arrow keys!

        self._textColor = curses.color_pair(color)

    def _move(self,y,x):
        try:
            self._window.move(int(y),int(x))
        except:
            raise BaseException("Failed moving x={0}, y={1}".format(x,y))


    # def edit(self):
    #     # (y, x) = self.window.getyx()
    #     self._move(0,1)
    #     self._window.addch("x")
    #     self._window.refresh()
    #     raw_input()
    #     pass

    def set(self,text):
        """ Set buffer to text
        """
        self._buffer=[ord(i) for i in text]
        self._cur=len(self._buffer)
        self._doScrolling()
        self._update()

    def edit(self, validate=None):
        "Edit in the widget window and collect the results."
        while 1:
            ch = self._window.getch()
            if validate:
                ch = validate(ch)
            if not ch:
                continue
            if not self.do_command(ch):
                break
            self._window.refresh()
        return self.gather()

    def gather(self):
        text = "".join([chr(c) for c in self._buffer])
        return text

    def _update(self):
        """ Update text and cursor position
        """
        # get text to draw
        lo = self._scrollPos
        hi = lo+self._ncols+1
        text = "".join([chr(c) for c in self._buffer])
        text = text[lo:hi]
        while len(text)<self._ncols+1: text+=" "
        self._move(0,0)
        self._window.addstr(text,self._textColor)

        # place cursor
        self._move(0,self._cur-self._scrollPos)

    def _doScrolling(self):
        """ Adjust scroll of text
        """
        # adjust if cursor longer than buffer
        self._cur=min(self._cur,len(self._buffer))
        self._cur=max(self._cur,0)

        # scroll until cursor not out of bounds
        while self._cur-self._scrollPos>self._ncols+1:
            self._scrollPos+=1
        # scroll until cursor not out of bounds
        while self._cur-self._scrollPos<0:
            self._scrollPos-=1



    def do_command(self,c):
        if c==10 or c==27: 
            return 0

        # return when empty
        if self._commandMode and len(self._buffer)==0:
            return 0

        if c==curses.KEY_LEFT:
            self._cur-=1
        elif c==curses.KEY_RIGHT:
            self._cur+=1
        elif c == (curses.ascii.ENQ):
            # jump to end ctrl E
            self._cur=len(self._buffer)
        elif c == (curses.ascii.SOH):
            # jump to start ctrl A
            self._cur=0
        elif c == (curses.ascii.NAK):
            # delete to beginning ctrl U
                self._buffer=self._buffer[self._cur:]
                self._cur=0
        elif c in (curses.ascii.BS, curses.KEY_BACKSPACE):
            # delete character
            if len(self._buffer) and self._cur>0:
                self._buffer.pop(self._cur-1)
                self._cur-=1
            pass
        else:
            try: chr(c)
            except: return 1
            self._buffer.insert(self._cur,c)
            self._cur+=1


        self._doScrolling()
        self._update()
        self._window.refresh()
        return 1

    def reset(self):
        """ Reset the text box for next entry
        """
        self._buffer=[]
        self._update()

if __name__ == '__main__':
    def test_editbox(stdscr):
        ncols, nlines = 12, 1
        uly, ulx = 15, 20
        # stdscr.addstr(uly-2, ulx, "Use Ctrl-G to end editing.")
        win = curses.newwin(nlines, ncols, uly, ulx)
        def rectangle(win, uly, ulx, lry, lrx):
            """Draw a rectangle with corners at the provided upper-left
            and lower-right coordinates.
            """
            win.vline(uly+1, ulx, curses.ACS_VLINE, lry - uly - 1)
            win.hline(uly, ulx+1, curses.ACS_HLINE, lrx - ulx - 1)
            win.hline(lry, ulx+1, curses.ACS_HLINE, lrx - ulx - 1)
            win.vline(uly+1, lrx, curses.ACS_VLINE, lry - uly - 1)
            win.addch(uly, ulx, curses.ACS_ULCORNER)
            win.addch(uly, lrx, curses.ACS_URCORNER)
            win.addch(lry, lrx, curses.ACS_LRCORNER)
            win.addch(lry, ulx, curses.ACS_LLCORNER)
        rectangle(stdscr, uly-1, ulx-1, uly + nlines, ulx + ncols)
        stdscr.refresh()
        # stdscr.keypad(1)
        # win.keypad(1)
        return Textbox(win,ncols).edit()


    str = curses.wrapper(test_editbox)
    print 'Contents of text box:', repr(str)
