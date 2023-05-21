from setup import *
import _curses

def _drawBox(window,y,x,h,l,char,color):
    """ Draw rectangle filled with shaded character """
    # for yPos in range(int(y),int(y+h)):
    for line in range(h):
        _hline(window,y+line,x,l,char,color=color)

def _drawBoxOutline(window,y,x,h,l,char,color):
    """ Draw rectangle """
    _hline(window,y,x,l,color=color)
    _hline(window,y+h,x,l,color=color)
    _vline(window,y,x,h,color=color)
    _vline(window,y,x+l,h,color=color)

    _point(window,y,x,curses.ACS_ULCORNER,color=color)
    _point(window,y,x+l,curses.ACS_URCORNER,color=color)
    _point(window,y+h,x,curses.ACS_LLCORNER,color=color)
    _point(window,y+h,x+l,curses.ACS_LRCORNER,color=color)

def _drawBoxLine(window,y,x,l,char,color):
    """ Draw Line across box """
    _hline(window,y,x,l,color=color)

    # left T
    _point(window,y,x,curses.ACS_ULCORNER+8,color=color)
    _point(window,y,x+l,curses.ACS_ULCORNER+9,color=color)


    # _point(window,y,x+l,curses.ACS_URCORNER,color=color)
    # _point(window,y+h,x,curses.ACS_LLCORNER,color=color)
    # _point(window,y+h,x+l,curses.ACS_LRCORNER,color=color)

def log(*text):
    f = open("log.txt","a")
    text = " ".join([str(t) for t in text])
    f.write(str(text)+"\n")
    f.close()

def _text(window,y,x,s,color=3,bold=False,reverse=False,underline=False):
    _move(window,int(y),int(x))
    label=str(s)

    color = curses.color_pair(color)

    # if bold: color |= curses.A_UNDERLINE
    if bold: color |= curses.A_BOLD
    if reverse: color |= curses.A_REVERSE
    if underline: color |= curses.A_UNDERLINE
    # log("-"*50)
    # log(window)
    # log(label)
    try:
        window.addstr(label,color)
    except: pass


def _point(window,y,x,c,color=0):
    _move(window,int(y),int(x))
    try:
        # window.addstr(str(c),curses.color_pair(color))
        window.addch(c,curses.color_pair(color))
    except _curses.error as e:
        # curses tries to wrap around corner
        pass
    except:
        log(f"ERROR: Failed while drawing _point: y{y},x{x},c{c},color{color}")
        raise Exception(f"ERROR: Failed while drawing _point: y{y},x{x},c{c},color{color}")
        quit()



def _vline(window,y,x,l,color=0):
    _move(window,int(y),int(x))
    try:
        window.vline(curses.ACS_VLINE,int(l),curses.color_pair(color))
    except:
        log("Failed while drawing _vline")

def _hline(window,y,x,l,char=None,color=0):
    if char==None: char = curses.ACS_HLINE
    _move(window,int(y),int(x))
    try:
        window.hline(char,int(l),curses.color_pair(color))
    except:
        log("Failed while drawing _hline")

def _move(window,y,x):
    try:
        window.move(int(y),int(x))
    except:
        raise BaseException("Failed moving x={0}, y={1}".format(x,y))

