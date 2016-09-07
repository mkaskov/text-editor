#! /usr/bin/env python
# -*- coding: utf-8 -*-

# by Max8mk
"""Binary for training editor models and decoding from them.

Running this program without --decode will enter into --data_dir
and tokenize data in a very basic way,
and then start training a model saving checkpoints to --train_dir.

Running with --decode starts an interactive loop so you can see how
the current checkpoint editor works.

See the following papers for more information on neural translation models.
 * http://arxiv.org/abs/1409.3215
 * http://arxiv.org/abs/1409.0473
 * http://arxiv.org/abs/1412.2007
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from nnet import data_utils, seq2seq_model
import tensorflow as tf
import numpy as np

import math
import random
import sys
import time
import datetime

from six.moves import xrange  # pylint: disable=redefined-builtin

class Unbuffered:

   def __init__(self, stream): self.stream = stream

   def write(self, data):
       if isinstance(data, unicode): data=data.encode('utf-8')
       self.stream.write(data)
       self.stream.flush()

   def flush(self): pass

class Core(object):

    global FLAGS
    global sess
    global model
    global in_vocab_path
    global in_vocab
    global out_vocab_path
    global rev_out_vocab
    global _TTP_WORD_SPLIT

    # We use a number of buckets and pad to the closest one for efficiency.
    # See seq2seq_model.Seq2SeqModel for details of how they work.
    global _buckets

    def __init__(self,FLAGS,_TTP_WORD_SPLIT,_buckets,web=False,reduce_gpu=False,forward_only = False):
        sys.stdout = Unbuffered(sys.stdout)
        self.FLAGS = FLAGS
        self._buckets = _buckets
        self._TTP_WORD_SPLIT = _TTP_WORD_SPLIT
        self.sess = None
        self.in_vocab_path = None
        self.out_vocab_path = None
        self.in_vocab = None
        self.rev_out_vocab = None

        self.printStartParams (FLAGS,_TTP_WORD_SPLIT,_buckets,web,reduce_gpu,forward_only)

        # Выделение видеопамяти на процесс 20%
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.20)

        if reduce_gpu: self.sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))
        else: self.sess = tf.Session()

        if web:
            self.in_vocab_path = os.path.join(FLAGS.data_dir, "vocab%d.input" % FLAGS.in_vocab_size)
            self.out_vocab_path = os.path.join(FLAGS.data_dir, "vocab%d.output" % FLAGS.out_vocab_size)
            self.in_vocab, _ = data_utils.initialize_vocabulary(self.in_vocab_path)
            _, self.rev_out_vocab = data_utils.initialize_vocabulary(self.out_vocab_path)

        # Создаем модель и загружаем параметры
        print("Creating %d layers of %d units." % (FLAGS.num_layers, FLAGS.size))
        self.model = self.create_model(self.sess, forward_only)
        if web: self.model.batch_size = 1  # We decode one sentence at a time.

    def printStartParams(self,FLAGS,_TTP_WORD_SPLIT,_buckets,web,reduce_gpu,forward_only):
        print("------------------------Starting----------------------------------------------------------------")
        print("Current date and time: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        print ("------------------------Start parameters of neural network--------------------------------------")

        if web:
            print ("Mode: web mode")
            print ("Port:",FLAGS.port)
        else: print ("Mode: train mode")

        if forward_only: print ("forward only: true")
        else: print ("forward only: false")

        print ("Buckets: ",_buckets)

        print ("RegEx patter: ", _TTP_WORD_SPLIT.pattern)

        print ("Learning rate: ", FLAGS.learning_rate)

        print("learning_rate_decay_factor: ", FLAGS.learning_rate_decay_factor)

        print("max_gradient_norm: ", FLAGS.max_gradient_norm)

        print("batch_size: ", FLAGS.batch_size)

        print("num_layers: ", FLAGS.num_layers)

        print("size: ", FLAGS.size)

        print("in_vocab_size: ", FLAGS.in_vocab_size)

        print("out_vocab_size: ", FLAGS.out_vocab_size)

        print("data_dir: ", FLAGS.data_dir)

        print("train_dir: ", FLAGS.train_dir)

        print("max_train_data_size: ", FLAGS.max_train_data_size)

        print("steps_per_checkpoint: ", FLAGS.steps_per_checkpoint)

        print("decode mode: ", FLAGS.decode)

        print("self_test mode: ", FLAGS.self_test)

        print("reduce gpu usage: ", reduce_gpu)

        print ("------------------------------------------------------------------------------------------------")

    def create_model(self,session, forward_only):
      FLAGS=self.FLAGS
      _buckets = self._buckets

      """Create model and initialize or load parameters in session."""
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
        print("Created model with fresh parameters.")
        session.run(tf.initialize_all_variables())
      return model

    def recognition(self,sentence):
        _buckets = self._buckets
        in_vocab = self.in_vocab
        rev_out_vocab = self.rev_out_vocab
        sess = self.sess
        model = self.model
        _TTP_WORD_SPLIT = self._TTP_WORD_SPLIT

        token_ids = data_utils.sentence_to_token_ids(sentence, in_vocab, normalize_digits=False,ext_TTP_WORD_SPLIT=_TTP_WORD_SPLIT)  # Get token-ids for the input sentence.

        # для справки выводим токены введёного текста
        print("Input sentence: ", sentence)
        print('Tokens: ', token_ids)

        # Which bucket does it belong to?
        detect_bucket_array = [b for b in xrange(len(_buckets)) if _buckets[b][0] > len(token_ids)]
        bucket_id = min(detect_bucket_array) if len(detect_bucket_array) > 0 else len(_buckets) - 1
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

        return outputs, rev_out_vocab

    def read_data(self,source_path, target_path, max_size=None):
        _buckets = self._buckets
        """Read data from source and target files and put into buckets.

        Args:
          source_path: path to the files with token-ids for the source language.
          target_path: path to the file with token-ids for the target language;
            it must be aligned with the source file: n-th line contains the desired
            output for n-th line from the source_path.
          max_size: maximum number of lines to read, all other will be ignored;
            if 0 or None, data files will be read completely (no limit).

        Returns:
          data_set: a list of length len(_buckets); data_set[n] contains a list of
            (source, target) pairs read from the provided data files that fit
            into the n-th bucket, i.e., such that len(source) < _buckets[n][0] and
            len(target) < _buckets[n][1]; source and target are lists of token-ids.
        """
        data_set = [[] for _ in _buckets]
        with tf.gfile.GFile(source_path, mode="r") as source_file:
            with tf.gfile.GFile(target_path, mode="r") as target_file:
                source, target = source_file.readline(), target_file.readline()
                counter = 0
                while source and target and (not max_size or counter < max_size):
                    counter += 1
                    if counter % 100000 == 0:
                        print("  reading data line %d" % counter)
                        sys.stdout.flush()
                    source_ids = [int(x) for x in source.split()]
                    target_ids = [int(x) for x in target.split()]
                    target_ids.append(data_utils.EOS_ID)
                    for bucket_id, (source_size, target_size) in enumerate(_buckets):
                        if len(source_ids) < source_size and len(target_ids) < target_size:
                            data_set[bucket_id].append([source_ids, target_ids])
                            break
                    source, target = source_file.readline(), target_file.readline()
                print("------------------------------------------------------------------------------------------------")
                print("Total lines: ", counter)
                print("------------------------------------------------------------------------------------------------")
        return data_set

    def train(self):
        FLAGS = self.FLAGS
        _buckets = self._buckets
        model = self.model
        sess = self.sess
        _TTP_WORD_SPLIT = self._TTP_WORD_SPLIT

        # """Train a INPUT->OUTPUT editor model."""
        # Prepare data.
        print("Preparing data in %s" % FLAGS.data_dir)
        in_train, out_train, in_dev, out_dev, _, _ = data_utils.prepare_data(
            FLAGS.data_dir, FLAGS.in_vocab_size, FLAGS.out_vocab_size,_TTP_WORD_SPLIT)

        # Read data into buckets and compute their sizes.
        print("Reading development and training data (limit: %d)."
              % FLAGS.max_train_data_size)
        dev_set = self.read_data(in_dev, out_dev)
        train_set = self.read_data(in_train, out_train, FLAGS.max_train_data_size)
        train_bucket_sizes = [len(train_set[b]) for b in xrange(len(_buckets))]
        train_total_size = float(sum(train_bucket_sizes))

        print("------------------------------------------------------------------------------------------------")
        print("bucket sizes")
        print(train_bucket_sizes)
        print("train total size")
        print(train_total_size)
        print("------------------------------------------------------------------------------------------------")

        # A bucket scale is a list of increasing numbers from 0 to 1 that we'll use
        # to select a bucket. Length of [scale[i], scale[i+1]] is proportional to
        # the size if i-th training bucket, as used later.
        train_buckets_scale = [sum(train_bucket_sizes[:i + 1]) / train_total_size
                               for i in xrange(len(train_bucket_sizes))]

        # This is the training loop.
        step_time, loss = 0.0, 0.0
        current_step = 0
        previous_losses = []
        while True:
            # Choose a bucket according to data distribution. We pick a random number
            # in [0, 1] and use the corresponding interval in train_buckets_scale.
            random_number_01 = np.random.random_sample()
            bucket_id = min([i for i in xrange(len(train_buckets_scale))
                             if train_buckets_scale[i] > random_number_01])

            # Get a batch and make a step.
            start_time = time.time()
            encoder_inputs, decoder_inputs, target_weights = model.get_batch(
                train_set, bucket_id)
            _, step_loss, _ = model.step(sess, encoder_inputs, decoder_inputs,
                                         target_weights, bucket_id, False)
            step_time += (time.time() - start_time) / FLAGS.steps_per_checkpoint
            loss += step_loss / FLAGS.steps_per_checkpoint
            current_step += 1

            # Once in a while, we save checkpoint, print statistics, and run evals.
            if current_step % FLAGS.steps_per_checkpoint == 0:
                # Print statistics for the previous epoch.
                perplexity = math.exp(loss) if loss < 300 else float('inf')
                print("global step %d learning rate %.4f step-time %.2f perplexity "
                      "%.2f" % (model.global_step.eval(sess), model.learning_rate.eval(sess),
                                step_time, perplexity))
                # Decrease learning rate if no improvement was seen over last 3 times.
                if len(previous_losses) > 2 and loss > max(previous_losses[-3:]):
                    sess.run(model.learning_rate_decay_op)
                previous_losses.append(loss)
                # Save checkpoint and zero timer and loss.
                checkpoint_path = os.path.join(FLAGS.train_dir, "editor.ckpt")
                model.saver.save(sess, checkpoint_path, global_step=model.global_step)
                step_time, loss = 0.0, 0.0
                # Run evals on development set and print their perplexity.
                for bucket_id in xrange(len(_buckets)):
                    encoder_inputs, decoder_inputs, target_weights = model.get_batch(
                        dev_set, bucket_id)
                    _, eval_loss, _ = model.step(sess, encoder_inputs, decoder_inputs,
                                                 target_weights, bucket_id, True)
                    eval_ppx = math.exp(eval_loss) if eval_loss < 300 else float('inf')
                    print("  eval: bucket %d perplexity %.2f" % (bucket_id, eval_ppx))
                sys.stdout.flush()

    def decode(self):
        sess = self.sess
        model = self.model
        FLAGS = self.FLAGS
        _buckets = self._buckets
        _TTP_WORD_SPLIT = self._TTP_WORD_SPLIT

        # Load vocabularies.
        in_vocab_path = os.path.join(FLAGS.data_dir,
                                     "vocab%d.input" % FLAGS.in_vocab_size)
        out_vocab_path = os.path.join(FLAGS.data_dir,
                                      "vocab%d.output" % FLAGS.out_vocab_size)
        in_vocab, _ = data_utils.initialize_vocabulary(in_vocab_path)
        _, rev_out_vocab = data_utils.initialize_vocabulary(out_vocab_path)

        # Decode from standard input.
        sys.stdout.write("> ")
        sys.stdout.flush()
        sentence = sys.stdin.readline()
        while sentence:
            # Get token-ids for the input sentence.
            token_ids = data_utils.sentence_to_token_ids(sentence, in_vocab, normalize_digits=False,ext_TTP_WORD_SPLIT=_TTP_WORD_SPLIT)
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
            print((" ".join([rev_out_vocab[output] for output in outputs])).decode("utf-8"))
            print("> ", end="")
            sys.stdout.flush()
            sentence = sys.stdin.readline()

    def self_test(self):
        sess = self.sess

        print("Self-test for neural editor model.")
        # Create model with vocabularies of 10, 2 small buckets, 2 layers of 32.
        model = seq2seq_model.Seq2SeqModel(10, 10, [(3, 3), (6, 6)], 32, 2,
                                           5.0, 32, 0.3, 0.99, num_samples=8)
        sess.run(tf.initialize_all_variables())

        # Fake data set for both the (3, 3) and (6, 6) bucket.
        data_set = ([([1, 1], [2, 2]), ([3, 3], [4]), ([5], [6])],
                    [([1, 1, 1, 1, 1], [2, 2, 2, 2, 2]), ([3, 3, 3], [5, 6])])
        for _ in xrange(5):  # Train the fake model for 5 steps.
            bucket_id = random.choice([0, 1])
            encoder_inputs, decoder_inputs, target_weights = model.get_batch(
                data_set, bucket_id)
            model.step(sess, encoder_inputs, decoder_inputs, target_weights,
                       bucket_id, False)