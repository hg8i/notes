#!/bin/env python3
from interface import *

def main(screen):
    curses.start_color()
    curses.use_default_colors()

    indexPath = settings["indexPath"]

    if "-p" in sys.argv:
        index = noteindex(loadPickle=0,picklePath=indexPath)
    else:
        try:
            log("Loading index with pickle file")
            index = noteindex(loadPickle=1,picklePath=indexPath)
        except:
            log("Loading index without pickle file")
            index = noteindex(loadPickle=0,picklePath=indexPath)

    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)
    i = interface(screen,index)

if __name__=="__main__":
    wrapper(main)
