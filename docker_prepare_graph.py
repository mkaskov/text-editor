#! /usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import sys
import re

datasetFolder = sys.argv[1]
editorMode = sys.argv[2]
editorPort = sys.argv[3]
if len(sys.argv) == 5: prepare = sys.argv[4]
else: prepare="false"

def base_prepare():
    filesToWrite = ["web_GraphParser_2.sh"]

    for fileName in filesToWrite:
        with open(fileName, "r") as myfile: s = myfile.read()

        ret = re.sub("--port\s\d{1,4}", "--port "+editorPort, s)
        ret = re.sub("url_database=[\S]+", "url_database=db:5432/ttp", ret)

        print("[File]", fileName, "_________________________________________________________")
        print (ret)
        print("[File]", fileName, "_________________________________________________________")

        with open(fileName, "w") as text_file: text_file.write(ret)

if prepare=="prepare": base_prepare()
