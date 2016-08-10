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

from flask import Flask
from flask import request, jsonify

import os

import numpy as np
from six.moves import xrange  # pylint: disable=redefined-builtin
import tensorflow as tf

import data_utils
import seq2seq_model
import util.textUtil as textUtil
from cStringIO import StringIO

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

FLAGS = tf.app.flags.FLAGS

# We use a number of buckets and pad to the closest one for efficiency.
# See seq2seq_model.Seq2SeqModel for details of how they work.
# _buckets = [(5, 10), (10, 15), (20, 25), (40, 50),(50, 60),(60,70),(70,80),(80,90),(90,100)] # Это зачем?
_buckets = [(5, 10), (10, 15), (30, 35), (50, 60), (90, 100)]


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
        [answer.write('\n') if '[newline]' in s else answer.write('')]
        s = textUtil.prepare_decode(s)
        answer.write(recognition(s))
    return answer.getvalue().strip()

def recognition(sentence):
  token_ids = data_utils.sentence_to_token_ids(sentence, in_vocab, normalize_digits=False) # Get token-ids for the input sentence.

  #для справки выводим токены введёного текста
  print("Input sentence:")
  print(sentence)
  print(token_ids)
  
  # Which bucket does it belong to?
  detect_bucket_array = [b for b in xrange(len(_buckets)) if _buckets[b][0] > len(token_ids)]
  bucket_id = min(detect_bucket_array) if len(detect_bucket_array)>0 else len(_buckets)-1
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
  
  return retValue.encode('utf8')

def onstart():
  #Создаем глобальные переменные (сессия тенсорфлоу и обрабатывающая модель)
  global sess
  
  # Выделение видеопамяти на процесс 20%
  gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.20)
  sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))
  #sess = tf.Session()
  
  global model

  # Создаем модель и загружаем параметры
  print("Load model")
  model = create_model(sess, True)
  model.batch_size = 1  # We decode one sentence at a time.

if __name__ == "__main__":
  onstart()
  app.run(host='0.0.0.0', port=5002, debug=True, use_reloader=False, threaded=True) #новый порт, чтобы обращаться к нему из веб-приложения, запущенного на JAVA
