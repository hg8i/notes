from setup import *

# A class to be launched in a thread to load note, in case it is slow

class noteloader:
    def __init__(self,path,outputq,scrollPos=0):
        self.path = path
        self.output = outputq
        self.scrollPos = scrollPos

    def run(self):
        if self.path==None:
            # prepare update frame
            data = {}
            data["type"]     = "notesview"
            data["name"]     = "No note"
            data["tags"]     = [""]
            data["created"]  = ""
            data["modified"] = ""
            data["noteText"] = ""
            data["scroll"]   = 0
            self.output.put(data)

        else:
            pathMeta = os.path.join(self.path,"meta.json")
            pathText = os.path.join(self.path,"note.md")

            # load
            if not os.path.exists(pathMeta) or not os.path.exists(pathText):
                data = {}
                data["type"]     = "notesview"
                data["name"]     = ""
                data["tags"]     = ""
                data["created"]  = ""
                data["modified"] = ""
                data["noteText"] = [f"There was a problem loading this note.",
                                    f"    * The meta file exists: {os.path.exists(pathMeta)}.",
                                    f"    * The note .md file exists: {os.path.exists(pathText)}."]
                data["scroll"]   = self.scrollPos
                self.output.put(data)
            else:
                metaData = json.load(open(pathMeta,"r"))
                textData = open(pathText,"r").readlines()
                # time.sleep(1)

                # prepare update frame
                data = {}
                data["type"]     = "notesview"
                data["name"]     = metaData["name"]
                data["tags"]     = metaData["tags"]
                data["created"]  = metaData["created"]
                data["modified"] = metaData["modified"]
                data["noteText"] = textData
                data["scroll"]   = self.scrollPos
                self.output.put(data)
