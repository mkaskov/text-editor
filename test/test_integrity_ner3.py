#! /usr/bin/env python
# Puremind.tech

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import urllib2, json
import os
import sys
import re
import datetime

_test_file =  "/home/user/datasets/construction_text_base/test_sentences.txt"
_test_file_result =  "/home/user/datasets/construction_text_base/test_sentences_result.txt"
_url = 'http://server.puremind.tech:5003/decode_sentense'
lines_Num = 5

def run_test():

    count_right = 0
    wrong_rows = []
    linesNum = 0

    with open(_test_file, "r") as text_file:
       text_arr =  text_file.readlines()#[0:lines_Num]
       linesNum = len(text_arr)

       for i,item in enumerate(text_arr):

           postdata = {'query': item}
           req = urllib2.Request(_url)
           req.add_header('Content-Type', 'application/json')
           data = json.dumps(postdata)

           response = urllib2.urlopen(req, data)

           answer = json.load(response)

           if answer['_integrity']:
               count_right +=1
           else:
               wrong_rows.append(i+1)

           print ('Total progress',((i+1)/linesNum)*100,'%')

    print ('Total right answers',count_right,'/',linesNum)
    print ('Right',(count_right/linesNum)*100,'%')

    if len(wrong_rows)>0:
        print ('Wrong rows:',len(wrong_rows))
        print (wrong_rows)

    with open(_test_file_result, "a") as text_file_result:
        arrayStr = ",".join(map(str, wrong_rows))
        text_file_result.write("\n"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M")+" "+'Total right answers '+str(count_right)+'/'+str(linesNum)+" "+'Right '+str((count_right/linesNum)*100)+'%'+" "+'Wrong rows:'+str(len(wrong_rows))+" -- "+str(arrayStr))
        print ("[DONE] results saved to",_test_file_result)
run_test()