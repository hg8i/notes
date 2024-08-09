from setup import *

"""
# Class to generate HTML pages from markdown note directories
"""

class markdown:
    def __init__(self,name,outputq,event):
        self._name = name
        self._event = event
        self._output = outputq
        # self.pageHead = [] # metadata
        self.htmlTable = "" # meta file text
        self.htmlNote = "" # note text
        # self.pageFoot = [] # footer
        self._notePath   = os.path.join(settings["dataPath"],name)
        self._htmlPath   = os.path.join(settings["tmpPath"],f"{name}")
        self._htmlImages = os.path.join(self._htmlPath,"images")

        # Make required/assumed directories
        os.makedirs(self._htmlPath,exist_ok=1)
        while not os.path.exists(self._htmlPath): time.sleep(0.01)
        os.makedirs(self._htmlImages,exist_ok=1)
        while not os.path.exists(self._htmlPath): time.sleep(0.01)

    def run_view(self):
        """ Generate website and view it with command defined in setup.py
        """
        log(f"Generating note from {self._notePath}")
        log(f"Saving page to {self._htmlPath}")
        self.report(f"Parsing note {self._name}")
        self.parseJson()
        self.parseMarkdown()
        self.report(f"Generating note {self._name}")
        path = self.generateSite()
        self.report(f"Note generated to {path}")
        cmd = f'{settings["htmlview"]} {path}'
        self.report(f"Run {cmd}")
        # launch 
        prog = lambda: subprocess.run(cmd.split(),stderr=subprocess.DEVNULL)
        thread = threading.Thread(target=prog)
        thread.start()

        # self.save()
        # self.report(f"[DONE] Published to {settings['siteUrl'].format(self._name)}"})

    def run_publish(self):
        """ Publish website to location from private_settings.py
        """
        log(f"Generating note from {self._notePath}")
        log(f"Saving page to {self._htmlPath}")
        self.report(f"Parsing note {self._name}")
        self.parseJson()
        self.parseMarkdown()
        self.report(f"Publishing note {self._name}")
        self.publishSite()
        self.report(f"[DONE] Published to {settings['siteUrl'].format(self._name)}")

    def parseJson(self):
        meta     = json.load(open(os.path.join(self._notePath,"meta.json"),"r"))
        rows = {}
        rows[" "]     = meta["name"] if "name" in meta.keys() else "Name"
        # rows[" "]     = rows[" "].capitalize()
        rows["Created:"]  = meta["created"] if "created" in meta.keys() else "No creation date"
        rows["Modified:"] = meta["modified"] if "modified" in meta.keys() else "No modification date"
        html = ""
        html+="<table>\n"
        for row,val in rows.items():
            html+=f"<tr><td>{row}</td><td>{val}</td></tr>\n"
        html+="</table>\n"
        self.htmlTable = html
        self.htmlTitle = rows[" "]

    def blockReplacement(self,blockText):
        self.blockCounter+=1
        blockHolder = f'BLOCKHOLD-{self.blockCounter}'
        self.blockMapper[blockHolder] = blockText
        return blockHolder

    def getUniquePath(self,dirname,filename):
        ret = os.path.join(dirname,filename)
        # Make sure ret doesn't already exist
        u = 0
        while os.path.exists(ret):
            ret = os.path.join(dirname,f"u-{u}-{filename}")
            u+=1
        return ret

    def parseMarkdown(self):

        note = open(os.path.join(self._notePath,"note.md"),"r").read()

        # Get list of all attached files
        imageMovements = {}
        imagePattern = re.compile(r'!\[(.*)\]\((.*)\)')
        images = imagePattern.findall(note)
        for (alt,path) in images:
            imageMovements[path] = os.path.join(self._htmlImages,os.path.basename(path))
            # imageMovements[path] = self.getUniquePath(self._htmlImages,os.path.basename(path))
            # determine if it is an absolute path or a relative path
            if path[0]=="/":
                # absolute path
                cmd = f"cp {path} {imageMovements[path]}"
            else:
                # relative path to self._notePath
                cmd = f"cp {os.path.join(self._notePath,path)} {imageMovements[path]}"
            log(f"COPY: {cmd}")
            os.popen(cmd)

        # Replace paths
        for origin,destination in imageMovements.items():
            destination = f"images/{os.path.basename(destination)}"
            note = re.sub(origin,destination,note)

        # STEP 1: Replace every < and >
        note = re.sub(">",r'&gt;',note)
        note = re.sub("<",r'&lt;',note)

        # STEP 2: Exclude blocks of preformatted text, save in dictionary
        self.blockCounter = 0
        self.blockMapper = {}
        blockPattern = re.compile(r'```\n*([\s\S]*?)\n*```')
        blockHtml = r'<pre id="pre-paragraph">\n\1\n</pre>'
        note = re.sub(blockPattern,self.blockReplacement,note)
        log(f"Identified {len(self.blockMapper.keys())} block quotes")

        note = note.split("\n")
        note = [l.rstrip() for l in note]

        # STEP 3: Perform majority of HTML conversions
        expressions = {
            'h1':       {'e':re.compile(r'^\s*#\s*([^#\n\r]+)'),'r':r'<h1>\1</h1>'},
            'h2':       {'e':re.compile(r'^\s*##\s*([^#\n\r]+)'),'r':r'<h2>\1</h2>'},
            'h3':       {'e':re.compile(r'^\s*###\s*([^#\n\r]+)'),'r':r'<h3>\1</h3>'},
            'h4':       {'e':re.compile(r'^\s*#{4,}\s*([^#\n\r]+)'),'r':r'<h4>\1</h4>'},
            'bullet':   {'e':re.compile(r'^[\*\t]{1}\s+(.*)'),'r':r'<li>\1</li>'},
            'subbullet':{'e':re.compile(r'^(?:[\*]{2}|\s{4}\*)\s+(.*)'),'r':r'<ul><li>\1</li></ul>'},
            'ssbullet': {'e':re.compile(r'^(?:[\*]{3}|\s{8}\*)\s+(.*)'),'r':r'<ul><ul><li>\1</li></ul></ul>'},
            'freeurl':  {'e':re.compile(r'((http[s]?://|www.)[^\s)><]+)(?![^()]*\))'),'r':r'<a href="\1">\1</a>'}, # needs to come BEFORE link
            'link':     {'e':re.compile(r'(^|[^!]){1}\[(.*)\]\((.*)\)'),'r':r'\1<a href="\3">\2</a>'},
            'image':    {'e':re.compile(r'!\[(.*)\]\((.*)\)'),'r':r'<a href="\2"><img src="\2" alt="\1" width="500"></a>'},
            'preform':  {'e':re.compile(r'^>(.*)'),'r':r'<pre id="pre-inline">\1</pre>'},
        }
        for iLine,line in enumerate(note):
            # log("-"*50)
            # log(line)
            for name,expr in expressions.items():
                # Check if line matches
                if expr["e"].search(line):
                    line = re.sub(expr["e"], expr["r"], line)
                    note[iLine] = line
                    # log(name,line)
                    # break

        note = "<p>\n".join(note)

        for blockHolder,blockText in self.blockMapper.items():
            # log(blockHolder,blockText.group(1))
            blockHtml = f'<pre id="pre-paragraph">\n{blockText.group(1)}\n</pre>'
            note = re.sub(blockHolder,blockHtml,note)

        self.htmlNote = note

    def generateSite(self):
        # Load HTML template
        thispath = os.path.dirname(os.path.abspath(__file__))
        template = open(os.path.join(thispath,"htmlResources/template.html")).read()
        page = template.format(self.htmlTitle,self.htmlTable,self.htmlNote)

        # save webpage
        oPath = os.path.join(self._htmlPath,"index.html")
        oFile = open(oPath,"w")
        oFile.write(page)
        oFile.flush()
        return oPath

    def publishSite(self):
    # def save(self):

        # Save text files
        oPath = os.path.join(self._htmlPath,"table.html")
        oFile = open(oPath,"w")
        oFile.write(self.htmlTable)
        oFile.flush()

        oPath = os.path.join(self._htmlPath,"note.html")
        oFile = open(oPath,"w")
        oFile.write(self.htmlNote)
        oFile.flush()

        oPath = os.path.join(self._htmlPath,".htaccess")
        oFile = open(oPath,"w")
        oFile.write("SetHandler none")
        oFile.flush()

        # Copy meta
        cmd = f'cp {os.path.join(self._notePath,"meta.json")} {self._htmlPath}'
        os.popen(cmd).read()


        # Load HTML template
        thispath = os.path.dirname(os.path.abspath(__file__))
        template = open(os.path.join(thispath,"htmlResources/template.html")).read()
        page = template.format(self.htmlTitle,self.htmlTable,self.htmlNote)

        # save webpage
        oPath = os.path.join(self._htmlPath,"index.html")
        oFile = open(oPath,"w")
        oFile.write(page)
        oFile.flush()

        # Synchronize to EOS
        cmd = settings["htmlsync"].format(self._htmlPath,settings["htmlPath"])
        log(f"Synced to: https://aawhite.web.cern.ch/notes/pages")
        log(cmd)
        # os.popen(cmd).read()

        self.report(f"Starting copy: {cmd}")

        import subprocess
        cmd = cmd.split()
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=1)
        while True:
            std = process.stdout.readline()
            if std:
                c = repr(std.strip())
                self.report(f"Publishing note: {c}")
            err = process.stderr.readline()
            if err:
                c = repr(err.strip())
                self.report(f"Publishing note: {c}")
            # check if thread is done and no output
            p = process.poll()
            if p!=None and std=="" and err=="":
                break
        time.sleep(5)


    def report(self,m):
        """ Report a message to main thread
        """
        self._output.put({"type":"markdown","message":m}); 
        # set event to notify main thread of change
        self._event.set()

if __name__=="__main__":
    md = markdown("061123-hey.note")
    md.run()
