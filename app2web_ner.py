#! /usr/bin/env python

# by PureMind

"""ONLY for start app flask for web decoding data.

Директория с данными --data_dir 
Директория с обученной моделью --train_dir.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re

from flask import Flask, request, jsonify
from flask_cors import CORS

import docker_prepare
from ner import ner_db as NERDB
from ner import ner
from nnet import data_utils as du
from nnet import initialization, core
from util import textUtil as tu

# Obtain the flask app object
app = Flask(__name__)
CORS(app)

global core
global nerdb

def isEntityResolved(entity):
    for item in entity:
        if len(item['answer'])==0: return False
    return True

def extractQueryData(input_data, text_cell_id):
    CELL_SPLIT = re.compile("\[\|\|\]")

    #clear input text
    input_data = re.sub("[\s]+", " ", input_data)
    input_data = tu.replace_celsius(input_data)

    tableRow = re.split(CELL_SPLIT, input_data.strip())

    category = ""
    category_cell_id = -1

    [print("[splitted]",x.strip(),len(x.strip())) for x in tableRow]

    for i,cat in enumerate(tableRow):
        if nerdb.isInputExist(nerdb.category,cat):
            category_cell_id = i
            category = tu.removeSamples(cat,core).strip()

    if len(category)==0:
        if nerdb.isInputExist(nerdb.category,tableRow[0]): category = tu.removeSamples(tableRow[0],core).strip()

    text = tableRow[text_cell_id].strip()

    return category,text,len(text.strip()),category_cell_id,tableRow

def parse_search(text,exist_category,use_exist_category=False):
    category, entity = ner.parse(text,core)

    if not use_exist_category:
        if len(category)>0:
            print("-----------1")
            if nerdb.isInputExist(nerdb.category, category):
                use_exist_category = True
                category  = tu.removeSamples(category, core).strip()
                exist_category = category
                print ("-----------2")

        elif nerdb.isInputExist(nerdb.category, entity[0]):
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
        if categoryRaw==existRaw and len(existRaw)>0:
           print("var 0")
        elif entity0Raw==existRaw:
           if len(entity) > 0:
             entity = entity[1:]
             category = exist_category
           print ("var 1")
        elif existRaw in categoryRaw and len(existRaw)>0:
            entity = [category]+entity
            if len(entity) > 0:
                entity[0] = entity[0].strip()[len(existCategorySpace):].strip()
                category = exist_category
            print ("var 2")
        elif existRaw in (categoryRaw+entity0Raw) and len(categoryRaw)>0:
            print("var 3")
            if len(entity) > 0:
                entity[0] = categorySpace +" " + entity[0].strip()
                entity[0] = entity[0].strip()[len(existCategorySpace):].strip()
                category = exist_category
        elif len(categoryRaw)==0:
            if ( tu.removeSamples(exist_category, core).strip())==( tu.removeSamples( entity[0], core).strip()):
                category = entity[0]
                if len(entity)>0:
                    entity = entity[1:]
                else:
                    entity = []
            else:
                if existRaw in entity0Raw:
                    if len(entity) > 0:
                        entity[0] = categorySpace + " " + entity[0].strip()
                        entity[0] = entity[0].strip()[len(existCategorySpace):].strip()
                        category = exist_category
                else:
                    category = exist_category
            print ("var 4")
        else:
            if len(entity) > 0:
                entity[0] = category + " " + entity[0]
                category = exist_category
            print ("var 5")



    else:
        print ("var 6")
        if len(entity) > 0:
            entity[0] = category + " " + entity[0]
            category = exist_category


    if len(entity) > 0:
        if len(entity[0].strip()) == 0:
            entity = entity[1:]

    print("-------------after use exist----------------------------------")
    print("[ner exist category]", category)
    print("[ner exist entity]")
    [print("[]", x) for x in entity]
    print("[/ner exist entity]")

    entity = nerdb.search(category, entity)
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

def getQueryData(request):
    query = request.json['query']
    query = tu.decode_from_java(query)

    if query.find('[/cellid]') == -1:  query = "[cellid]-1[/cellid] " + query

    input_data = query[query.index('[/cellid]') + len("[/cellid]"):]
    text_cell_id = int(query[len("[cellid]"):query.index('[/cellid]')])

    return input_data,text_cell_id

def prepareForSearch(input_data, text_cell_id):
    use_exist_category = False
    exist_category = ""

    if (text_cell_id > -1):
        exist_category, exist_text,len_exist_text,category_cellid,row = extractQueryData(input_data, text_cell_id)
        if len(exist_text) > 0:
            text = exist_category + " " + exist_text
            if(len(exist_category)>0):
                use_exist_category = True
    else:
        text = re.sub("\[\|\|\]", " ", input_data)
        len_exist_text = len(text)
        category_cellid = -1
        row = []
        exist_text = text
    print ("[user exist category]",use_exist_category,exist_category)
    return exist_category,text,use_exist_category,len_exist_text,category_cellid,row,exist_text

# @app.route('/ner/parse/search/simple', methods=['POST'])
# def parse_search_simple():
#     text = request.json['query'].encode("utf-8")
#     entity, category = parse_search(text)
#     resolved = isEntityResolved(entity)
#     integrity = ner.check_integrity(text, category, [x["entity"] for x in entity])
#     return jsonify(_integrity=integrity, _resolved=resolved, entity=entity, category=category)

def simpleBaseSearch(entity, row, cellid, category_cellid):
    print (row[cellid])
    print (row[category_cellid])

    if not cellid-1==category_cellid:
        catText = row[cellid-1]
        catText = tu.removeSpaces(catText)

        print("[cattext]", catText)

        for i1,x in enumerate(entity):
            for i2,z in enumerate(x["answer"]):
                if z.find(catText)==0:
                    entity[i1]["answer"][i2] = z[len(catText):].strip()
                    print (entity[i1]["answer"][i2])

    if cellid+1<len(row):
        postEntity = row[cellid+1]
        postEntity = tu.removeSpaces(postEntity)

        print("[postEntity]", postEntity)

        for i1, x in enumerate(entity):
            for i2, z in enumerate(x["answer"]):
                if z.find(postEntity) > 0:
                    entity[i1]["answer"][i2] = z[:len(z)-len(postEntity)].strip()
                    print(entity[i1]["answer"][i2])

@app.route('/ner/parse/search', methods=['POST'])
def entry_point():
    input_data, text_cell_id = getQueryData(request)
    exist_category, exist_text, use_exist_category, len_exist_text,category_cellid,row,cellText = prepareForSearch(input_data, text_cell_id)

    if len_exist_text > nerdb.maxLenChar or text_cell_id==-1 or len(row)<2:
        return ner_parse_search(exist_category, exist_text, use_exist_category, len_exist_text, category_cellid, row, cellText)
    else:
        print("Try find")
        isCategoryInBase = nerdb.isInputExist(nerdb.category,exist_category)
        if(isCategoryInBase):
            entity = nerdb.search(exist_category,[cellText],False)

            print (entity)

            resolved = isEntityResolved(entity)
            if not resolved:
                return ner_parse_search(exist_category, exist_text, use_exist_category, len_exist_text, category_cellid, row, cellText)

            simpleBaseSearch(entity, row, text_cell_id, category_cellid)

            integrity = ner.check_integrity(exist_text, exist_category, [x["entity"] for x in entity])

            answer = jsonify(_integrity=integrity, _resolved=resolved, entity=entity, category=exist_category)

            return jsonify(answer=answer.get_data(as_text=True))
        else:
            print ("category not in base")
            return ner_parse_search(exist_category, exist_text, use_exist_category, len_exist_text,
                                    category_cellid, row, cellText)

    return jsonify(answer=None)

def ner_parse_search(exist_category, exist_text, use_exist_category, len_exist_text, category_cellid, row, cellText):
    print("Ner Parse")
    try:
        entity, category = parse_search(exist_text,exist_category,use_exist_category)

        finalAppend = False
        if len(exist_category)==0 and len(category)>0: finalAppend = True
        resolved = isEntityResolved(entity)

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
                    _entity = nerdb.search(category, [newText], core)
                    resolved = isEntityResolved(_entity)

                    _entity2, _category2 = parse_search(newText, category, use_exist_category)
                    resolved2 = isEntityResolved(_entity2)

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

                        _resolved = isEntityResolved(_entity)
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
                _entity = nerdb.search(category, [newText], core)
                resolved = isEntityResolved(_entity)

                _entity2, _category2 = parse_search(newText, category, use_exist_category)
                resolved2 = isEntityResolved(_entity2)

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

                    _resolved = isEntityResolved(_entity)
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
        resolved = isEntityResolved(entity)
        if use_exist_category:
            integrity = ner.check_integrity(exist_text, category, [x["entity"] for x in entity])
        else: integrity = ner.check_integrity(exist_category+exist_text, category, [x["entity"] for x in entity])

        if finalAppend:
            appendEntity = {"entity":category,"answer":[category]}
            entity = [appendEntity] +  entity
        entity = appendPunktMars(entity)
        answer = jsonify(_integrity=integrity, _resolved=resolved, entity=entity, category=category)

        if 'readable' in request.json: return answer

        print("ANSWER")
        print(answer)

        return jsonify(answer=answer.get_data(as_text=True))
    except TypeError:
        print("error 1")
        return jsonify(answer=None)
    else:
        print("error 2")
        return jsonify(answer=None)

@app.route('/ner/parse/search/tag', methods=['POST'])
def parse_search_tag():
    text = request.json['query']

    _category, _entity = ner.parse(text,core,cleanTags=False)
    category, entity = ner.clean_tags(_category, _entity)
    category = category[0] if len(category) > 0 else ""
    integrity = ner.check_integrity(text, category, entity)
    entity = nerdb.search(category, entity)
    resolved = isEntityResolved(entity)

    finalEntity = []
    for i,item in enumerate(entity): finalEntity.append({"entity":item["entity"],"answer":item["answer"],"tag":_entity[i][1]})

    return jsonify(_integrity=integrity,_resolved=resolved, entity=finalEntity, category=category)

@app.route('/ner/parse', methods=['POST'])
def parse():
    text = request.json['query']
    category, entity = ner.parse(text,core)
    integrity = ner.check_integrity(text, category, entity)
    return jsonify(_integrity=integrity,entity=entity, category=category)

@app.route('/ner/parse/tag', methods=['POST'])
def parse_tag():
    text = request.json['query']
    category, entity = ner.parse_tags(text,core)
    category = category[0] if len(category)>0 else ""
    return jsonify(entity=entity, category=category)

@app.route('/db/update', methods=['POST'])
def updateDB():
    query = request.json

    if 'url' in query.keys() and 'connecttodb':
        nerdb.setParameters(query["url"],query['connecttodb'])
    nerdb.reConnectToDb()

    return jsonify(answer="ok")

if __name__ == "__main__":
    FLAGS, _TTP_WORD_SPLIT, _buckets,app_options = initialization.getParams()
    if app_options["fixdataset"]: docker_prepare.fix_dataset()
    core = core.Core(FLAGS, _TTP_WORD_SPLIT, _buckets,app_options)
    nerdb = NERDB.NerDB(app_options["url_database"],core,app_options["connect_to_db"])
    ner.setGlobalCore(core)
    app.run(host='0.0.0.0', port=FLAGS.port, debug=True, use_reloader=False, threaded=False)
