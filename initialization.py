#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from ConfigParser import SafeConfigParser
import re
import tensorflow as tf
import sys
import os.path

buckets = [(5, 10), (10, 15), (30, 35), (50, 55), (70, 75), (100, 110)]
buckets_v2 = [(5, 5), (10, 10), (30, 30), (50, 50), (70, 70), (100, 100)]
test =  [(5, 5),(10, 10), (30, 30), (50, 50), (70, 70), (110,110)]

def getDefaultBuckets(): return buckets_v2

def getConfig(config_file):
    config_file+='model.ini'
    if not os.path.isfile(config_file): return None

    parser = SafeConfigParser()
    parser.read(config_file)

    _conf_ints = [(key, int(value)) for key, value in parser.items('ints')]
    _conf_floats = [(key, float(value)) for key, value in parser.items('floats')]
    _conf_strings = [(key, str(value)) for key, value in parser.items('strings')]
    _get_buckets = [(key, str(value)) for key, value in parser.items('buckets')]

    with open(config_file) as f:
        [_conf_strings.append(('regex',r[r.find('=')+1:].strip())) for r in f.readlines() if 'regex_string' in r]

    _buckets = []
    for x in _get_buckets:
        if 'buckets' in x[0]:
            bucketsText = x[1].split(';')
            for elem in bucketsText:
                nums = re.findall('\d+', elem)
                _buckets.append((int(nums[0]), int(nums[1])))
        _conf_strings.append(('buckets',_buckets))

    return dict(_conf_ints + _conf_floats + _conf_strings)

def getParams():

    # defaults
    value_num_layers = 3
    value_learning_rate = 0.5
    value_learning_rate_decay_factor = 0.9
    value_max_gradient_norm = 5.0
    value_batch_size = 8
    value_size = 512
    value_in_vocab_size = 40000
    value_out_vocab_size = 40000
    value_train_dir = "/tmp"
    value_max_train_data_size = 0
    value_steps_per_checkpoint = 400
    value_default_port = 5002
    _TTP_WORD_SPLIT = re.compile(ur"ГОСТ\s[\d]+\-?[\d]+|[а-яА-Я]+\/[а-яА-Я\d]+\.{1}[а-яА-Я\d]+\.{1}|[а-яА-Я]+\/\([^()]+\)|[^\s\d.,():]+\d?\/[^\s.,():]+|м{1,2}[\d⁰¹²³⁴⁵⁶⁷⁸⁹]|см[\d⁰¹²³⁴⁵⁶⁷⁸⁹]|дм[\d⁰¹²³⁴⁵⁶⁷⁸⁹]|[a-zA-Zа-яА-ЯёЁ]*[^\s\d.!?,:;()\"\'<>%«»±^…\-*=/\xA0]|[\d()!?\'\"<>%,:;±«»^…\-*=/]|\.{3}|\.{1}")
    _buckets = getDefaultBuckets()

    #read data from model.ini, if file exist
    data_dir = None
    for id, arg in enumerate(sys.argv[1:]):
        if '--data_dir' in arg: data_dir = sys.argv[1:][id + 1]

    if data_dir is not None:
        params = getConfig(config_file=data_dir)
        if params is not None:
            if 'num_layers' in params.keys(): value_num_layers = params["num_layers"]
            if 'learning_rate' in params.keys(): value_learning_rate = params["learning_rate"]
            if 'learning_rate_decay_factor' in params.keys(): value_learning_rate_decay_factor = params["learning_rate_decay_factor"]
            if 'max_gradient_norm' in params.keys(): value_max_gradient_norm = params["max_gradient_norm"]
            if 'batch_size' in params.keys(): value_batch_size = params["batch_size"]
            if 'layer_size' in params.keys(): value_size = params["layer_size"]
            if 'in_vocab_size' in params.keys():  value_in_vocab_size = params["in_vocab_size"]
            if 'out_vocab_size' in params.keys():  value_out_vocab_size = params["out_vocab_size"]
            if "train_dir" in params.keys():  value_train_dir = params["train_dir"]
            if "max_train_data_size" in params.keys(): value_max_train_data_size = params["max_train_data_size"]
            if "steps_per_checkpoint" in params.keys(): value_steps_per_checkpoint = params["steps_per_checkpoint"]
            if "buckets" in params.keys(): _buckets = params["buckets"]
            if "regex" in params.keys():  _TTP_WORD_SPLIT = re.compile(ur''+params["regex"].decode('utf-8'))
            if "checkpoints_directory" in params.keys(): value_train_dir = data_dir; value_train_dir+=params["checkpoints_directory"]

    #set value to TF flags
    tf.app.flags.DEFINE_float("learning_rate", value_learning_rate, "Learning rate.")
    tf.app.flags.DEFINE_float("learning_rate_decay_factor", value_learning_rate_decay_factor, "Learning rate decays by this much.")
    tf.app.flags.DEFINE_float("max_gradient_norm", value_max_gradient_norm, "Clip gradients to this norm.")
    tf.app.flags.DEFINE_integer("batch_size", value_batch_size, "Batch size to use during training.")
    tf.app.flags.DEFINE_integer("num_layers", value_num_layers, "Number of layers in the model.")
    tf.app.flags.DEFINE_integer("size", value_size, "Size of each model layer.")
    tf.app.flags.DEFINE_integer("in_vocab_size", value_in_vocab_size, "INPUT vocabulary size.")
    tf.app.flags.DEFINE_integer("out_vocab_size", value_out_vocab_size, "OUTPUT vocabulary size.")
    tf.app.flags.DEFINE_string("data_dir", "/tmp", "Data directory")
    tf.app.flags.DEFINE_string("train_dir", value_train_dir, "Training directory.")
    tf.app.flags.DEFINE_integer("max_train_data_size", value_max_train_data_size, "Limit on the size of training data (0: no limit).")
    tf.app.flags.DEFINE_integer("steps_per_checkpoint", value_steps_per_checkpoint, "How many training steps to do per checkpoint.")
    tf.app.flags.DEFINE_integer("port", value_default_port, "default port.")
    tf.app.flags.DEFINE_boolean("decode", False, "Set to True for interactive decoding.")
    tf.app.flags.DEFINE_boolean("self_test", False, "Run a self-test if this is set to True.")
    tf.app.flags.DEFINE_boolean("reduce_gpu", False, "")
    tf.app.flags.DEFINE_boolean("web", False, "")

    return tf.app.flags.FLAGS,_TTP_WORD_SPLIT,_buckets