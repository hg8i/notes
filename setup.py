import math, sys, time, copy
import curses
from curses import wrapper
import curses, sys, os, time, string
# from datetime import date
from datetime import datetime
import functools
import glob,utils
from subprocess import call
import multiprocessing

import glob,json,os,re
import pickle
from collections import defaultdict

os.popen("rm log.txt"); time.sleep(0.01)
def log(*text):
    global logon
    if not logon: return
    f = open("log.txt","a")
    text = " ".join([str(t) for t in text])
    f.write(str(text)+"\n")
    f.close()

debug = 1

thispath = os.path.dirname(os.path.abspath(__file__))

if debug:
    remotepath = thispath #debug
    logon = True
else:
    remotepath = "/home/prime/sshfs/lxp/notes"
    logon = False

settings = {}

settings["filesWidth"] = 30


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

settings["commandHistoryPath"] = os.path.join(thispath,"history.txt")
settings["indexPath"] = os.path.join(remotepath,"storedIndex.pickle")
settings["dataPath"] = os.path.join(remotepath,"data")
settings["tmpPath"] = "/tmp/notetmp"
settings["delPath"] = "/tmp/notetrash"

shortcutMap = defaultdict(lambda:None)
shortcutMap["p"] = "pickle"
shortcutMap["k"] = "key"
shortcutMap["n"] = "new"
shortcutMap["d"] = "delete"
shortcutMap["c"] = "change"
shortcutMap["e"] = "edit"
shortcutMap["s"] = "sort"
shortcutMap["q"] = "quit"
shortcutMap["h"] = "help"
settings["shortcutMap"] = shortcutMap

hotkeyMap = defaultdict(lambda:None)
hotkeyMap["/"] = "search"
hotkeyMap["\t"] = "cfocus"
hotkeyMap["c"] = "change"
hotkeyMap["e"] = "edit"
hotkeyMap["q"] = "quit"
hotkeyMap["h"] = "help"
hotkeyMap[":"] = "command"
settings["hotkeyMap"] = hotkeyMap

helpMessage = defaultdict(lambda:None)
helpMessage["key"]    = "[arg] set search key (tag,name,modified,all)"
helpMessage["sort"]   = "[arg] sort note list (name,modified,created,tag)"
helpMessage["pickle"] = "      write index pickle file"
helpMessage["new"]    = "      new note"
helpMessage["delete"] = "      delete note"
helpMessage["change"] = "      edit note"
helpMessage["edit"]   = "      edit metadata"
helpMessage["quit"]   = "      exit notes"
helpMessage["help"]   = "      display this message"
helpMessage["search"] = "      search notes with regex"
helpMessage["command"]= "      run a command in the prompt"
helpMessage["cfocus"] = "      change window focus (tab)"
settings["helpMessage"] = helpMessage
