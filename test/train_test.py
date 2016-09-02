#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import urllib2, json
import os
import sys
import re
import datetime

fileInput = "/home/user/Documents/editor_data/text_editor_v15/dev-data.input"
fileOutput =  "/home/user/Documents/editor_data/text_editor_v15/dev-data.output"
storeOutput = "/home/user/datasets/construction_text_base/tests/"
url = 'http://server.puremind.tech:5002/decode_sentense'
linesNum = 10

def runTest():

    if not os.path.isfile(fileInput) or not os.path.isfile(fileOutput):
        print ("No input or output data")
        sys.exit(0)

    count = 0
    errosArray = []
    rightArray = []

    startTime = datetime.datetime.now()
    fileToWrite=storeOutput+"test_"+datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")+".txt"

    with open(fileToWrite, "w") as text_file:
        with open(fileInput) as fi:
            with open(fileOutput) as fo:
                contentI = fi.readlines()[0:linesNum]
                contentO = fo.readlines()[0:linesNum]

                print("Start processing")
                for row in enumerate(contentI):
                    count+=1
                    if count % (linesNum/10) == 0: print ("Processing:",count/(linesNum/100),"%")
                    postdata = {'query': row[1]}
                    req = urllib2.Request(url)
                    req.add_header('Content-Type', 'application/json')
                    data = json.dumps(postdata)

                    response = urllib2.urlopen(req, data)

                    answer = json.load(response)

                    if re.sub("[\s\xA0]+", "", answer['answer']).lower()!=re.sub("[\s\xA0]+", "", contentO[row[0]].decode('utf-8')).lower(): errosArray.append((row[0],answer['answer']))
                    else: rightArray.append((row[0], answer['answer']))

                print ("Errors:",len(errosArray),"/",linesNum)
                print ("Errors:",100*len(errosArray)/linesNum,"%")

        endTime = datetime.datetime.now()
        totalTime = endTime - startTime

        text_file.write("[Input data --------------------------------------------------]\n\n")
        text_file.write("Input file: %s\n" % fileInput)
        text_file.write("Output file: %s\n" % fileOutput)
        text_file.write("Start time: %s\n" % startTime.strftime("%Y-%m-%d %H:%M"))
        text_file.write("End time: %s\n" % endTime.strftime("%Y-%m-%d %H:%M"))

        text_file.write("Total time: %s\n" % str(totalTime))

        text_file.write("\n[Stats -------------------------------------------------------]\n\n")
        text_file.write("Total lines: %s\n" % linesNum)
        text_file.write("Right answers: %s\n" % len(rightArray))
        text_file.write("Error answers: %s\n" % len(errosArray))

        text_file.write("\n[Section with right answers ----------------------------------]\n\n")
        for x in rightArray:
            text_file.write("Input : %(1)s\n" % {"1": re.sub("\n", "", contentI[x[0]])})
            text_file.write("Answer: %(1)s\n" % {"1": re.sub("\n", "", x[1].encode('utf-8'))})
            text_file.write("------------------------------------------\n")

        text_file.write("\n[Section with errors------------------------------------------]\n\n")
        for x in errosArray:
            text_file.write("Input : %(1)s\n" % {"1": re.sub("\n", "", contentI[x[0]])})
            text_file.write("Output: %(1)s\n" % {"1": re.sub("\n", "", contentO[x[0]])})
            text_file.write("Answer: %(1)s\n" % {"1": re.sub("\n", "", x[1].encode('utf-8'))})
            text_file.write("------------------------------------------\n")

        print("Results saved to: %(1)s:" % {"1":fileToWrite})

runTest()