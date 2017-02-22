#! /usr/bin/env python
import errno
import urllib2, json
import os
import re
import datetime

filePath = '../collectData/collectNerData.txt'
url = 'http://localhost:5003/ner/parse/search'

def get_entity_array():
    with open(filePath) as fi:
        fullStr = "".join([x for x in fi.readlines()])
        retValue = re.split("\[line\]", fullStr)
        return [x for x in retValue if len(x) > 0]

if not os.path.isfile(filePath):
    print ("No input or output data")
    exit(errno.EFAULT)

entityArray = get_entity_array()

totalEntity = 0
totalAnswered = 0

entityDataLen = len(entityArray)
currentEntityDataNum = 0

for entity in entityArray:
    postdata = {'query': entity}
    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/json')
    data = json.dumps(postdata)
    response = urllib2.urlopen(req, data)
    answer = json.load(response)['answer']
    entityData = json.loads(answer)['entity']
    totalEntity += len(entityData)
    for subEntity in entityData:
        if len(subEntity['answer'])>0:
            totalAnswered+=1

    currentEntityDataNum+=1
    print ("progress:",100*(float(currentEntityDataNum)/(entityDataLen)),"answered_prc:",100*(float(totalAnswered)/(totalEntity)))

if not os.path.exists("../testResults"):
    os.makedirs("../testResults")
with open("../testResults/resultsNerFullTest.txt", "a") as text_file:
    text_file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")+" [total]: " + str(totalEntity) + " [answered]: "+ str(totalAnswered) + ' result: '+ str(100*(float(totalAnswered)/(totalEntity))) +" %"+ "\n")