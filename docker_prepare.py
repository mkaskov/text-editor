#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import sys
import os
import re

datasetFolder = sys.argv[1]
editorMode = sys.argv[2]
editorPort = sys.argv[3]

filesToWrite = ["web_NERparser.sh","train.sh"]

for fileName in filesToWrite:
    with open(fileName, "r") as myfile: s = myfile.read()

    ret = re.sub("data_dir=[\S]+", "data_dir="+datasetFolder, s)
    ret = re.sub("python /home/user/Documents/editor/app2web_ner.py", "python app2web_ner.py", ret)
    ret = re.sub("--port=\d+", "--port="+editorPort, ret)
    if editorMode=="gpu": ret = re.sub("--usegpu=\S+", "--usegpu=true", ret)
    elif editorMode=="cpu": ret = re.sub("--usegpu=\S+", "--usegpu=false", ret)

    print ("[File]",fileName,"-------------------------------------------------------------")
    print (ret)

    with open(fileName, "w") as text_file: text_file.write(ret)
    
with open("app2web_ner.py", "r") as myfile: s = myfile.read()

    ret = re.sub("url_database\s+=\s+[\S]+", "url_database = " +datasetFolder +"/dataset/base.xslx", s)
    
    print ("[File]",fileName,"-------------------------------------------------------------")
    print (ret)

    with open("app2web_ner.py", "w") as text_file: text_file.write(ret)