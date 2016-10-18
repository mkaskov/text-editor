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
import copy
import re
from nnet import data_utils
from util import textUtil as tu

# Obtain the flask app object
app = Flask(__name__)
CORS(app)

global core
global dataBase

url_database = '/home/user/datasets/construction_text_base/БД_3столбца071016.xlsx'

def checkResolved(entity):
    for item in entity:
        if len(item['answer'])==0: return False
    return True

def prepareForSearch(sourceText,cellid):
    _WORD_SPLIT = re.compile("\[\|\|\]")
    tableRow = re.split(_WORD_SPLIT, sourceText)

    category = ""
    startIndexText = -1
    text = ""

    for i,cat in enumerate(tableRow):
        if ner_search.isCategoryExist(dataBase,cat,core):
            category = cat.strip()
            startIndexText = i+1

    # if startIndexText>-1 and startIndexText<len(tableRow): text = tableRow[cellid]
    text = tableRow[cellid]

    [print("[]",x) for x in tableRow]

    print("---------------------------------")
    print ("[final category]:",category)
    print("[final Text]:", text.strip())

    return category,text


def checkExistAndSplitParser(orig,entity):

    finalText = ""
    for x in entity:
        finalText += x["entity"]

    orig = data_utils.tokenizer_tpp(orig, core._TTP_WORD_SPLIT)
    orig = "".join(orig)
    orig = re.sub("[\s]+", "", orig)

    finalText = data_utils.tokenizer_tpp(finalText, core._TTP_WORD_SPLIT)
    finalText = "".join(finalText)
    finalText = re.sub("[\s]+", "", finalText)


    print ("check orig and parser split")
    # print(orig)
    # print (finalText)
    print ("equal:",orig==finalText)

    return orig==finalText


def parse_search(text,secondTry = False):
    category, entity = ner.parse(text,core)


    if secondTry:
        checkCat = re.sub("[\s\xA0]+", "", category.decode('utf-8'))
        if not ner_search.isCategoryExist(dataBase,category,core) or checkCat in tu.dotsArrEntity:
            if ner_search.isInputExist(dataBase,category,core):
                newEntity = []
                newEntity.append(category)
                newEntity+=entity
                entity=newEntity
            elif checkCat in tu.dotsArrEntity:
                entity[0] = category + " " + entity[0]
            else:
                entity[0] = category + " " + entity[0]

            category = ""


    print ("parser------------------------------------")
    print ("[source text]",text)
    print ("[category]",category)
    for x in entity:
        print ("[entity]",x)

    entity = ner_search.search(dataBase,category,entity,core)
    return entity, category

@app.route('/ner/parse/search/simple', methods=['POST'])
def parse_search_simple():
    text = request.json['query'].encode("utf-8")
    entity, category = parse_search(text)
    resolved = checkResolved(entity)
    integrity = ner.check_integrity(text, category, [x["entity"] for x in entity], printStats=False)
    return jsonify(_integrity=integrity, _resolved=resolved, entity=entity, category=category)

@app.route('/ner/parse/search', methods=['POST'])
def parse_search_double_parse():
    text = request.json['query']["text"].encode("utf-8")
    cellid = request.json['query']["cellid"]

    if(cellid>-1):
        exist_category,exist_text = prepareForSearch(text,cellid)
        use_exist_category = False
        if len(exist_text)>0:
            text =  exist_category + " " + exist_text
            use_exist_category = True

    print ("search 0")
    entity, category = parse_search(text)

    print ("[paser category]",category)
    # for x in entity:
    #     print ("[e]",x["entity"],"[a]",x["answer"])

    if (cellid > -1):
        if entity[0]["entity"]==exist_category:
            entity = entity[1:len(entity)]
            category = exist_category
        if not category==exist_category and not checkExistAndSplitParser(exist_text,entity):
                text = exist_text
                use_exist_category = False
                print("search 1")
                entity, category = parse_search(text,secondTry=True)

    print ("[check category]",category)
    print ("[check entity]",entity)

    resolved = checkResolved(entity)
    integrity = ner.check_integrity(text, category, [x["entity"] for x in entity],printStats=False)

    if not resolved and integrity:
        print("-----------------Second try to resolve-------------------------------")

        newEntity = []
        lastStart = 0

        for i, item in enumerate(entity):
            if len(item["answer"]) == 0:
                print("search 2",i)
                _entity, _category = parse_search(item["entity"])

                _resolved = checkResolved(_entity)
                _integrity = ner.check_integrity(item["entity"], _category, [x["entity"] for x in _entity], printStats=False)

                if _integrity and _resolved:
                    if len(_category) > 0: newEntity.append({"entity": _category, "answer": _category})
                    newEntity += entity[lastStart:i] + _entity
                    lastStart = i + 1

        if len(newEntity) > 0: newEntity += entity[lastStart:len(entity)]

        newResolve = True
        for i in newEntity:
            if len(i["answer"]) == 0: newResolve = False

        if len(newEntity) == 0: newResolve = False

        if newResolve: entity=newEntity
        else: print("\x1b[31m[WARNING] entity not full resolved\x1b[0m")

    print ("\nFinal check for resolved and entity")
    resolved = checkResolved(entity)
    integrity = ner.check_integrity(text, category, [x["entity"] for x in entity], printStats=False)

    if len(category) > 0:
        finalEntity = []

        if not use_exist_category: finalEntity.append({"entity": category, "answer": ""})

        finalEntity += entity
        entity = finalEntity

    return jsonify(_integrity=integrity, _resolved=resolved, entity=entity, category=category)

@app.route('/ner/parse/search/tag', methods=['POST'])
def parse_search_tag():
    text = request.json['query'].encode("utf-8")

    _category, _entity = ner.parse(text,core,cleanTags=False)
    category, entity = ner.clean_tags(_category, _entity)
    category = category[0] if len(category) > 0 else ""
    integrity = ner.check_integrity(text, category, entity, printStats=True)
    entity = ner_search.search(dataBase,category,entity,core)
    resolved = checkResolved(entity)

    finalEntity = []
    for i,item in enumerate(entity): finalEntity.append({"entity":item["entity"],"answer":item["answer"],"tag":_entity[i][1]})

    return jsonify(_integrity=integrity,_resolved=resolved, entity=finalEntity, category=category)

@app.route('/ner/parse', methods=['POST'])
def parse():
    text = request.json['query'].encode("utf-8")
    category, entity = ner.parse(text,core)
    integrity = ner.check_integrity(text, category, entity, printStats=False)
    return jsonify(_integrity=integrity,entity=entity, category=category)

@app.route('/ner/parse/tag', methods=['POST'])
def parse_tag():
    text = request.json['query'].encode("utf-8")
    category, entity = ner.parse_tags(text,core)
    category = category[0] if len(category)>0 else ""
    return jsonify(entity=entity, category=category)

if __name__ == "__main__":
    FLAGS, _TTP_WORD_SPLIT, _buckets = initialization.getParams()
    core = core.Core(FLAGS, _TTP_WORD_SPLIT, _buckets, web=True, reduce_gpu=True, forward_only=True)
    dataBase = ner_db.connectToBase(url_database,core)
    app.run(host='0.0.0.0', port=FLAGS.port, debug=True, use_reloader=False, threaded=False)
