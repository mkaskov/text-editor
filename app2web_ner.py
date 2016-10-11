#! /usr/bin/env python
# -*- coding: utf-8 -*-
# by PureMind

"""ONLY for start app flask for web decoding data.

Директория с данными --data_dir 
Директория с обученной моделью --train_dir.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from flask import Flask, request, jsonify
from nnet import initialization, core
from ner import ner, ner_search
import pandas as pd
from nnet import data_utils
from util import textUtil

# Obtain the flask app object
app = Flask(__name__)

global core
global dataBase

url_database = '/home/user/datasets/construction_text_base/БД_3столбца071016.xlsx'

def connectToBase():
    textbase = pd.read_excel(url_database, header=None, names=['category', 'in', 'out'])
    textbase = textbase.fillna(value=' ')
    pd.isnull(textbase).any(1).nonzero()[0]  # проверка nan значений

    textbase['in'] = textbase['in'].apply(lambda x: textUtil.clearFromDots(data_utils.tokenizer_tpp(x.encode("utf-8"),core._TTP_WORD_SPLIT)))
    textbase['category'] = textbase['category'].apply(lambda x: textUtil.clearFromDots(data_utils.tokenizer_tpp(x.encode("utf-8"),core._TTP_WORD_SPLIT)))

    return textbase

@app.route('/ner/parse/search', methods=['POST'])
def decode_sentense():

    query = request.json['query'].encode("utf-8")

    integrity, category, entity = ner.parse(query,core)

    entity = ner_search.search(dataBase,integrity,category,entity,core)

    return jsonify(_integrity=integrity, entity=entity, category=category)
    # return jsonify(entity)

if __name__ == "__main__":
    FLAGS, _TTP_WORD_SPLIT, _buckets = initialization.getParams()
    core = core.Core(FLAGS, _TTP_WORD_SPLIT, _buckets, web=True, reduce_gpu=True, forward_only=True)
    dataBase = connectToBase()
    app.run(host='0.0.0.0', port=FLAGS.port, debug=True, use_reloader=False, threaded=True)
