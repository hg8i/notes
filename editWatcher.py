from setup import *

""" This class watches the local note directory
    When a change is detected, it tries copying the file to the remote location
    It reports the status when closed
"""

class editwatcher:
    def __init__(self,remoteDir,tmpDir,inputq=None,outputq=None):
        self._iLog = 0
        self._input = inputq
        self._outputq = outputq
        self._remoteDir = remoteDir
        self._tmpDir = tmpDir
        log(f"editwatcher: startup for {tmpDir}")

        self._trackedFilesModTimes = defaultdict(int)
        self._trackedFilesSyncedTimes = defaultdict(int)
        self.updateListOfFiles()
        self.updateModTimes()


        # self._tmpNotePath = os.path.join(tmpDir,"note.md")
        # self._remoteNotePath = os.path.join(remoteDir,"note.md")

        self._nSyncs=0
        self._nCopies=0
        creationTime = time.time()
        # self._lastNoteModTime = self.getNoteModTime()

        # self._outputq.put({"message":"Started Edit Watcher"})

    def now(self):
        return datetime.now().strftime("%d/%m/%y %H:%M::%S")

    def tmpToRemote(self,tmp):
        """ Convert path to remote dir, create subdir if needed
        """
        remote = tmp.replace(self._tmpDir,self._remoteDir)
        if not os.path.exists(os.path.dirname(remote)):
            os.makedirs(os.path.dirname(remote), exist_ok=True)
        return remote

    def updateListOfFiles(self):
        """ Get the files to track in the tmpDir
        """
        candidates = [os.path.join(self._tmpDir,"note.md")]
        candidates+= glob.glob(os.path.join(self._tmpDir,"figures/*"))
        # if not in dictionary, add with mod and sync time 0
        for c in candidates:
            self._trackedFilesSyncedTimes[c]
            self._trackedFilesModTimes[c]

    def updateModTimes(self):
        for c in self._trackedFilesSyncedTimes.keys():
            # file doesn't exist, remove
            if not os.path.exists(c):
                del self._trackedFilesSyncedTimes[c]
                del self._trackedFilesModTimes[c]
                continue
            # update modification time
            self._trackedFilesModTimes[c] = os.path.getmtime(c)

    def run(self):
        while True:

            # check queue for instructions
            if self._input.qsize():
                update = self._input.get()
                if update["type"] == "close":
                    finalCopy = self.sync()
                    self._outputq.put({"message":f"Updated remote file. {self._nSyncs} syncs, {self._nCopies} copies. Final sync: {finalCopy}"})
                    return

            # check directory for updates
            self.updateListOfFiles()
            self.sync()
            time.sleep(1)


    def sync(self):
        self._nSyncs+=1
        self.updateModTimes()
        nSync = 0


        for c in self._trackedFilesSyncedTimes.keys():
            modTime  = self._trackedFilesModTimes[c]
            syncTime = self._trackedFilesSyncedTimes[c]
            tmpPath = c

            if modTime>syncTime:
                self._nCopies+=1
                cmd = f"cp {c} {self.tmpToRemote(c)}"
                cp = os.popen(cmd).read()
                # log(f"editwatcher {self._iLog}: copy {c} {self.tmpToRemote(c)}, because {modTime}>{syncTime}")
                self._iLog+=1
                nSync+=1
                self._trackedFilesSyncedTimes[c] = time.time()

                # update modification time
                # this is just in case the editor is quit without returning to the main thread
                # unfortunately, it won't be reflected in the index
                # to fix this, should put index in its own thread, communicate to it from here
                metaPath = os.path.join(self._remoteDir,"meta.json")
                meta = json.load(open(metaPath,"r"))
                meta["modified"] = self.now()
                json.dump(meta,open(metaPath,"w"),indent=4)




        return nSync



