import math, sys, time, copy
import curses
from curses import wrapper
import curses, sys, os, time
from datetime import date
# import curses.textpad as textpad
import textpad
import cPickle as pickle
# import editDialog
import functools
import utils,glob
from subprocess import call




settings = {}
settings["bkColorCommandView"] = utils.color_dark_yellow
settings["fgColorCommandView"] = utils.color_red

settings["bkColorNotesView"] = utils.color_dark_blue
settings["fgColorNotesView"] = utils.color_cyan

settings["bkColorFilesView"] = utils.color_dark_green
settings["fgColorFilesView"] = utils.color_white
settings["bkColorFilesViewHighlight"] = utils.color_white
settings["fgColorFilesViewHighlight"] = utils.color_dark_green

# dialog box
settings["dialogDialogFocus"] = utils.color_cyan
settings["dialogDialogBackground"] = utils.color_dark_red



settings["filesWidth"] = 30

settings["dataPath"] = "/home/prime/dev/notes/data"
settings["trashPath"] = "/home/prime/dev/notes/trash"
settings["indexPath"] = "/home/prime/dev/notes/index.pickle"

os.popen("rm -f log.txt")
def xprint(*string):
    string = [str(s) for s in string]
    string = " ".join(string)
    f = open("log.txt","a")
    f.write(string+"\n")
    f.close()
