import multiprocessing
import curses
from curses import wrapper
import time,os,sys,glob,json
from datetime import datetime
from collections import defaultdict
import re
import pickle

from subprocess import call

logon = True
os.popen("rm log.txt"); time.sleep(0.01)
def log(*text):
    global logon
    # if not logon: return
    f = open("log.txt","a")
    text = " ".join([str(t) for t in text])
    f.write(str(text)+"\n")
    f.close()

debug = 1

thispath = os.path.dirname(os.path.abspath(__file__))

if debug:
    remotepath = thispath #debug
    htmlpath = "/eos/user/a/aawhite/www/notes"
    logon = True
else:
    remotepath = "/home/prime/sshfs/lxp/notes"
    htmlpath = "/eos/user/a/aawhite/www/notes"
    logon = False


settings = {}

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

settings["deleteChar"]         = 263
settings["ctrlUChar"]         = 21
settings["enterChar"]         = 10
settings["escapeChar"]         = 27

settings["overflowSymbol"] = ">"

settings["bkColorCommandView"]         = color_dark_blue
settings["fgColorCommandView"]         = color_white
settings["bkColorNotesView"]           = color_dark_blue
settings["fgColorNotesView"]           = color_white
settings["bkColorFilesView"]           = color_dark_cyan
settings["fgColorFilesView"]           = color_white
settings["bkColorFilesViewHighlight"]  = color_white
settings["fgColorFilesViewHighlight"]  = color_dark_cyan

# dialog box
settings["fgColorDialog"]          = color_light_grey
settings["bkColorDialog"]          = color_dark_grey
settings["bkColorDialogHighlight"] = color_dark_grey
settings["fgColorDialogHighlight"] = color_dark_cyan

settings["filesWidth"] = 30
settings["commandHistoryPath"] = os.path.join(thispath,"history.txt")
settings["indexPath"] = os.path.join(remotepath,"storedIndex.pickle")
settings["dataPath"] = os.path.join(remotepath,"data")
settings["htmlPath"] = os.path.join(htmlpath,"pages")
settings["tmpPath"] = "/tmp/notetmp"
settings["delPath"] = "/tmp/notetrash"

hotkeyMap = defaultdict(lambda:None)
hotkeyMap["/"] = "search"
hotkeyMap["\t"] = "cfocus"
hotkeyMap["c"] = "change"
hotkeyMap["e"] = "edit"
hotkeyMap["q"] = "quit"
hotkeyMap["h"] = "help"
hotkeyMap["n"] = "new"
hotkeyMap[":"] = "command"
hotkeyMap["p"] = "publish"
settings["hotkeyMap"] = hotkeyMap

shortcutMap = defaultdict(lambda:None)
shortcutMap["p"] = "publish"
shortcutMap["b"] = "pickle"
shortcutMap["k"] = "key"
shortcutMap["n"] = "new"
shortcutMap["d"] = "delete"
shortcutMap["c"] = "change"
shortcutMap["e"] = "edit"
shortcutMap["s"] = "sort"
shortcutMap["q"] = "quit"
shortcutMap["h"] = "help"
settings["shortcutMap"] = shortcutMap

helpMessage = defaultdict(lambda:None)
helpMessage["key"]    = "[arg] set search key (tag,name,modified,all)"
helpMessage["sort"]   = "[arg] sort note list (name,modified,created,tag)"
helpMessage["pickle"] = "      write index pickle file"
helpMessage["publish"]= "      generate website"
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

from markdown import markdown

def dd(d):
    if type(d) in [str,int,float,dict,list]:
        return d
    for k,v in d.items():
        d[k] = dd(v)
    return dict(d)

def updateBuffer(buffer,char,pos=0):
    if char==settings["deleteChar"]:
        buffer=buffer[:-1]
        pos-=1
    elif char==settings["ctrlUChar"]:
        buffer=""
        pos = 0
    else:
        buffer+=chr(char)
        pos+=1
    pos = max(pos,0)
    pos = min(pos,len(buffer))
    return buffer,pos

try:
    import private_settings
    settings["htmlsync"] = private_settings.htmlsync
    settings["siteUrl"] = private_settings.siteUrl
except:
    settings["htmlsync"] = ""
    settings["siteUrl"] = ""
