#! /usr/bin/env python
# -*- coding: utf-8 -*-
# by Max8mk

"""ONLY for start app flask for web decoding data.
It start public server on port 5001

Директория с данными --data_dir 
Директория с обученной моделью --train_dir.

See the following papers for more information on neural translation models.
 * http://arxiv.org/abs/1409.3215
 * http://arxiv.org/abs/1409.0473
 * http://arxiv.org/abs/1412.2007
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from cStringIO import StringIO

import numpy as np
import tensorflow as tf
from flask import Flask
from flask import request, jsonify
from six.moves import xrange  # pylint: disable=redefined-builtin

from nnet import data_utils, seq2seq_model
from util import textUtil, ttpSettings
import core

# Obtain the flask app object
app = Flask(__name__)

# by default as translate model
tf.app.flags.DEFINE_float("learning_rate", 0.5, "Learning rate.")
tf.app.flags.DEFINE_float("learning_rate_decay_factor", 0.99,
                          "Learning rate decays by this much.")
tf.app.flags.DEFINE_float("max_gradient_norm", 5.0,
                          "Clip gradients to this norm.")
tf.app.flags.DEFINE_integer("batch_size", 64,
                            "Batch size to use during training.")
tf.app.flags.DEFINE_integer("size", 512, "Size of each model layer.")
tf.app.flags.DEFINE_integer("num_layers", 3, "Number of layers in the model.")
tf.app.flags.DEFINE_integer("in_vocab_size", 40000, "INPUT vocabulary size.")
tf.app.flags.DEFINE_integer("out_vocab_size", 40000, "OUTPUT vocabulary size.")
tf.app.flags.DEFINE_string("data_dir", "/tmp", "Data directory")
tf.app.flags.DEFINE_string("train_dir", "/tmp", "Training directory.")
tf.app.flags.DEFINE_integer("max_train_data_size", 0,
                            "Limit on the size of training data (0: no limit).")
tf.app.flags.DEFINE_integer("steps_per_checkpoint", 200,
                            "How many training steps to do per checkpoint.")
tf.app.flags.DEFINE_boolean("web_decode", True,
                            "Set to True for interactive decoding into web.")
tf.app.flags.DEFINE_integer("port", 5002,
                            "default port.")

FLAGS = tf.app.flags.FLAGS

global core

@app.route('/decode_sentense', methods=['POST'])  # метод через json, принимает запросы в виде строки от клиента
def decode_sentense():

  query = request.json['query']
  sentences = textUtil.sent_splitter(query)
  answer = batch_recognition(sentences)

  return jsonify(answer=answer)

def batch_recognition(sentences):
    answer = StringIO()
    answer.truncate(0)
    for s in sentences:
        if '[newline]' in s: answer.write('\n')
        s = textUtil.prepare_decode(s)
        if '[OL]' in s or '[UL]' in s: answer.write(s)
        else:
            if '[LI]' in s: answer.write('[LI]'); s = s[4:]
            print ("------------------------------- Start recogintion -----------------------------------------")
            outputs, rev_out_vocab =  core.recognition(s)
            orig_val = (" ".join([rev_out_vocab[output] for output in outputs])).decode("utf-8")
            print("Output sentence: ", orig_val)
            s = textUtil.buildRetValue(outputs, rev_out_vocab)
            s = textUtil.removeSpaces(s)
            print("Final sentence: ", s)
            answer.write(s)
            answer.write(' ')
    return answer.getvalue().strip()

if __name__ == "__main__":
  # onstart()
  core = core.Core(FLAGS)
  app.run(host='0.0.0.0', port=FLAGS.port, debug=True, use_reloader=False, threaded=True)
