from setup import *
import editDialog

"""
Container for various IO and DB functions
"""

class functions:
    def __init__(self,nv,fv,screen):
        self._nv = nv
        self._fv = fv
        self._screen = screen

    def deleteNote(self,args):
        """ Delete note based on name
        """
        path=settings["dataPath"]
        names = [glob.glob(os.path.join(path,n)) for n in args]
        names = [i for l in names for i in l]

        indexPath = settings["indexPath"]
        index = pickle.load(open(indexPath))

        for name in names:
            picklePath = os.path.join(name,"meta.pickle")
            data = utils.getData(picklePath)
            tags = data["tags"]
            xprint(tags)
            for tag in tags:
                if os.path.basename(name) in index[tag]:
                    index[tag].remove(os.path.basename(name))

            # remove from index 

            toPath = os.path.join(settings["trashPath"],os.path.basename(name))
            c,toPath=utils.uniquifyPath(toPath)
            cmd = "mv {} {}".format(name,toPath)
            os.popen(cmd)

        pickle.dump(index,open(indexPath,"w"))

        self._nv._noteName=None
        self._fv.ping()
        self._nv.ping()
        self._nv.ping()

    def dialogPopup(self,requestString):
        """ Popup to get a single string reply
        """
        screenY,screenX = self._screen.getmaxyx()
        height = 7
        width = 60
        x = int((screenX-width)/2)
        y = int((screenY-height)/2)
        dialogScreen = self._screen.subwin(height,width,y,x)
        displayData = {}
        displayData[requestString] = ""
        edits = editDialog.editDialog(dialogScreen,displayData)
        changed,newDat = edits.run()
        return newDat[requestString].split()
        # return "".join(newDat[requestString])

    def newNote(self,args):
        """ Make new empty note
            Return 0 if problem
            Return directory path otherwise
        """
        if len(args)==0: 
            args=self.dialogPopup("New note name")
            self._fv.ping()
            self._nv.ping()

        if len(args)==0: return

        protoData = {}
        protoData["displayName"] = " ".join(args)
        name = "_".join(args)
        name = name.replace(" ","_")
        today = date.today().strftime("%d%m%y")

        # make directory
        dirName = "{}-{}.note".format(today,name)
        dirPath = os.path.join(settings["dataPath"],dirName)
        # avoid conflicts
        if os.path.exists(dirPath): return False
        os.makedirs(dirPath)

        # make files
        picklePath = os.path.join(dirPath,"meta.pickle")
        protoData["created"] = time.time()
        protoData["displayCreated"] = today
        protoData["name"] = name
        protoData["dirName"] = dirName
        protoData["dirPath"] = dirPath
        protoData["uniqueFileCounter"] = 0
        protoData["tags"] = []
        pickle.dump(protoData,open(picklePath,"w"))
        notePath = os.path.join(dirPath,"note.md")
        open(notePath,"w").write("")
        dataPath = os.path.join(dirPath,"data")
        os.makedirs(dataPath)

        return dirPath

    def editAttributes(self,args):
        """ Edit attributes of a pickle file
            Use edit dialog taken from isocal
            No arguements, uses current
        """

        screenY,screenX = self._screen.getmaxyx()
        height = 10
        width = 60
        x = int((screenX-width)/2)
        y = int((screenY-height)/2)
        dialogScreen = self._screen.subwin(height,width,y,x)

        dataPath = self._nv.curPath()["data"]
        notePath = self._nv.curPath()["note"]
        indexPath = settings["indexPath"]
        index = pickle.load(open(indexPath))
        data = pickle.load(open(dataPath))
        tagsBeforeChange = list(data["tags"])

        # trimmed data to display
        displayData = {}
        displayData["name"] = data["displayName"]
        displayData["tags"] = ",".join(data["tags"])

        edits = editDialog.editDialog(dialogScreen,displayData)
        changed,newDat = edits.run()

        # merge results back into pickle file, and global tag index
        if changed:
            data["displayName"] = newDat["name"]
            newDat["tags"]=newDat["tags"].upper()
            data["tags"] = newDat["tags"].split(",")
            pickle.dump(data,open(dataPath,"w"))

            # update index
            for tag in data["tags"]:
                if tag not in index.keys():
                    index[tag] = []
                if data["dirName"] not in index[tag]:
                    index[tag].append(data["dirName"])

            # remove entries from index if they were removed from this note
            for tag in tagsBeforeChange:
                if tag not in index.keys():
                    index[tag] = []
                if tag not in data["tags"]:
                    index[tag].remove(data["dirName"])

        pickle.dump(index,open(indexPath,"w"))

    def remakeIndex(self,args=None):
        """ Update index file
        """
        allDirs = os.listdir(settings["dataPath"])
        index={}
        for path in allDirs:
            picklePath = os.path.join(settings["dataPath"],path,"meta.pickle")
            if not os.path.exists(picklePath): continue
            data = utils.getData(picklePath)
            tags = data["tags"]
            for tag in tags:
                if tag not in index.keys(): index[tag]=[]
                index[tag].append(data["dirName"])

        pickle.dump(index,open(settings["indexPath"],"w"))



        # pickle.dump(index,open(indexPath,"w"))

    def filterNotes(self,args=None):
        """ Filter files by tags
        """
        xprint("==========================")
        args = [a.upper() for a in args]
        if args:
            tags = args
            self._fv.setMode("tags",tags=tags)
        else:
            self._fv.setMode("path")
        # go to new filtered file
        self._fv.ping()
        self._nv.load(self._fv._curName())
        self._nv.ping()

    def insertMedia(self,args):
        """ Copy media to data directory
            add markdown link to end of file
        """
        if len(args)!=1: return
        fromPaths = glob.glob(args[0])
        for fromPath in fromPaths:
            fromName = os.path.basename(fromPath)
            notePath = self._nv.curPath()["note"]
            filesPath = self._nv.curPath()["files"]
            picklePath = self._nv.curPath()["data"]
            data = utils.getData(picklePath)
            data["uniqueFileCounter"]+=1
            toPath = "{}/{}-{}".format(filesPath,data["uniqueFileCounter"],fromName)
            shortPath = "data/{}-{}".format(data["uniqueFileCounter"],fromName)
            cmd = "cp {} {}".format(fromPath,toPath)
            os.popen(cmd)
            utils.writeData(picklePath,data)
            # append link to file
            linkString = '![{}]({} "{}")\n'.format(fromName,shortPath,fromName)
            open(notePath,"a").write(linkString)


        # self._fv.ping()
        self._nv.ping()
