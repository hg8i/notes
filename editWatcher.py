from setup import *

""" This class watches the local text file
    When a change is detected, it tries copying the file to the remote location
    It reports the status when closed
"""

class editwatcher:
    def __init__(self,remoteDir,tmpDir,inputq=None,outputq=None):
        self._input = inputq
        self._outputq = outputq
        self._remoteDir = remoteDir
        self._tmpDir = tmpDir
        self._tmpNotePath = os.path.join(tmpDir,"note.md")
        self._remoteNotePath = os.path.join(remoteDir,"note.md")

        self._nSyncs=0
        self._nCopies=0
        creationTime = time.time()
        self._lastNoteModTime = self.getNoteModTime()

        # self._outputq.put({"message":"Started Edit Watcher"})

    def getNoteModTime(self):
        if not os.path.exists(self._tmpNotePath):
            return 0
        ret= os.path.getmtime(self._tmpNotePath)
        return ret

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
            self.sync()
            time.sleep(1)


    def sync(self):
        self._nSyncs+=1
        if self.getNoteModTime()> self._lastNoteModTime:
            self._nCopies+=1
            cmd = f"cp {self._tmpNotePath} {self._remoteNotePath}"
            cp = os.popen(cmd).read()
            log(f"editwatcher: copy {self._tmpNotePath} {self._remoteNotePath}")
            return True
        return False



