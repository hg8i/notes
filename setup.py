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
settings["bkColorCommandView"]         = utils.color_dark_blue
settings["fgColorCommandView"]         = utils.color_white

settings["bkColorNotesView"]           = utils.color_dark_blue
settings["fgColorNotesView"]           = utils.color_white

settings["bkColorFilesView"]           = utils.color_dark_cyan
settings["fgColorFilesView"]           = utils.color_white
settings["bkColorFilesViewHighlight"]  = utils.color_white
settings["fgColorFilesViewHighlight"]  = utils.color_dark_cyan

# dialog box
settings["dialogDialogFocus"]          = utils.color_blue
settings["dialogDialogBackground"]     = utils.color_white



settings["filesWidth"] = 30
settings["timeout"] = 2 # time before number reset

settings["dataPath"] = "/home/prime/sshfs/lxp/notes/data"
# settings["dataPath"] = "/home/prime/dev/notes/data"
settings["trashPath"] = "/home/prime/dev/notes/trash"
settings["indexPath"] = "/home/prime/dev/notes/index.pickle"
settings["commandHistoryPath"] = "/home/prime/dev/notes/history.txt"

os.popen("rm -f log.txt")
def xprint(*string):
    string = [str(s) for s in string]
    string = " ".join(string)
    f = open("log.txt","a")
    f.write(string+"\n")
    f.close()
