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
from flask_cors import CORS
from nnet import initialization, core
from ner import ner,ner_db
import re
from nnet import data_utils as du
from util import textUtil as tu
import docker_prepare

# Obtain the flask app object
app = Flask(__name__)
CORS(app)

global core
global dataBase

def checkResolved(entity):
    for item in entity:
        if len(item['answer'])==0: return False
    return True

def splitForSearch(sourceText, cellid):
    _WORD_SPLIT = re.compile("\[\|\|\]")
    sourceText = re.sub("[\s]+", " ", sourceText)
    sourceText = tu.replace_celsius(sourceText)
    tableRow = re.split(_WORD_SPLIT,sourceText.strip())

    for i,cat in enumerate(tableRow):
        if ner_db.isInputExist("category",dataBase,cat,core): category = tu.removeSamples(cat,core).strip()

    if len(category)==0:
        if ner_db.isInputExist("category",dataBase, tableRow[0], core): category = tu.removeSamples(tableRow[0],core).strip()

    text = tableRow[cellid].strip()

    return category,text

def parse_search(text,exist_category,use_exist_category=False):
    category, entity = ner.parse(text,core)

    if not use_exist_category:
        if len(category)>0:
            print("-----------1")
            if ner_db.isInputExist("category", dataBase, category, core):
                use_exist_category = True
                category  = tu.removeSamples(category, core).strip()
                exist_category = category
                print ("-----------2")

        elif ner_db.isInputExist("category", dataBase, entity[0], core):
            use_exist_category = True
            category = tu.removeSamples(entity[0],core).strip()
            exist_category = category
            if len(entity)>0:
                entity = entity[1:]
            else:
                entity = []
            print("-----------3")

    print ("-----------------------------------------------")
    print("[ner category]", category)
    print("[ner entity]")
    [print("[]",x) for x in entity]
    print("[/ner entity]")

    categoryRaw ="".join([x for x in du.tokenizer_tpp(category, core._TTP_WORD_SPLIT)])
    existRaw = "".join([x for x in du.tokenizer_tpp(exist_category, core._TTP_WORD_SPLIT)])
    if len(entity) > 0:
        entity0Raw = "".join([x for x in du.tokenizer_tpp(entity[0], core._TTP_WORD_SPLIT)])
    else:
        entity0Raw = ""

    categorySpace = " ".join([x for x in du.tokenizer_tpp(category, core._TTP_WORD_SPLIT)])
    existCategorySpace = " ".join([x for x in du.tokenizer_tpp(exist_category, core._TTP_WORD_SPLIT)])

    if use_exist_category:
        if categoryRaw==existRaw:
           print("var 1")
        elif entity0Raw==existRaw:
           if len(entity) > 1:
             entity = entity[1:]
           print ("var 2")
        elif existRaw in categoryRaw:
            entity = [category]+entity
            if len(entity) > 0:
                entity[0] = entity[0].strip()[len(existCategorySpace):].strip()
            print ("var 3")
        elif existRaw in (categoryRaw+entity0Raw):
            print("var 4")
            if len(entity) > 0:
                entity[0] = categorySpace +" " + entity[0].strip()
                entity[0] = entity[0].strip()[len(existCategorySpace):].strip()
        else:
            if len(entity) > 0: entity[0] = category + " " + entity[0]
            print ("var 5")

        category = exist_category

    else:
        print ("var 6")
        if len(entity) > 0:
            entity[0] = category + " " + entity[0]
            category = exist_category


    if len(entity) > 1:
        if len(entity[0].strip()) == 0:
            entity = entity[1:]

    print("-------------after use exist----------------------------------")
    print("[ner exist category]", category)
    print("[ner exist entity]")
    [print("[]", x) for x in entity]
    print("[/ner exist entity]")

    entity = ner_db.search(dataBase, category, entity, core)
    return entity, category

def appendPunktMars(entity):
    for x in entity:
        tokensEnt = du.tokenizer_tpp(x["entity"], core._TTP_WORD_SPLIT)
        for y,answer in enumerate(x["answer"]):
            tokensAns = du.tokenizer_tpp(answer, core._TTP_WORD_SPLIT)

            if len(tokensAns)>0 and len(tokensEnt)>0:
                dotEntEnd = tokensEnt[-1]
                dotEntStart = tokensEnt[0]
                dotAnsEnd = tokensAns[-1]
                dotAnsStart = tokensAns[0]
                if dotEntEnd in tu.dotsArr and not dotEntEnd==dotAnsEnd:
                    if dotEntEnd in tu.dotsArrSpace:
                        answer=answer + " " + dotEntEnd
                    else:
                        answer = answer + dotEntEnd
                if dotEntStart in tu.dotsArr and not dotEntStart==dotAnsStart: answer = dotEntStart +" "+ answer
                x["answer"][y] = answer

    return entity

def getQuery(request):
    q = request.json['query']
    q = tu.decode_from_java(q)

    if q.find('[/cellid]') == -1:  q = "[cellid]-1[/cellid] " + q

    text = q[q.index('[/cellid]') + len("[/cellid]"):]
    cellid = int(q[len("[cellid]"):q.index('[/cellid]')])

    return text,cellid

def prepareForSearch(text,cellid):
    use_exist_category = False
    exist_category = ""

    if (cellid > -1):
        exist_category, exist_text = splitForSearch(text, cellid)
        if len(exist_text) > 0:
            text = exist_category + " " + exist_text
            use_exist_category = True
    else:
        text = re.sub("\[\|\|\]", " ", text)

    return exist_category,text,use_exist_category

@app.route('/ner/parse/search/simple', methods=['POST'])
def parse_search_simple():
    text = request.json['query'].encode("utf-8")
    entity, category = parse_search(text)
    resolved = checkResolved(entity)
    integrity = ner.check_integrity(text, category, [x["entity"] for x in entity])
    return jsonify(_integrity=integrity, _resolved=resolved, entity=entity, category=category)

@app.route('/ner/parse/search', methods=['POST'])
def parse_search_double_parse():

    text, cellid = getQuery(request)
    exist_category,exist_text,use_exist_category = prepareForSearch(text,cellid)
    entity, category = parse_search(exist_text,exist_category,use_exist_category)
    resolved = checkResolved(entity)

    if use_exist_category:
        integrity = ner.check_integrity(exist_text, category, [x["entity"] for x in entity])
    else: integrity = ner.check_integrity(exist_category+exist_text, category, [x["entity"] for x in entity])

    if not resolved or not integrity:
        print ("\n[Firts search results]")
        print("[resolved]", resolved)
        print("[integrity]", integrity)

    if not resolved and integrity:
        print("-----------------Second try to resolve-------------------------------")

        newText = ""
        newEntity = []
        lastEnd = 0
        lastStart = -1

        for i, item in enumerate(entity):
            if len(item["answer"]) == 0:
                if lastStart==-1: lastStart=i
                newText+=" " +item["entity"]
            elif len(newText)>0:
                _entity = ner_db.search(dataBase, category, [newText], core)
                resolved = checkResolved(_entity)

                _entity2, _category2 = parse_search(newText, category, use_exist_category)
                resolved2 = checkResolved(_entity2)

                if resolved2:
                    newText = ""
                    newEntity += entity[lastEnd:lastStart] + _entity2
                    lastEnd = i + 1
                    lastStart = -1
                elif resolved:
                    newText = ""
                    newEntity += entity[lastEnd:lastStart] + _entity
                    lastEnd = i + 1
                    lastStart = -1
                else:
                    _entity, _category = parse_search(category+" "+newText, category, use_exist_category)

                    print("-----------------------------------------------")
                    print("[parsed second category]", _category)
                    print("[parsed second text]")
                    for x in _entity:
                        print("--------------------------------")
                        print("[Answer second]", x["answer"])
                        print("[Entity second]", x["entity"])
                    print("[/parsed second text]")

                    _resolved = checkResolved(_entity)
                    _integrity = ner.check_integrity(newText, "", [x["entity"] for x in _entity])

                    newText = ""

                    print("\n[resolved second]", _resolved)
                    print("[integrity second]", _integrity)

                    if _integrity and _resolved:
                        print ("[second try sucessfull]",i)
                        newEntity += entity[lastEnd:lastStart] +_entity
                        lastEnd = i+1
                        lastStart = -1

                        print ("[current new entity]")
                        for i, item in enumerate(newEntity):
                            print(i, item["entity"])
                    else:
                        lastStart =-1

        if len(newText)>0:
            _entity = ner_db.search(dataBase, category, [newText], core)
            resolved = checkResolved(_entity)

            _entity2, _category2 = parse_search(newText, category, use_exist_category)
            resolved2 = checkResolved(_entity2)

            if resolved2:
                newEntity += entity[lastEnd:lastStart] + _entity2
                entity = newEntity
            elif resolved:
                newEntity += entity[lastEnd:lastStart] + _entity
                entity = newEntity
            else:
                _entity, _category = parse_search(category+" "+newText, category, use_exist_category)

                print("-----------------------------------------------")
                print("[parsed final category]", _category)
                print("[parsed final text]")
                for x in _entity:
                    print("--------------------------------")
                    print("[Answer final]", x["answer"])
                    print("[Entity final]", x["entity"])
                print("[/parsed final text]")

                _resolved = checkResolved(_entity)
                _integrity = ner.check_integrity(newText, "", [x["entity"] for x in _entity])

                print("\n[resolved final]", _resolved)
                print("[integrity final]", _integrity)

                if _integrity and _resolved:
                    print("[second try sucessfull]", i)
                    newEntity += entity[lastEnd:lastStart] + _entity

                    print("[current new entity]")
                    for i, item in enumerate(newEntity):
                        print(i, item["entity"])

                    entity = newEntity

        elif len(newEntity) > 0:
            newEntity += entity[lastEnd-1:len(entity)]
            entity = newEntity

        for i,item in enumerate(entity):
            print (i,item["entity"])

    print ("----------------__Finish check_----------------------------")
    resolved = checkResolved(entity)
    if use_exist_category:
        integrity = ner.check_integrity(exist_text, category, [x["entity"] for x in entity])
    else: integrity = ner.check_integrity(exist_category+exist_text, category, [x["entity"] for x in entity])

    entity = appendPunktMars(entity)
    answer = jsonify(_integrity=integrity, _resolved=resolved, entity=entity, category=category)

    if 'readable' in request.json: return answer
    return jsonify(answer=answer.get_data(as_text=True))

@app.route('/ner/parse/search/tag', methods=['POST'])
def parse_search_tag():
    text = request.json['query'].encode("utf-8")

    _category, _entity = ner.parse(text,core,cleanTags=False)
    category, entity = ner.clean_tags(_category, _entity)
    category = category[0] if len(category) > 0 else ""
    integrity = ner.check_integrity(text, category, entity)
    entity = ner_db.search(dataBase, category, entity, core)
    resolved = checkResolved(entity)

    finalEntity = []
    for i,item in enumerate(entity): finalEntity.append({"entity":item["entity"],"answer":item["answer"],"tag":_entity[i][1]})

    return jsonify(_integrity=integrity,_resolved=resolved, entity=finalEntity, category=category)

@app.route('/ner/parse', methods=['POST'])
def parse():
    text = request.json['query'].encode("utf-8")
    category, entity = ner.parse(text,core)
    integrity = ner.check_integrity(text, category, entity)
    return jsonify(_integrity=integrity,entity=entity, category=category)

@app.route('/ner/parse/tag', methods=['POST'])
def parse_tag():
    text = request.json['query'].encode("utf-8")
    category, entity = ner.parse_tags(text,core)
    category = category[0] if len(category)>0 else ""
    return jsonify(entity=entity, category=category)

if __name__ == "__main__":
    FLAGS, _TTP_WORD_SPLIT, _buckets,app_options = initialization.getParams()
    if app_options["fixdataset"]: docker_prepare.fix_dataset()
    core = core.Core(FLAGS, _TTP_WORD_SPLIT, _buckets,app_options)
    dataBase = ner_db.connectToBase(app_options["url_database"],core)
    app.run(host='0.0.0.0', port=FLAGS.port, debug=True, use_reloader=False, threaded=False)
