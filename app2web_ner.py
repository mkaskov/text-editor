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
from flask_cors import CORS, cross_origin
from nnet import initialization, core
from ner import ner, ner_search,ner_db

# Obtain the flask app object
app = Flask(__name__)
CORS(app)

global core
global dataBase

url_database = '/home/user/datasets/construction_text_base/БД_3столбца071016.xlsx'



@app.route('/ner/parse/search', methods=['POST'])
def decode_sentense():
    text = request.json['query'].encode("utf-8")
    integrity, category, entity = ner.parse(text,core)
    entity,resolved = ner_search.search(dataBase,integrity,category,entity,core)
    category = category[0] if len(category)>0 else ""
    return jsonify(_integrity=integrity,_resolved=resolved, entity=entity, category=category)

if __name__ == "__main__":
    FLAGS, _TTP_WORD_SPLIT, _buckets = initialization.getParams()
    core = core.Core(FLAGS, _TTP_WORD_SPLIT, _buckets, web=True, reduce_gpu=True, forward_only=True)
    dataBase = ner_db.connectToBase(url_database,core)
    app.run(host='0.0.0.0', port=FLAGS.port, debug=True, use_reloader=False, threaded=True)
