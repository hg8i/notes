from setup import *
import editDialog

"""
Container for various IO and DB functions
"""

class functions:
    def __init__(self,nv,fv):
        self._nv = nv
        self._fv = fv

    def deleteNote(self,args):
        """ Delete note based on name
        """
        path=settings["dataPath"]
        names = [glob.glob(os.path.join(path,n)) for n in args]
        names = [i for l in names for i in l]

        for name in names:
            toPath = os.path.join(settings["trashPath"],os.path.basename(name))
            c,toPath=utils.uniquifyPath(toPath)
            cmd = "mv {} {}".format(name,toPath)
            xprint (cmd)
            xprint (c)
            os.popen(cmd)

        self._nv._noteName=None
        self._fv.ping()
        self._nv.ping()
        self._nv.ping()


    def newNote(self,args):
        """ Make new empty note
            Return 0 if problem
            Return directory path otherwise
        """
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

    def editAttributes(self,screen,args):
        """ Edit attributes of a pickle file
            Use edit dialog taken from isocal
            No arguements, uses current
        """

        screenY,screenX = screen.getmaxyx()
        height = 30
        width = 60
        x = 10
        y = 10
        x = int((screenX-width)/2)
        y = int((screenY-height)/2)
        dialogScreen = screen.subwin(height,width,y,x)

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



    def filterNotes(self,args=None):
        """ Filter files by tags
        """
        if args!=None:
            tags = args
            self._fv.setMode("tags",tags=tags)
        else:
            self._fv.setMode("files")
        self._fv.ping()
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
            xprint(toPath)
            cmd = "cp {} {}".format(fromPath,toPath)
            os.popen(cmd)
            utils.writeData(picklePath,data)
            # append link to file
            linkString = '![{}]({} "{}")\n'.format(fromName,shortPath,fromName)
            open(notePath,"a").write(linkString)


        # self._fv.ping()
        self._nv.ping()
