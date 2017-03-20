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
    filesToWrite = ["web_GraphParser_2.sh","train.sh"]

    for fileName in filesToWrite:
        with open(fileName, "r") as myfile: s = myfile.read()

        ret = re.sub("data_dir=[\S]+", "data_dir="+datasetFolder, s)
        #ret = re.sub("python3 app2web_graph_2.py", "python3 app2web_graph_2.py --fixdataset=true", ret)
        #ret = re.sub("--port=\d+", "--port="+editorPort, ret)
        ret = re.sub("url_database=[\S]+", "url_database=db:5432/ttp", ret)
        if editorMode=="gpu": ret = re.sub("--usegpu=\S+", "--usegpu=true", ret)
        elif editorMode=="cpu": ret = re.sub("--usegpu=\S+", "--usegpu=false", ret)

        print ("[File]",fileName,"-------------------------------------------------------------")
        print (ret)

        with open(fileName, "w") as text_file: text_file.write(ret)

if prepare=="prepare": base_prepare()

def fix_dataset():
    fileName = "/home/service/data_base/checkpoints/checkpoint"
    with open(fileName, "r") as myfile: s = myfile.read()
    ret = re.sub("model_checkpoint_path:\s+[\S]+checkpoints/", "model_checkpoint_path: \"/home/service/data_base/checkpoints/", s)
    ret = re.sub("all_model_checkpoint_paths:\s+[\S]+checkpoints/", "all_model_checkpoint_paths: \"/home/service/data_base/checkpoints/", ret)
    print ("[File]",fileName,"-------------------------------------------------------------")
    print (ret)
    with open(fileName, "w") as text_file: text_file.write(ret)

