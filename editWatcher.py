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

        # messages for tracking anomalies in file size
        base = os.path.basename(tmpDir)
        self._anomalies = []
        self._anomaliesLogPath = os.path.join(settings["tmpPath"],f"anomalies-{base}.txt")

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

    def _safeFileSize(self,path):
        if os.path.exists(path):
            return os.path.getsize(path)
        else:
            return -1

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

    def dumpAnomaliesLog(self):
        output = open(self._anomaliesLogPath,"w")
        for message in self._anomalies:
            output.write(message+"\n")
        output.close()


    def run(self):
        while True:

            if True:
            # try:

                # check queue for instructions
                if self._input.qsize():
                    update = self._input.get()
                    if update["type"] == "close":
                        finalCopy = self.sync()
                        if len(self._anomalies):
                            self._outputq.put({"message":f"ERROR: {len(self._anomalies)} file anomalies. See log. {self._nSyncs} syncs, {self._nCopies} copies. Final sync: {finalCopy}"})
                            self.dumpAnomaliesLog()
                        else:
                            self._outputq.put({"message":f"Updated remote file. {self._nSyncs} syncs, {self._nCopies} copies. Final sync: {finalCopy}"})
                        return

                # check directory for updates
                self.updateListOfFiles()
                self.sync()
                time.sleep(1)

            # except:
            #     self._anomalies.append(f"{self.now()} Edit Watcher Crashed")


    def sync(self):
        self._nSyncs+=1
        self.updateModTimes()
        nSync = 0


        for tmpFile in self._trackedFilesSyncedTimes.keys():
            modTime  = self._trackedFilesModTimes[tmpFile]
            syncTime = self._trackedFilesSyncedTimes[tmpFile]

            # if self._safeFileSize(tmpFile)<=0:
            #     self._anomalies.append(f"{self.now()} Issue with temporary local file, size: {self._safeFileSize(tmpFile)} bytes: {tmpFile}.")

            if modTime>syncTime:
                self._nCopies+=1
                remoteFile = self.tmpToRemote(tmpFile)
                cmd = f"cp {tmpFile} {remoteFile}"
                cp = os.popen(cmd).read()
                # log(f"editwatcher {self._iLog}: copy {tmpFile} {self.tmpToRemote(tmpFile)}, because {modTime}>{syncTime}")
                self._iLog+=1
                nSync+=1
                self._trackedFilesSyncedTimes[tmpFile] = time.time()

                if self._safeFileSize(remoteFile)<=0:
                    self._anomalies.append(f"{self.now()} Issue with remote file, size: {self._safeFileSize(remoteFile)} bytes: {remoteFile}.")

                # update modification time
                # this is just in case the editor is quit without returning to the main thread
                # unfortunately, it won't be reflected in the index
                # to fix this, should put index in its own thread, communicate to it from here
                metaPath = os.path.join(self._remoteDir,"meta.json")
                meta = json.load(open(metaPath,"r"))
                meta["modified"] = self.now()
                json.dump(meta,open(metaPath,"w"),indent=4)

                if self._safeFileSize(metaPath)<=0:
                    self._anomalies.append(f"{self.now()} Issue with remote meta file, size: {self._safeFileSize(metaPath)} bytes: {metaPath}.")



        return nSync


if __name__=="__main__":
    print(settings.keys())
