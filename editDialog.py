from __future__ import division
from setup import *

# import math, sys, time, copy
# import curses
# import logging
# import numpy as np
# import datetime
# import textpad


# from backend import *
# from drawingFunctions import _drawBox, _drawBoxOutline, _print, _text, _point

"""
Pop-up dialog for editing an event
Originally from isoplan
"""

class editDialog:
    def __init__(self,window,data):
        self._data = dict(data)
        self._origData = dict(data)
        self._window = window
        self._optionFocusColor     = settings["dialogDialogFocus"]
        self._optionRegularColor   = settings["dialogDialogBackground"]
        self._optionBackground     = settings["dialogDialogBackground"]

        # self._optionRegularColor   = 0
        # self._optionFocusColor     = 0

        window.bkgd(curses.color_pair(self._optionRegularColor))


        self._focus = 0
        self._anyChangesMade = False
        # window.clear()
        self.update(window)

    def _drawTextline(self,y,x,name,defaultValue,focused):
        """ Draw textbox, and line """
        # this is needed to sanitize spaces
        defaultValue = str(defaultValue).replace('\x02'," ")
        # check if focused
        if focused:
            color = self._optionFocusColor
        else:
            color = self._optionRegularColor
        utils._text(self._window,y,x,name,color=color)
        windowWidth = self._screenX-len(name)-2
        borderWindow = self._window.derwin(3,windowWidth-1,y-1,x+len(name)-1)
        borderWindow.clear()
        borderWindow.bkgd(curses.color_pair(color))
        borderWindow.border()
        textWindow = self._window.derwin(1,windowWidth-3,y,x+len(name)-0)
        text = textpad.Textbox(textWindow,windowWidth-3,commandMode=0)
        text.set(defaultValue)
        # for i,character in enumerate(str(defaultValue)):
            # text.do_command(character)
        return text, textWindow


    def _drawData(self):
        """ Draw data corresponding to this day 
            Creates self._inputs, which stores the textboxes
        """
        # draw date info
        dateLine = "Day: {0}".format(1)
        utils._text(self._window,0,2,dateLine, color=self._optionRegularColor)

        # draw id in bottom 
        idLine = "ID: {0}".format("1")
        utils._text(self._window,self._screenY-1,2,idLine, color=self._optionRegularColor)

        # debug
        utils._text(self._window,0,self._screenX-5,self._focus, color=self._optionRegularColor)

        data = self._data
        # decide what inputs to show in dialog
        inputsToShow = data.keys()
        # inputsToShow.pop(inputsToShow.index("id"))
        # ordering
        def sortOrder(x):
            if x=="msg": return 1
            if x=="category": return 2
            if x=="time": return 3
            if x=="notes": return 4
            if x=="Frequency": return 5
            if x=="From": return 6
            if x=="Until": return 7
            else: return 8
        inputsToShow=sorted(inputsToShow,key=sortOrder)
        shift = 3
        leftMargin = 2

        # display data
        spacing = 1
        # spacing = math.floor((self._screenY-2)/len(data.keys()))
        maxLenKey = max([len(k) for k in data.keys()])+2
        textBoxWidth = self._screenX-maxLenKey-leftMargin-3
        self._inputs = []

        for iKey, key in enumerate(inputsToShow):
            yPos=int(iKey*max(3,spacing)) + shift
            if yPos+2>self._screenY:
                nUnseen = len(data.keys())-self._screenY+4
                keyLine = "... {0} additional parameter{1} ...".format(nUnseen,["","s"][nUnseen>1])
                utils._text(self._window,yPos+0,int((self._screenX-len(keyLine))/2),keyLine, color=self._optionRegularColor)
                break
            keyLine = "{0}: {1}".format(key," "*(maxLenKey-len(key)))
            focused = (iKey == self._focus)
            inputline = {}
            inputline["name"] = key
            inputline["text"],inputline["window"] = self._drawTextline(yPos,leftMargin,keyLine,data[key],focused)
            inputline["content"] = str(data[key])
            self._inputs.append(inputline)


    def _nextFocus(self):
        """ Increment focus """
        self._focus+=1
        self._focus%=len(self._inputs)+0
    def _prevFocus(self):
        """ Increment focus """
        self._focus-=1
        self._focus%=len(self._inputs)+0

    def _getInput(self):
        """ Get input from currently selected textbox """
        curses.curs_set(1)
        text = self._inputs[self._focus]["text"]
        name = self._inputs[self._focus]["name"]
        text.edit(checkInput)
        new = text.gather()
        # remove trailing spaces
        new = new.replace("\x02"," ")
        new = new.replace("\x00"," ") # ugh, changed in update
        while len(new)>0 and new[-1]==" ": new=new[:-1]
        self._data[name] = new
        curses.curs_set(0)
        self._anyChangesMade = True

    def _delete(self):
        """ Delete contents of input """
        content = self._inputs[self._focus]["content"]
        text = self._inputs[self._focus]["text"]
        window = self._inputs[self._focus]["window"]
        name = self._inputs[self._focus]["name"]
        self._data[name]=""
        text.set("")


        window.refresh()
        self._window.refresh()
        self._anyChangesMade = True
        self._drawData()

    def update(self,window=None):
        if window!=None:
            self._window = window
        self._screenY,self._screenX = self._window.getmaxyx()
        utils._drawBox(self._window,0,0,self._screenY,self._screenX," ",self._optionBackground)
        self._window.border()
        self._drawData()
        # self._window.refresh()

    def finish(self,changed,data):
        """ Clean up screen, return info """
        self._window.clear()
        # data["msg"]="newEvent"
        # data["category"]="newCat"
        # self._window.refresh()
        if not self._anyChangesMade:
            changed=False
        return changed,data

    def run(self):
        first = True
        first = False
        while True:
            if first:
                c = ord("i")
            else:
                c = self._window.getch()

            if False:
                pass
            elif c == ord("j"):
                self._nextFocus()
                self.update()
            elif c == ord("k"):
                self._prevFocus()
                self.update()
            elif c == ord("d"):
                self._delete()
                self.update()
            elif c == ord("c"):
                self._delete()
                self._getInput()
                self.update()
            elif c == ord("i"):
                self._getInput()
                self.update()
            elif c == curses.KEY_RESIZE:
                self._window.clear()
                self.update(self._window)
                self._window.refresh()
            # press escape to cancel
            elif c in [27,ord("x"),ord("q")]:
                return self.finish(False, self._origData)
            # press enter to save
            elif c in [10,ord("w")]:
                return self.finish(True, self._data)
            first = False


def checkInput(k):
    # 32 is space
    # 27 is escape
    # 10 is enter
    # _print(k)
    if k == 27: return 10
    # if k == 32: return "_"
    return k


