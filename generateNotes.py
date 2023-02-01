#!/bin/env python3

import json,pickle,os,sys,time
import random,string

# ==================================================
# Script to generate a test data directory
# ==================================================

nNotes = 100

os.popen("rm -rf data/*")
os.popen("mkdir data")
allTags = ["linux","p1","nsw","bash","oldlinux","regex"]

def dateGen():
    s = f"{random.randint(1,30):02d}/09/22 04:05::06"
    return s
    d = datetime.datetime.strptime(s,"%d/%m/%y %H:%M::%S")

for i in range(nNotes):
    d = dateGen().split()[0]
    name = "".join([string.ascii_lowercase[random.randint(0,len(string.ascii_lowercase)-1)] for i in range(16)])
    dPath = f"data/{d.replace('/','')}-{name}.note"
    print(dPath)
    os.popen("mkdir "+dPath)
    os.popen("ls "+dPath).read()
    time.sleep(0.01)
    nTags = random.randint(0,len(allTags)-1)

    # make meta.json
    data = {}
    data["tags"] = allTags[:nTags]
    data["created"] = dateGen()
    data["modified"] = dateGen()
    data["name"] = f"Note number {i}"
    data["shortname"] = name
    data["author"] = "aaron"
    data["blocked"] = "aaron"
    data["dirName"] = f"{d.replace('/','')}-{name}.note"
    json.dump(data,open(os.path.join(dPath,"meta.json"),"w"),indent=4)

    # make data
    os.popen(f"mkdir {dPath}/files")

    # make note.md
    f = open(os.path.join(dPath,"note.md"),"w")
    for i in range(100):
        f.write("".join([(string.ascii_lowercase+"  ")[random.randint(0,len(string.ascii_lowercase)+1)] for i in range(100)]))
        f.write("\n")
    f.close()

