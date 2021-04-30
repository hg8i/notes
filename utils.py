import curses, sys, os, time
import cPickle as pickle


def _print(*string):
    string = [str(s) for s in string]
    string = " ".join(string)
    f = open("log.txt","a")
    f.write(string+"\n")
    f.close()

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

def _point(window,y,x,c,color=0):
    _move(window,int(y),int(x))
    try:
        window.addch(c,curses.color_pair(color))
    except:
        _print("Failed while drawing")

def _vline(window,y,x,l,color=0):
    _move(window,int(y),int(x))
    try:
        window.vline(curses.ACS_VLINE,int(l),curses.color_pair(color))
    except:
        _print("Failed while drawing")

def _hline(window,y,x,l,char=None,color=0):
    if char==None: char = curses.ACS_HLINE
    _move(window,int(y),int(x))
    try:
        window.hline(char,int(l),curses.color_pair(color))
    except:
        _print("Failed while drawing")

def _move(window,y,x):
    try:
        window.move(int(y),int(x))
    except:
        raise BaseException("Failed moving x={0}, y={1}".format(x,y))

def _text(window,y,x,s,color=20):
    _move(window,int(y),int(x))
    try:
        label=str(s)
        window.addstr(label,curses.color_pair(color))
    except:
        label=repr(s)
        window.addstr(label,curses.color_pair(color))


def getData(path):
    """ Safe way to get data files
    """
    data = pickle.load(open(path))
    if "tags" not in data.keys():
        data["tags"] = []
    if "uniqueFileCounter" not in data.keys():
        data["uniqueFileCounter"] = 0
    return data

def writeData(path,data):
    """ Safe way to dump data files
    """
    data = pickle.dump(data,open(path,"w"))

def uniquifyPath(path):
    c = 0
    if not os.path.exists(path): return None,path
    basename = os.path.basename(path)
    dirname = os.path.dirname(path)
    f = lambda x: "{}/{}-{}".format(dirname,x,basename)
    while os.path.exists(f(c)):
        c+=1
    return c,f(c)

color_green=40
color_red=197
color_white=231
color_purple=201
color_yellow=220
color_black=0

color_cyan=123
color_dark_cyan=39

color_blue=45
color_dark_blue=25

color_dark_green=28
color_dark_red=88
color_dark_yellow=178

color_dark_grey= 235
color_mid_grey= 244
color_light_grey= 252
