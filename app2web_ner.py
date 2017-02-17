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

def isResolved(entity):
    for item in entity:
        if len(item['answer'])==0: return False
    return True

def isResolvedSimple(entity):
    for item in entity:
        if len(item['answer'])>0: return True
    return False

def isIntegrity(original_text, category, entity):
    final_text = "".join(du.tokenizer_tpp(tu.removeSamples(category + "".join(entity), core), core._TTP_WORD_SPLIT))
    original_text = "".join(du.tokenizer_tpp(tu.removeSamples(original_text, core), core._TTP_WORD_SPLIT))

    # if not original_text == final_text:
    #     print("\n__________________________Integrity False__________________________")
    #     print(original_text)
    #     print(final_text)

    return original_text == final_text

def getQueryData(request):
    query = request.json['query']
    query = tu.decode_from_java(query)

    if query.find('[/cellid]') == -1:  query = "[cellid]-1[/cellid] " + query

    input_data = query[query.index('[/cellid]') + len("[/cellid]"):]
    text_cell_id = int(query[len("[cellid]"):query.index('[/cellid]')])

    return input_data,text_cell_id

def extractQueryData(input_data, text_cell_id):
    CELL_SPLIT = re.compile("\[\|\|\]")

    #clear input text
    input_data = re.sub("[\s]+", " ", input_data)
    input_data = tu.replace_celsius(input_data)

    tableRow = re.split(CELL_SPLIT, input_data.strip())

    category = ""
    category_cell_id = -1

    # print ("_______________________Splitted text_______________________________________")
    # [print("[]",x.strip(),"[len]",len(x.strip())) for x in tableRow]

    for i,cat in enumerate(tableRow):
        if nerdb.isInputExist(nerdb.category,cat):
            category_cell_id = i
            category = tu.removeSamples(cat,core).strip()

    if len(category)==0:
        if nerdb.isInputExist(nerdb.category,tableRow[0]): category = tu.removeSamples(tableRow[0],core).strip()

    text = tableRow[text_cell_id].strip()

    return category,text,category_cell_id,tableRow

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

def prepareForSearch(input_data, text_cell_id):
    use_exist_category = False
    exist_category = ""

    if (text_cell_id > -1):
        exist_category, exist_text,category_cell_id,row = extractQueryData(input_data, text_cell_id)
        if len(exist_text.strip()) > 0:
            # text = exist_category + " " + exist_text
            text = exist_text
            if(len(exist_category.strip())>0):
                use_exist_category = True
    else:
        text = re.sub("\[\|\|\]", " ", input_data)
        category_cell_id = -1
        row = []
        exist_text = text
    # print ("[user exist category]",use_exist_category,exist_category)
    return exist_category,text,use_exist_category,category_cell_id,row,exist_text

def findCategory(category,exist_category,entity):
    use_exist_category = False

    if len(category) > 0:
        print("________________________________________________________1")
        if nerdb.isInputExist(nerdb.category, category):
            use_exist_category = True
            category = tu.removeSamples(category, core).strip()
            exist_category = category
            print("________________________________________________________2")

    elif nerdb.isInputExist(nerdb.category, entity[0]):
        use_exist_category = True
        category = tu.removeSamples(entity[0], core).strip()
        exist_category = category
        if len(entity) > 0:
            entity = entity[1:]
        else:
            entity = []
        print("________________________________________________________3")

    return category,exist_category,use_exist_category,entity

def printAnswerResult(entity,category):
    print("[category]", category)
    # print("________________________________________________________answered________________________________________________________")
    # print("[entity]")
    # for ent in entity:
    #     if len(ent["answer"])>0:
    #         print ("[]",ent)
    # print("[/entity]")
    print("________________________________________________________not answered________________________________________________________")
    print("[entity]")
    for ent in entity:
        if len(ent["answer"]) == 0:
            print("[]", ent["entity"])
    print("[/entity]")

def parse_search(text,exist_category,use_exist_category=False):
    category, entity = ner.parse(text,core)

    checkFullEntity = nerdb.search(exist_category, entity)

    if (isResolved(checkFullEntity)):
        return checkFullEntity, exist_category
    # else:
    #     print("_____________________________PARSE SEARCH________________________________")
    #     print("[use_exist_category]", use_exist_category)
    #     print("[exist_category]", exist_category)
    #     print("[text]", text)
    #     printAnswerResult(checkFullEntity, category)

    if not use_exist_category:
        category, exist_category, use_exist_category, entity = findCategory(category,exist_category,entity)

    ner_category_raw ="".join([x for x in du.tokenizer_tpp(category, core._TTP_WORD_SPLIT)])
    exist_category_raw = "".join([x for x in du.tokenizer_tpp(exist_category, core._TTP_WORD_SPLIT)])

    entity_raw_0 = ""

    if len(entity) > 0:
        entity_raw_0 = "".join([x for x in du.tokenizer_tpp(entity[0], core._TTP_WORD_SPLIT)])

    categorySpace = " ".join([x for x in du.tokenizer_tpp(category, core._TTP_WORD_SPLIT)])
    existCategorySpace = " ".join([x for x in du.tokenizer_tpp(exist_category, core._TTP_WORD_SPLIT)])

    print("_____________________________________________________________")
    if(len(checkFullEntity[0]['answer'])>0):
        category = exist_category
    elif use_exist_category:
        if ner_category_raw==exist_category_raw and len(exist_category_raw)>0:
           print("var 0")
        elif entity_raw_0==exist_category_raw:
           if len(entity) > 0:
             entity = entity[1:]
             category = exist_category
           print ("var 1")
        elif exist_category_raw in ner_category_raw and len(exist_category_raw)>0:
            entity = [category]+entity
            if len(entity) > 0:
                entity[0] = entity[0].strip()[len(existCategorySpace):].strip()
                category = exist_category
            print ("var 2")
        elif exist_category_raw in (ner_category_raw+entity_raw_0) and len(ner_category_raw)>0:
            print("var 3")
            if len(entity) > 0:
                entity[0] = categorySpace +" " + entity[0].strip()
                entity[0] = entity[0].strip()[len(existCategorySpace):].strip()
                category = exist_category
        elif len(ner_category_raw)==0:
            if ( tu.removeSamples(exist_category, core).strip())==( tu.removeSamples( entity[0], core).strip()):
                category = entity[0]
                if len(entity)>0:
                    entity = entity[1:]
                else:
                    entity = []
            else:
                if exist_category_raw in entity_raw_0:
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

    if len(entity) > 0 and len(entity[0].strip()) == 0:
            entity = entity[1:]

    entity = nerdb.search(category, entity)

    # print("________________________________________________________after use exist________________________________________________________")
    # printAnswerResult(entity,category)

    return entity, category

def simpleOnPairSearch(entityArr,category):
    #simpe pair search
    for i,ent in enumerate(entityArr):
        if i+1<len(entityArr) and len(entityArr[i+1]['answer'])==0:
            try_to_find_full = nerdb.search(category, [entityArr[i]['entity'] + " " + entityArr[i + 1]['entity']], core)
            if(len(try_to_find_full[0]['answer'])>0):
                entityArr[i]['entity'] = entityArr[i]['entity'] + " " + entityArr[i + 1]['entity']
                entityArr[i]['answer'] = try_to_find_full[0]['answer']
                entityArr[i + 1]['entity'] = ''

    return clearFromEmpty(entityArr)

def clearFromEmpty(entity):
    return [x for x in entity if len(x['entity'])>0]

def extractNotResolved(entityArr,category,use_exist_category,refactorArr):
    if len(entityArr) > 0:
        temp_text = ''

        for item in entityArr:
            temp_text += item['entity']

        temp_resolve,_ = parse_search(temp_text, category, use_exist_category)

        if(isResolvedSimple(temp_resolve)):
            for x in temp_resolve:
                refactorArr.append({'entity':x,'notresolved':[]})
        else:
            for item in entityArr:
                refactorArr.append({'entity':item, 'notresolved': []})

    return refactorArr

def hardSecondParse(entityArr,category,use_exist_category):
    refactorArr = [{'entity': None, 'notresolved': []}]

    for entity in entityArr:
        if len(entity['answer']) > 0:
            refactorArr = extractNotResolved(refactorArr[-1]['notresolved'], category, use_exist_category, refactorArr)
            refactorArr.append({'entity': entity, 'notresolved': []})
        else:
            if refactorArr[-1]['entity']:
                refactorArr.append({'entity': None, 'notresolved': []})
            refactorArr[-1]['notresolved'].append(entity)

    refactorArr = extractNotResolved(refactorArr[-1]['notresolved'], category, use_exist_category, refactorArr)
    return [x['entity'] for x in refactorArr if x['entity']]

def secondTryToResolve(entityArr, category, use_exist_category):
    print("______________________________Second try to resolve_____________________________")

    entityArr = simpleOnPairSearch(entityArr,category)
    entityArr = hardSecondParse(entityArr,category,use_exist_category)

    [print(x) for x in entityArr]

    # newText = ""
    # newEntity = []
    # lastEnd = 0
    # lastStart = -1
    #
    # for i, item in enumerate(entityArr):
    #     if len(item["answer"]) == 0:
    #         if lastStart == -1: lastStart = i
    #         newText += " " + item["entity"]
    #     elif len(newText) > 0:
    #         _entity = nerdb.search(category, [newText], core)
    #         resolved = isResolved(_entity)
    #
    #         _entity2, _category2 = parse_search(newText, category, use_exist_category)
    #         resolved2 = isResolved(_entity2)
    #
    #         if resolved2:
    #             newText = ""
    #             newEntity += entityArr[lastEnd:lastStart] + _entity2
    #             lastEnd = i + 1
    #             lastStart = -1
    #         elif resolved:
    #             newText = ""
    #             newEntity += entityArr[lastEnd:lastStart] + _entity
    #             lastEnd = i + 1
    #             lastStart = -1
    #         else:
    #             _entity, _category = parse_search(category + " " + newText, category, use_exist_category)
    #
    #             print("-----------------------------------------------")
    #             print("[parsed second category]", _category)
    #             print("[parsed second text]")
    #             for x in _entity:
    #                 print("--------------------------------")
    #                 print("[Answer second]", x["answer"])
    #                 print("[Entity second]", x["entity"])
    #             print("[/parsed second text]")
    #
    #             _resolved = isResolved(_entity)
    #             _integrity = isIntegrity(newText, "", [x["entity"] for x in _entity])
    #
    #             newText = ""
    #
    #             print("\n[resolved second]", _resolved)
    #             print("[integrity second]", _integrity)
    #
    #             if _integrity and _resolved:
    #                 print("[second try sucessfull]", i)
    #                 newEntity += entityArr[lastEnd:lastStart] + _entity
    #                 lastEnd = i + 1
    #                 lastStart = -1
    #
    #                 print("[current new entity]")
    #                 for i, item in enumerate(newEntity):
    #                     print(i, item["entity"])
    #             else:
    #                 lastStart = -1
    #
    # if len(newText) > 0:
    #     _entity = nerdb.search(category, [newText], core)
    #     resolved = isResolved(_entity)
    #
    #     _entity2, _category2 = parse_search(newText, category, use_exist_category)
    #     resolved2 = isResolved(_entity2)
    #
    #     if resolved2:
    #         newEntity += entityArr[lastEnd:lastStart] + _entity2
    #         entityArr = newEntity
    #     elif resolved:
    #         newEntity += entityArr[lastEnd:lastStart] + _entity
    #         entityArr = newEntity
    #     else:
    #         _entity, _category = parse_search(category + " " + newText, category, use_exist_category)
    #
    #         print("-----------------------------------------------")
    #         print("[parsed final category]", _category)
    #         print("[parsed final text]")
    #         for x in _entity:
    #             print("--------------------------------")
    #             print("[Answer final]", x["answer"])
    #             print("[Entity final]", x["entity"])
    #         print("[/parsed final text]")
    #
    #         _resolved = isResolved(_entity)
    #         _integrity = isIntegrity(newText, "", [x["entity"] for x in _entity])
    #
    #         print("\n[resolved final]", _resolved)
    #         print("[integrity final]", _integrity)
    #
    #         if _integrity and _resolved:
    #             print("[second try sucessfull]", i)
    #             newEntity += entityArr[lastEnd:lastStart] + _entity
    #
    #             print("[current new entity]")
    #             for i, item in enumerate(newEntity):
    #                 print(i, item["entity"])
    #
    #             entityArr = newEntity
    #
    # elif len(newEntity) > 0:
    #     newEntity += entityArr[lastEnd - 1:len(entityArr)]
    #     entityArr = newEntity





    # for i, item in enumerate(entityArr):
    #     print(i, item["entity"])
    #     print(" - ", item["answer"])

    return entityArr

def ner_parse_search(exist_category, exist_text, use_exist_category,category_cell_id, row, cell_text):
    check_text = exist_text if use_exist_category else exist_category + exist_text

    # try:
    entity, category = parse_search(exist_text,exist_category,use_exist_category)

    resolved = isResolved(entity)
    integrity = isIntegrity(check_text, category, [x["entity"] for x in entity])

    # if not resolved and integrity:
    if not resolved:
        entity = secondTryToResolve(entity,category,use_exist_category)

    # print ("_______________________________Final check__________________________________")
    resolved = isResolved(entity)
    integrity = isIntegrity(check_text, category, [x["entity"] for x in entity])

    if len(exist_category) == 0 and len(category) > 0:
        entity = [{"entity":category,"answer":[category]}] +  entity

    entity = appendPunktMars(entity)

    answer = jsonify(_integrity=integrity, _resolved=resolved, entity=entity, category=category)

    if 'readable' in request.json: return answer

    return jsonify(answer=answer.get_data(as_text=True))
    # except TypeError:
    #     return jsonify(answer=None)
    # else:
    #     return jsonify(answer=None)

@app.route('/ner/parse/search', methods=['POST'])
def entry_point():
    input_data, text_cell_id = getQueryData(request)
    category, text, use_category, category_cell_id, row, cell_text = prepareForSearch(input_data, text_cell_id)

    if len(text.strip()) > nerdb.maxLenChar or text_cell_id == -1 or len(row) < 2:
        return ner_parse_search(category, text, use_category, category_cell_id, row, cell_text)
    else:
        isCategoryInBase = nerdb.isInputExist(nerdb.category, category)
        if (isCategoryInBase):
            entity = nerdb.search(category, [cell_text], False)
            resolved = isResolved(entity)

            if not resolved:
                return ner_parse_search(category, text, use_category, category_cell_id, row, cell_text)

            integrity = isIntegrity(text, category, [x["entity"] for x in entity])

            answer = jsonify(_integrity=integrity, _resolved=resolved, entity=entity, category=category)

            return jsonify(answer=answer.get_data(as_text=True))
        else:
            print("category not in base")
            return ner_parse_search(category, text, use_category,
                                    category_cell_id, row, cell_text)

    return jsonify(answer=None)

@app.route('/ner/parse/search/tag', methods=['POST'])
def parse_search_tag():
    text = request.json['query']

    _category, _entity = ner.parse(text,core,cleanTags=False)
    category, entity = ner.clean_tags(_category, _entity)
    category = category[0] if len(category) > 0 else ""
    integrity = isIntegrity(text, category, entity)
    entity = nerdb.search(category, entity)
    resolved = isResolved(entity)

    finalEntity = []
    for i,item in enumerate(entity): finalEntity.append({"entity":item["entity"],"answer":item["answer"],"tag":_entity[i][1]})

    return jsonify(_integrity=integrity,_resolved=resolved, entity=finalEntity, category=category)

@app.route('/ner/parse', methods=['POST'])
def parse():
    text = request.json['query']
    category, entity = ner.parse(text,core)
    integrity = isIntegrity(text, category, entity)
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
