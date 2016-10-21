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

from nnet import initialization, core
from util import textUtil as tU

import docker_prepare

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
  FLAGS, _TTP_WORD_SPLIT, _buckets, app_options = initialization.getParams()
  if app_options["fixdataset"]: docker_prepare.fix_dataset()
  core = core.Core(FLAGS, _TTP_WORD_SPLIT, _buckets, app_options)
  app.run(host='0.0.0.0', port=FLAGS.port, debug=True, use_reloader=False, threaded=True)
