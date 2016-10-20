#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import sys
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

fileName = "app2web_ner.py"
with open(fileName, "r") as myfile: s = myfile.read()
ret = re.sub("url_database\s+=\s+[\S]+", "url_database = \"" +datasetFolder +"/database/base.xlsx\" --fixdataset=true", s)
print ("[File]",fileName,"-------------------------------------------------------------")
print (ret)
with open(fileName, "w") as text_file: text_file.write(ret)

def fix_dataset():
    fileName = "/home/service/data_base/checkpoints/checkpoint"
    with open(fileName, "r") as myfile: s = myfile.read()
    ret = re.sub("model_checkpoint_path:\s+[\S]+checkpoints/", "model_checkpoint_path: \"/home/service/data_base/checkpoints/", s)
    ret = re.sub("all_model_checkpoint_paths:\s+[\S]+checkpoints/", "all_model_checkpoint_paths: \"/home/service/data_base/checkpoints/", ret)
    print ("[File]",fileName,"-------------------------------------------------------------")
    print (ret)
    with open(fileName, "w") as text_file: text_file.write(ret)