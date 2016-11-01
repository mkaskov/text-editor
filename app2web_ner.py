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

url_database = '/home/user/datasets/construction_text_base/БД_3столбца281016.xlsx'

def checkResolved(entity):
    for item in entity:
        if len(item['answer'])==0: return False
    return True

def splitForSearch(sourceText, cellid):
    _WORD_SPLIT = re.compile("\[\|\|\]")
    sourceText = re.sub("[\s]+", " ", sourceText)
    sourceText = sourceText.strip()
    tableRow = re.split(_WORD_SPLIT,sourceText)

    for i,cat in enumerate(tableRow):
        if ner_db.isCategoryExist(dataBase,cat,core): category = cat.strip()

    if len(category)==0:
        if ner_db.isCategoryExist(dataBase, tableRow[0], core): category = tableRow[0].strip()

    text = tableRow[cellid].strip()

    return category,text


def checkExistAndSplitParser(orig,entity):

    finalText = ""
    for x in entity: finalText += x["entity"]

    orig = du.tokenizer_tpp(orig, core._TTP_WORD_SPLIT)
    orig = "".join(orig)
    orig = re.sub("[\s]+", "", orig)

    finalText = du.tokenizer_tpp(finalText, core._TTP_WORD_SPLIT)
    finalText = "".join(finalText)
    finalText = re.sub("[\s]+", "", finalText)

    return orig==finalText

def parse_search(text,exist_category,use_exist_category=False):
    category, entity = ner.parse(text,core)

    print ("-----------------------------------------------")
    print("[ner category]", category)
    print("[ner entity]")
    [print(x) for x in entity]
    print("[/ner entity]")

    origCategory = category

    if use_exist_category:
        if ner_db.isInputExist(dataBase, category, core) and not ner_db.isCategoryExist(dataBase, category, core):
            entity = [category] + entity
            print ("[p var 1]")

        else:
        # elif not ner_search.isInputExist(dataBase, category, core) and not ner_search.isCategoryExist(dataBase, category, core) and len(category)>0:
            print("[p var 2]")

            def isCatInText(text,category):
                checkCat = [x for x in du.tokenizer_tpp(category, core._TTP_WORD_SPLIT)]
                pos = text.find(checkCat[len(checkCat) - 1])
                return pos>-1,pos,len(checkCat[len(checkCat) - 1])

            newEntityV1 = [category] + entity
            posExist,pos,lastLen = isCatInText(newEntityV1[0],exist_category)
            if posExist:
                print ("sub v2 1")
                entity = [newEntityV1[0][pos+lastLen:]]+newEntityV1[1:]
            else:
                print("sub v2 2")
                newEntityV2 = [category + " " + entity[0]] + entity[1:]
                posExist, pos,lastLen = isCatInText(newEntityV2[0], exist_category)
                print (posExist, pos,lastLen)
                if posExist:
                    print("sub v2 3")
                    entity = [newEntityV2[0][pos+lastLen:]]+newEntityV2[1:]
        # else:
        #     print("[p var 3]")

        if len(entity[0].strip()) == 0:
            entity = entity[1:]
        category = exist_category

        checkCat = du.tokenizer_tpp(origCategory, core._TTP_WORD_SPLIT)
        if len(checkCat) == 1:
            origCategory = origCategory if checkCat[0] in tu.dotsArrEntity else ""
            entity[0] = origCategory + " " + entity[0]

        print("-------------entity alter in base----------------------------------")
        print("[entity alter category]", category)
        print("[entity alter entity]")
        [print(x) for x in entity]
        print("[/entity alter entity]")

    else:
        if len(category)==0 and entity[0]==exist_category:
            category = entity[0]
            entity = entity[1:]

    print("-------------after use exist----------------------------------")
    print("[ner exist category]", category)
    print("[ner exist entity]")
    [print(x) for x in entity]
    print("[/ner exist entity]")

    entity = ner_db.search(dataBase, category, entity, core)
    return entity, category

def appendPunktMars(entity):
    for x in entity:
        answerText =x["answer"] if isinstance(x["answer"], (str)) else x["answer"].encode("utf-8")
        entityText =x["entity"] if isinstance(x["entity"], (str)) else x["entity"].encode("utf-8")

        tokensEnt = du.tokenizer_tpp(entityText, core._TTP_WORD_SPLIT)
        tokensAns = du.tokenizer_tpp(answerText, core._TTP_WORD_SPLIT)

        if len(tokensAns)>0 and len(tokensEnt)>0:
            dotEntEnd = tokensEnt[-1]
            dotEntStart = tokensEnt[0]
            dotAnsEnd = tokensAns[-1]
            dotAnsStart = tokensAns[0]
            if dotEntEnd in tu.dotsArr and not dotEntEnd==dotAnsEnd: x["answer"]=x["answer"] + dotEntEnd
            if dotEntStart in tu.dotsArr and not dotEntStart==dotAnsStart: x["answer"] = dotEntStart +" "+ x["answer"]

    return entity

def getQyery(request):
    query = request.json['query']
    query = tu.decode_from_java(query)

    if query.find('[/cellid]') == -1:  query = "[cellid]-1[/cellid] " + query

    text = query[query.index('[/cellid]') + len("[/cellid]"):]
    cellid = int(query[len("[cellid]"):query.index('[/cellid]')])

    return text,cellid

def prepareForSearch(text,cellid):
    use_exist_category = False
    exist_category = ""

    if (cellid > -1):
        exist_category, exist_text = splitForSearch(text, cellid)
        if len(exist_text) > 0:
            print("[var 2]")
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
    integrity = ner.check_integrity(text, category, [x["entity"] for x in entity], printStats=False)
    return jsonify(_integrity=integrity, _resolved=resolved, entity=entity, category=category)

@app.route('/ner/parse/search', methods=['POST'])
def parse_search_double_parse():

    text, cellid = getQyery(request)
    exist_category,exist_text,use_exist_category = prepareForSearch(text,cellid)

    print("-----------------------------------------------")
    print("[searched category]", exist_category)
    print("[searched text]", exist_text)
    print ("[exist_category]",use_exist_category)

    entity, category = parse_search(exist_text,exist_category,use_exist_category)

    print("-----------------------------------------------")
    print("[parsed category]", category)
    print("[parsed text]")
    for x in entity:
        print ("--------------------------------")
        print ("[Answer]",x["answer"])
        print ("[Entity]",x["entity"])
    print("[/parsed text]")

    resolved = checkResolved(entity)

    if use_exist_category:
        integrity = ner.check_integrity(exist_text, category, [x["entity"] for x in entity], printStats=True)
    else: integrity = ner.check_integrity(exist_category+exist_text, category, [x["entity"] for x in entity], printStats=True)

    print("\n[resolved]", resolved)
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
                newText+=item["entity"]
            elif len(newText)>0:
                _entity, _category = parse_search(newText, category, use_exist_category)

                print("-----------------------------------------------")
                print("[parsed second category]", _category)
                print("[parsed second text]")
                for x in _entity:
                    print("--------------------------------")
                    print("[Answer second]", x["answer"])
                    print("[Entity second]", x["entity"])
                print("[/parsed second text]")

                _resolved = checkResolved(_entity)
                _integrity = ner.check_integrity(newText, "", [x["entity"] for x in _entity], printStats=True)

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
            _entity, _category = parse_search(newText, category, use_exist_category)

            print("-----------------------------------------------")
            print("[parsed final category]", _category)
            print("[parsed final text]")
            for x in _entity:
                print("--------------------------------")
                print("[Answer final]", x["answer"])
                print("[Entity final]", x["entity"])
            print("[/parsed final text]")

            _resolved = checkResolved(_entity)
            _integrity = ner.check_integrity(newText, "", [x["entity"] for x in _entity], printStats=True)

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


    print ("------------------------Finishing------------------------------")
    resolved = checkResolved(entity)
    if use_exist_category:
        integrity = ner.check_integrity(exist_text, category, [x["entity"] for x in entity], printStats=True)
    else: integrity = ner.check_integrity(exist_category+exist_text, category, [x["entity"] for x in entity], printStats=True)

    entity = appendPunktMars(entity)

    answer = jsonify(_integrity=integrity, _resolved=resolved, entity=entity, category=category)

    print (answer)

    if 'readable' in request.json: return answer
    return jsonify(answer=answer.get_data(as_text=True))

@app.route('/ner/parse/search/tag', methods=['POST'])
def parse_search_tag():
    text = request.json['query'].encode("utf-8")

    _category, _entity = ner.parse(text,core,cleanTags=False)
    category, entity = ner.clean_tags(_category, _entity)
    category = category[0] if len(category) > 0 else ""
    integrity = ner.check_integrity(text, category, entity, printStats=True)
    entity = ner_db.search(dataBase, category, entity, core)
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
    FLAGS, _TTP_WORD_SPLIT, _buckets,app_options = initialization.getParams()
    if app_options["fixdataset"]: docker_prepare.fix_dataset()
    core = core.Core(FLAGS, _TTP_WORD_SPLIT, _buckets,app_options)
    dataBase = ner_db.connectToBase(url_database,core)
    app.run(host='0.0.0.0', port=FLAGS.port, debug=True, use_reloader=False, threaded=False)
