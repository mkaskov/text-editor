#! /usr/bin/env python
# -*- coding: utf-8 -*-
# by Max8mk

"""ONLY for start app flask for web decoding data.
It start public server on port 5001

Директория с данными --data_dir 
директория с результатами обучения --train_dir.

See the following papers for more information on neural translation models.
 * http://arxiv.org/abs/1409.3215
 * http://arxiv.org/abs/1409.0473
 * http://arxiv.org/abs/1412.2007
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from flask import Flask
from flask import render_template
from flask import request, jsonify

import math
import os
import random
import sys
import time
import re

import numpy as np
from six.moves import xrange  # pylint: disable=redefined-builtin
import tensorflow as tf

import data_utils
import seq2seq_model

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
tf.app.flags.DEFINE_integer("size", 1024, "Size of each model layer.")
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

FLAGS = tf.app.flags.FLAGS

# We use a number of buckets and pad to the closest one for efficiency.
# See seq2seq_model.Seq2SeqModel for details of how they work.
# _buckets = [(5, 10), (10, 15), (20, 25), (40, 50),(50, 60),(60,70),(70,80),(80,90),(90,100)] # Это зачем?
_buckets = [(5, 10), (10, 15), (30, 35), (50, 60)]


# Load vocabularies.
in_vocab_path = os.path.join(FLAGS.data_dir, "vocab%d.input" % FLAGS.in_vocab_size)
out_vocab_path = os.path.join(FLAGS.data_dir, "vocab%d.output" % FLAGS.out_vocab_size)
in_vocab, _ = data_utils.initialize_vocabulary(in_vocab_path)
_, rev_out_vocab = data_utils.initialize_vocabulary(out_vocab_path)


def create_model(session, forward_only):
  """Initialize model or load parameters in session."""
  # with tf.device('/cpu:0'):
  model = seq2seq_model.Seq2SeqModel(
      FLAGS.in_vocab_size, FLAGS.out_vocab_size, _buckets,
      FLAGS.size, FLAGS.num_layers, FLAGS.max_gradient_norm, FLAGS.batch_size,
      FLAGS.learning_rate, FLAGS.learning_rate_decay_factor,
      forward_only=forward_only)
  ckpt = tf.train.get_checkpoint_state(FLAGS.train_dir)
  if ckpt and tf.gfile.Exists(ckpt.model_checkpoint_path):
    print("Reading model parameters from %s" % ckpt.model_checkpoint_path)
    model.saver.restore(session, ckpt.model_checkpoint_path)
  else:
      print("Error! No model to load!")
  return model

@app.route('/')
def index():
    return render_template("index.html")   
          
@app.route('/decode', methods=['POST'])  # метод через json, принимает запросы в виде массива от клиента  
def decode():
  content = request.json
  retValue =[]
  
   # Подготовка абзаца текста к распознованию, разбиваем на предложения 
 # tempSentArray = []
 # tempSentArray = re.split('\. ', elem['col3']) # необходимо будет переделать паттерн для определения предложений, от этого зависит качество распознаваемого предложения
 # tempNewSentense = ""
 
 # Прогон разбитого предложения через декодер
 # for sentElem in tempSentArray:
  # if len(sentElem.strip())>0:
   # tempNewSentense += web_decode(sentElem) 
  
  
  for elem in content: 
   tempSentArray = [] 
   for inputElem in elem['data']:
    tempSentArray.append(web_decode(inputElem['input']))
   tempElem = {"out":tempSentArray}
   retValue.append(tempElem)
  
  return jsonify(answer=retValue)

@app.route('/decode_sentense', methods=['POST'])  # метод через json, принимает запросы в виде строки от клиента  
def decode_sentense():
  content = request.json
  return jsonify(answer=web_decode(content['query']))  
  
def web_decode(sentence):
  # with tf.Session() as sess: //// метод try catch, здесь не используется,так как необходимы глобальные переменные на приложение
    
  sentence = sentence.encode('utf8') #сначала надо перекодировать в utf-8 приходящий запрос, потому что словарь записан в этом формате
  token_ids = data_utils.sentence_to_token_ids(sentence, in_vocab, normalize_digits=False) # Get token-ids for the input sentence.
  #для справки выводим токены введёного текста
  print("Input sentence:")
  print(sentence)
  print(token_ids)
  
  # Which bucket does it belong to?
  bucket_id = min([b for b in xrange(len(_buckets))
                     if _buckets[b][0] > len(token_ids)])
  # Get a 1-element batch to feed the sentence to the model.
  encoder_inputs, decoder_inputs, target_weights = model.get_batch(
        {bucket_id: [(token_ids, [])]}, bucket_id)
  # Get output logits for the sentence.
  _, _, output_logits = model.step(sess, encoder_inputs, decoder_inputs,
                                     target_weights, bucket_id, True)
  # This is a greedy decoder - outputs are just argmaxes of output_logits.
  outputs = [int(np.argmax(logit, axis=1)) for logit in output_logits]
  # If there is an EOS symbol in outputs, cut them at that point.
  if data_utils.EOS_ID in outputs:
      outputs = outputs[:outputs.index(data_utils.EOS_ID)]
  
  # Print out OUTPUT sentence corresponding to outputs.
  retValue = (" ".join([rev_out_vocab[output] for output in outputs])).decode("utf-8")
  print("Output sentence:")
  print(retValue)
  
  return retValue # будем например возвращать декодированную фразу в виде строки

def onstart():
  #Создаем глобальные переменные (сессия тенсорфлоу и обрабатывающая модель)
  global sess
  sess = tf.Session()
  global model
  # with tf.Session() as sess: //// метод try catch, здесь не используется,так как необходимы глобальные переменные на приложение

  # Create model and load parameters.
  print("Load model")
  model = create_model(sess, True)
  model.batch_size = 1  # We decode one sentence at a time.
    

if __name__ == "__main__":
  onstart()
  app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False,threaded=True)