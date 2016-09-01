#! /usr/bin/env python
# -*- coding: utf-8 -*-
# by Max8mk

"""ONLY for start app flask for web decoding data.

Директория с данными --data_dir 
Директория с обученной моделью --train_dir.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from cStringIO import StringIO

from flask import Flask
from flask import request, jsonify

from util import textUtil as tU
import core as Core
import initialization

# Obtain the flask app object
app = Flask(__name__)

global core

@app.route('/decode_sentense', methods=['POST'])
def decode_sentense():
  q = request.json['query']
  return jsonify(answer=batch_recognition(tU.sent_splitter(q)))

def batch_recognition(sentences):
    answer = StringIO()
    answer.truncate(0)
    for s in sentences:
        if '[newline]' in s: answer.write('\n')
        s = tU.prepare_decode(s)
        if '[OL]' in s or '[UL]' in s: answer.write(s)
        else:
            if '[LI]' in s: answer.write('[LI]'); s = s[4:]
            print ("------------------------------- Start recogintion -----------------------------------------")
            outputs, rev_out_vocab =  core.recognition(s)
            orig_val = (" ".join([rev_out_vocab[output] for output in outputs])).decode("utf-8")
            print("Output sentence: ", orig_val)
            s = tU.buildRetValue(outputs, rev_out_vocab)
            s = tU.removeSpaces(s)
            print("Final sentence: ", s)
            answer.write(s)
            answer.write(' ')
    return answer.getvalue().strip()

if __name__ == "__main__":
  FLAGS,_TTP_WORD_SPLIT,_buckets = initialization.getParams()
  core = Core.Core(FLAGS,_TTP_WORD_SPLIT,_buckets,web=True,reduce_gpu=True,forward_only = True)
  app.run(host='0.0.0.0', port=FLAGS.port, debug=True, use_reloader=False, threaded=True)
