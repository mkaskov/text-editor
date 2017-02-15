#! /usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import urllib2, json
import os
import sys
import re
import datetime

fileDir = "/home/user/datasets/construction_text_base/071016/"
fileInput = "dev-data.input"
fileOutput =  "dev-data.output"
storeOutput = "/home/user/datasets/construction_text_base/tests/"
url = 'http://server.puremind.tech:5002/decode_sentense'
linesNum = 100 #number of lines for test
buckets = [(5, 5),(10, 10), (30, 30), (50, 50), (70, 70), (100,100)]
regex = u'\[_K_\]|\[_At_\]|\[\|\|\]|\[\/K\]|\[K\]|\[At\]|\[\/At\]|гост\s[\d.]+—?\-?[\d]+|ГОСТ\s[\d.]+—?\-?[\d]+|[а-яА-Я]+\/[а-яА-Я\d]+\.{1}[а-яА-Я\d]+\.{1}|[а-яА-Я]+\/\([^()]+\)|[^\s\d.,!?():;/\\|<>\"\'=–—\-+_*\xA0IV\[\]≥≤~”“_ₒ∙°··\x23«»]+\d?\/[^\s.,!?():;/\\|<>\"\'=–—\-+_*\xA0IV\[\]≥≤~”“_ₒ∙°··\x23«»]+|м{1,2}[\d⁰¹²³⁴⁵⁶⁷⁸⁹]|см[\d⁰¹²³⁴⁵⁶⁷⁸⁹]|дм[\d⁰¹²³⁴⁵⁶⁷⁸⁹]|[a-zA-Zа-яА-ЯёЁ]*[^\s\d.\\!?,:;()\"\'<>%«»±^…–—\-*=/+\xA0@·∙\[\]°ₒ”“·≥≤~_\x23]|[\d()\\!?\'\"<>%,:;±«»^…–—\-*=/+@·∙\[\]°ₒ”“·≥≤~_\x23]|\.{3}|\.{1}'
WORD_SPLIT = re.compile(regex)

def lenofSentence(t):
  source = re.sub("[\s\xA0]+", " ", t).strip()
  words = re.findall(WORD_SPLIT, source)
  return len(words)

def runTest():

    if not os.path.isfile(fileDir + fileInput) or not os.path.isfile(fileDir + fileOutput):
        print ("No input or output data")
        sys.exit(0)

    count = 0
    errosArray = []
    rightArray = []
    bucketTotal = []
    bucketRight = []

    startTime = datetime.datetime.now()
    fileToWrite=storeOutput+"test_"+datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")+".txt"

    with open(fileToWrite, "w") as text_file:
        with open(fileDir + fileInput) as fi:
            with open(fileDir + fileOutput) as fo:
                contentI = fi.readlines()[0:linesNum]
                contentO = fo.readlines()[0:linesNum]

                inLinesLen = []
                print ("[WARNING] check bucket and regex parameters")
                print("Start processing")

                for line in contentI:
                    inLinesLen.append(lenofSentence(line))

                for id,bucket in enumerate(buckets):
                    currBucketCount = 0
                    for elem in inLinesLen:
                        if elem>buckets[id-1][0]-1 and elem<=bucket[0]-1: currBucketCount+=1
                    bucketTotal.append(currBucketCount)
                    bucketRight.append([])

                for row in enumerate(contentI):
                    count+=1
                    if count % (linesNum/10) == 0: print ("Processing:",count/(linesNum/100),"%")
                    postdata = {'query': row[1]}
                    req = urllib2.Request(url)
                    req.add_header('Content-Type', 'application/json')
                    data = json.dumps(postdata)

                    response = urllib2.urlopen(req, data)

                    answer = json.load(response)

                    if re.sub("[\s\xA0]+", "", answer['answer']).lower()!=re.sub("[\s\xA0]+", "", contentO[row[0]]).lower(): errosArray.append((row[0],answer['answer']))
                    else:
                        currLen = inLinesLen[row[0]]
                        for id, bucket in enumerate(buckets):
                            if currLen > buckets[id - 1][1] - 1 and currLen <= bucket[1] - 1:
                                bucketRight[id].append(currLen)

                        rightArray.append((row[0], answer['answer']))

                print ("Errors:",len(errosArray),"/",linesNum)
                print ("Errors:",100*len(errosArray)/linesNum,"%")

        endTime = datetime.datetime.now()
        totalTime = endTime - startTime

        text_file.write("[Input data --------------------------------------------------]\n\n")
        text_file.write("Input file: %s\n" % fileDir + fileInput)
        text_file.write("Output file: %s\n" % fileDir + fileOutput)
        text_file.write("Start time: %s\n" % startTime.strftime("%Y-%m-%d %H:%M"))
        text_file.write("End time: %s\n" % endTime.strftime("%Y-%m-%d %H:%M"))

        text_file.write("Total time: %s\n" % str(totalTime))

        text_file.write("\n[Init params------------------------------------------------]\n\n")
        text_file.write("Buckets: %s\n" % str(buckets))
        text_file.write("Regex: %s\n" % regex)

        text_file.write("\n[Stats -------------------------------------------------------]\n\n")
        text_file.write("Total lines: %s\n" % linesNum)
        text_file.write("Right answers: %s\n" % len(rightArray))
        text_file.write("Error answers: %s\n" % len(errosArray))

        text_file.write("\n[Buckets------------------------------------------------------]\n")
        for id,bucket in enumerate(buckets):
            text_file.write(
                "\nBuckets "+ str(bucket)+ " right: " + str(len(bucketRight[id]))+ "/"+ str(bucketTotal[id])
            )

        text_file.write("\n\n[Section with right answers ----------------------------------]\n\n")
        for x in rightArray:
            text_file.write("Sentence id: " + str([x[0]]) + "\n")
            text_file.write("Token length of input sentence: " + str(inLinesLen[x[0]])+"\n")
            text_file.write("Input : %(1)s\n" % {"1": re.sub("\n", "", contentI[x[0]])})
            text_file.write("Answer: %(1)s\n" % {"1": re.sub("\n", "", x[1])})
            text_file.write("\n------------------------------------------\n\n")

        text_file.write("\n[Section with errors------------------------------------------]\n\n")
        for x in errosArray:
            text_file.write("Sentence id: " + str([x[0]]) + "\n")
            text_file.write("Token length of input sentence: " + str(inLinesLen[x[0]]) + "\n")
            text_file.write("Input : %(1)s\n" % {"1": re.sub("\n", "", contentI[x[0]])})
            text_file.write("Output: %(1)s\n" % {"1": re.sub("\n", "", contentO[x[0]])})
            text_file.write("Answer: %(1)s\n" % {"1": re.sub("\n", "", x[1])})
            text_file.write("\n------------------------------------------\n\n")

        print("Results saved to: %(1)s:" % {"1":fileToWrite})

runTest()