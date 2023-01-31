#!/bin/env python3

from setup import *

# ==================================================
# Class to store a quick index of notes
# ==================================================

""" Shortname is the key for data!! """

class noteindex:
    def __init__(self,picklePath="index.pickle",loadPickle=True):
        self.dataPath = settings["dataPath"]
        self.picklePath = picklePath
        self.data = {} # organized by name
        self.names = {}
        self._currentPattern=None
        self._searchResults=None
        self._searchKey="all"

        if loadPickle:
            loaded = pickle.load(open(picklePath,"rb"))
            self.names = loaded.names
            self.data = loaded.data
        else:
            self.names["tag"] = defaultdict(list)
            self.names["created"] = defaultdict(list)
            self.names["modified"] = defaultdict(list)
            self.names["name"] = defaultdict(list)
            self._generateIndex()
        # self._sortKey = "name"
        self._sortKey = "modified"
        self._sortSuccess = False
        self._generateListOfNames()

    def setSearchKey(self,key):
        if key in self.names.keys() or key=="all":
            self._searchKey=key

    def getSearchKey(self):
        return self._searchKey

    def now(self):
        return datetime.now().strftime("%d/%m/%y %H:%M::%S")

    def createNote(self,name=None,shortname=None,tags=[]):
        """ Create a new note, add to index, make directories
            Returns status
        """
        now = self.now()
        dirname = f"{now.split()[0].replace('/','')}-{shortname}.note"
        dirpath = os.path.join(self.dataPath,dirname)

        # make meta.json
        meta = {}
        meta["tags"] = tags
        meta["created"] = now
        meta["modified"] = now
        meta["name"] = name
        meta["shortname"] = shortname
        meta["author"] = os.environ.get("USERNAME")
        meta["dirName"] = dirname
        meta["blocked"] = "false"
        if os.path.exists(dirpath):
            return f"Failed to create existing note directory {dirpath}"
        else:
            os.makedirs(dirpath)

        # save
        metaPath = os.path.join(dirpath,"meta.json")
        json.dump(meta,open(metaPath,"w"),indent=4)


        # add note to index
        self.add(dirpath)
        self.setMeta(shortname,meta) # also updates pickle

        return f"Created new note: {name}"


    def _loadNote(self,path):
        """ Load note meta data """
        log("Loading: ",path)
        meta = json.load(open(path,"r"))
        assert "shortname" in meta.keys(), "Missing 'key' information :)"
        return meta

    def _generateIndex(self):
        """ Generate index from files in dataPath """
        for notePath in glob.glob(self.dataPath+"/*note"):
            self.add(notePath)

    def sToDate(self,s):
        if type(s)!=str: return s
        return datetime.strptime(s,"%d/%m/%y %H:%M::%S")

    def dateToS(self,d):
        if type(d)==str: return d
        return datetime.strftime(d,"%d/%m/%y %H:%M::%S")

    def add(self,notePath):
        metaPath = os.path.join(notePath,"meta.json")
        meta = json.load(open(metaPath,"r"))
        shortname = meta["shortname"]
        tags = meta["tags"]
        name = meta["name"]
        # copy data into dictionaries
        self.data[shortname] = meta

        # convert datestrings into datetime objects
        meta["created"] = self.sToDate(meta["created"])
        meta["modified"] = self.sToDate(meta["modified"])

        self.names["created"][meta["created"]].append(shortname)
        self.names["modified"][meta["modified"]].append(shortname)
        self.names["name"][name].append(shortname)
        [self.names["tag"][tag].append(shortname) for tag in tags]

    def _get(self,prog,key="name"):
        """ Return list of note names with matching tags
            "prog" is a regular expression
        """
        # get all matching tags
        # prog = re.compile(prog,re.IGNORECASE)
        if key in ["modified","created"]:
            # convert dates to string
            targets = [t for t in self.names[key] if prog.findall(self.dateToS(t))]
            names   = [ n  for t in targets for n in self.names[key][t] ]
        else:
            targets = [t for t in self.names[key] if prog.findall(t)]
            names   = [ n  for t in targets for n in self.names[key][t] ]
        log(f"Searching {key}\tFound:{targets}, {len(names)} names")
        return names

    def _sort(self,data,sort):
        # sort names from matching tags
        if sort == "name":
            data = sorted(data)
        elif sort == "created":
            data = sorted(data,key=lambda n: self.data[n]["created"])
        elif sort == "modified":
            data = sorted(data,key=lambda n: self.data[n]["modified"])
        return data

    def search(self,pattern,sort="name"):
        log("Search term:",repr(pattern))
        prog = re.compile(pattern,re.IGNORECASE)
        ret = {}

        # get lists of matching names
        log("="*50)
        created     = self._get(prog,key="created")
        modified    = self._get(prog,key="modified")
        tag         = self._get(prog,key="tag")
        name        = self._get(prog,key="name")
        log("="*50)

        ret["name"]     = self._sort(name,sort)
        ret["created"]  = self._sort(created,sort)
        ret["modified"] = self._sort(modified,sort)
        ret["tag"]      = self._sort(tag,sort)

        # save for internal use
        self._currentPattern=pattern
        self._searchResults=ret

        return ret

    def getPattern(self):
        return self._currentPattern

    def clearSearch(self):
        self._currentPattern=None
        self._searchResults=None

    def deleteNote(self,shortname):
        """ Delete a note (really mv it to /tmp) and clear index
        """
        assert shortname in self.data.keys()
        # delete directory
        path = self.getPath(shortname)
        basename = os.path.basename(path)
        newpath = os.path.join(settings["delPath"],basename)
        os.popen(f"mv {path} {newpath}")

        # remove from index
        del self.data[shortname]
        for k,v in self.names.items():
            for kk,vv in v.items():
                if shortname in vv: vv.remove(shortname)

        return f"Moved {shortname} to {newpath}"

    def getPath(self,shortname):
        log("Getting path for",shortname)
        assert shortname in self.data.keys()
        assert "dirName" in self.data[shortname]
        dirName = self.data[shortname]["dirName"]
        path = os.path.join(self.dataPath,dirName)
        assert os.path.exists(path), f"Note {path} not existing"
        return path

    def setMeta(self,shortname,meta):
        log("Getting path for",shortname)
        # assert shortname in self.data.keys()
        # update self (dates as datetimes)
        meta["created"] = self.sToDate(meta["created"])
        meta["modified"] = self.sToDate(meta["modified"])
        self.data[shortname] = dict(meta)
        # update disk (dates as strings)
        meta["created"] = self.dateToS(meta["created"])
        meta["modified"] = self.dateToS(meta["modified"])
        metaPath = os.path.join(self.getPath(shortname),"meta.json")
        json.dump(meta,open(metaPath,"w"),indent=4)
        # update pickle
        self.pickle()

    def getMeta(self,shortname):
        log("Getting path for",shortname)
        assert shortname in self.data.keys()
        return self.data[shortname]

    def isBlocked(self,shortname):
        meta = self.getMeta(shortname)
        return meta["blocked"] == "true"
 
    def block(self,shortname):
        log("Blocking",shortname)
        meta = self.getMeta(shortname)
        meta["blocked"] = "true"
        self.setMeta(shortname,meta)

    def unblock(self,shortname):
        log("Unblocking",shortname)
        meta = self.getMeta(shortname)
        meta["blocked"] = "false"
        meta["modified"] = self.now()
        self.setMeta(shortname,meta)
        

    def pickle(self):
        pickle.dump(self,open(self.picklePath,"wb"))

    def fullName(self,shortname):
        if shortname in self.data.keys():
            return self.data[shortname]["name"]
        else:
            return "None"

    def __getitem__(self,i):
        # log("Getting item",i,"of",self._listOfNames)
        return self._listOfNames[i]

    def __iter__(self):
        self.pos = 0
        self._generateListOfNames()
        return self

    def _generateListOfNames(self):
        if self._currentPattern!=None:
            if self._searchKey=="all":
                keys = self._searchResults.keys()
                self._listOfNames = [i for k in keys for i in self._searchResults[k]]
                self._listOfNames = list(set(self._listOfNames))
            else:
                self._listOfNames = self._searchResults[self._searchKey]
        else:
            self._listOfNames = list(self.data.keys())

        # sorting
        # if sort:
        try:
            self._listOfNames = sorted(self._listOfNames,key=lambda x: self.data[x][self._sortKey])
            if self._sortKey in ["created","modified"]:
                self._listOfNames = list(reversed(self._listOfNames))
            self._sortSuccess = True
        except:
            self._sortSuccess = False

    def getSort(self):
        if self._sortSuccess:
            return self._sortKey
        else:
            return "none"

    def getIndexOf(self,name):
        if name in self._listOfNames:
            return self._listOfNames.index(name)
        else:
            return 0

    def getPicklePath(self):
        return self.picklePath

    def setSort(self,sort):
        self._sortKey = sort

    def __len__(self):
        self._generateListOfNames()
        # log("List of names",self._listOfNames)
        # log("List of names",self.data.keys())
        return len(self._listOfNames)

    def __next__(self):
            
        if self.pos >= len(self._listOfNames):
            raise StopIteration
        else:
            self.pos += 1
            return self._listOfNames[self.pos - 1]
            # return self.data[name]

if __name__=="__main__":
    """ Test for class """
    i = noteindex(loadPickle=1)

    # example of a search
    matches = i.search("lin*")

    # example of getting the path of a given name
    name = list(i.data.keys())[0]
    log(i.getPath(name))

    # example of pickling the noteindex
    i.pickle()

    # iteration
