#!/bin/env python3
from interface import *

def main(screen):
    curses.start_color()
    curses.use_default_colors()

    try:
        index = noteindex(loadPickle=1)
    except:
        index = noteindex(loadPickle=0)

    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)
    i = interface(screen,index)

if __name__=="__main__":
    wrapper(main)
