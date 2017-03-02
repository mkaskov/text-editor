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

# entityArray = entityArray[0:1]

_total = len(entityArray)

_entity = 0
_answered = 0

_index = 0
_resolved = 0
_inregrity = 0

for entity in entityArray:
    postdata = {'query': entity}
    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/json')
    data = json.dumps(postdata)
    response = urllib2.urlopen(req, data)
    answer = json.load(response)['answer']

    _index += 1

    if json.loads(answer)["_resolved"]:
        _resolved +=1

    if json.loads(answer)["_integrity"]:
        _inregrity +=1
    else:
        print ("not inregrity",_index)

    entityData = json.loads(answer)['entity']
    _entity += len(entityData)
    for subEntity in entityData:
        if len(subEntity['answer'])>0:
            _answered+=1

    print ("progress:", 100 * (float(_index) / (_total)), "answered_prc:", 100 * (float(_answered) / (_entity)))

if not os.path.exists("../testResults"):
    os.makedirs("../testResults")
with open("../testResults/resultsNerFullTest.txt", "a") as text_file:
    text_file.write(
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        + " [total]: " + str(_entity)
        + " [answered]: " + str(_answered)
        + " [answered prc]: " + str(100 * (float(_answered) / (_entity)))[0:5] + " %"
        + " [entries]: " + str(_total)
        + " [resolved]: " + str(_resolved)
        + " [resolved prc]: " + str(100 * (float(_resolved) / _total))[0:5] + " %"
        + " [integrity]: " + str(_inregrity)
        + " [inregrity prc]: " + str(100 * (float(_inregrity) / _total))[0:5] + " %"
        + "\n")