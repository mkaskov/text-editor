#! /usr/bin/env python
# -*- coding: utf-8 -*-
# by Max8mk

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from flask import Flask
from flask import request, jsonify
from cStringIO import StringIO

import urllib
import re

app = Flask(__name__)

#to-do rename methods
@app.route('/decode_sentense', methods=['POST'])
def decode_sentense():
  query = request.json['query']
  sentences = splitter_with_prepare(query)
  answer = batch_recognition(sentences)
  prepare_for_database(query)
  return jsonify(answer=answer)

def prepare_for_database(source):
    sentences = splitter_with_prepare(source)
    sentences = [text_ttp_special_decode(s) for s in sentences]
    return sentences

def splitter_with_prepare(source):
  source = decode_from_java(source)
  source = text_ttp_special_encode(source)
  sentences = []
  SPLIT = re.compile("\. |\n")
  sentences.extend(re.split(SPLIT, source))
  return [s.encode('utf8') for s in sentences if s != '. ' and s !='' and s!='[newline]']

def batch_recognition(sentences):
    answer = StringIO()
    answer.truncate(0)
    for s in sentences:
        [answer.write('\n') if '[newline]' in s else answer.write('')]
        s = text_ttp_special_decode(s)
        answer.write(recognition(s))
    return answer.getvalue().strip()

def text_ttp_special_encode(text):
    return text.replace('\n','\n[newline]').replace('...','[threedot]').replace('. ', '[dot]. ')

def text_ttp_special_decode(text):
    return text.replace('[newline]', '').replace('[threedot]','...').replace('[dot]', '. ')

def decode_from_java(source):
  return urllib.unquote(source.encode('utf8')).decode('utf-8')

def recognition(sentence):
  return sentence

def printArr(array):
    [print(e) for e in array]

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5003, debug=True, use_reloader=False, threaded=True)
