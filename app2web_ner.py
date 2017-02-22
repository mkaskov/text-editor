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
global app_options

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
    print("[entity]")
    print("________________________________________________________answered________________________________________________________")
    [print ("[]",x) for x in entity if len(x["answer"])>0]
    print("________________________________________________________not answered________________________________________________________")
    [print("[]", x) for x in entity if len(x["answer"]) == 0]
    print("[/entity]")

def parse_search(text,exist_category,use_exist_category=False):
    category, entity = ner.parse(text,app_options['window_size'])

    if(use_exist_category):
        entity = [category]  + entity

    resolvedEntity = nerdb.search(exist_category, entity)

    if not isResolved(resolvedEntity):
        print("_____________________________PARSE SEARCH________________________________")
        print("[use_exist_category]", use_exist_category)
        print("[exist_category]", exist_category)
        print("[text]", text)
        printAnswerResult(resolvedEntity, category)

    return resolvedEntity, exist_category

def simpleOnPairSearch(entityArr,category):
    for i,entity in enumerate(entityArr):
        if len(entity['answer'])==0 and i+1<len(entityArr) and len(entityArr[i+1]['answer'])==0:
            single_resolve = nerdb.search(category, [entity['entity'] + " " + entityArr[i + 1]['entity']], core)
            if(len(single_resolve[0]['answer'])>0):
                entityArr[i]['entity'] = entity['entity'] + " " + entityArr[i + 1]['entity']
                entityArr[i]['answer'] = single_resolve[0]['answer']
                entityArr[i + 1]['entity'] = ''

    return [x for x in entityArr if len(x['entity'])>0]

def extractNotResolved(entityArr, category, use_exist_category, returnArr):
    if len(entityArr) > 0:
        search_text = ''

        for item in entityArr:
            search_text += " " + item['entity']

        finalEntity = entityArr

        single_resolve = nerdb.search(category, [search_text], core)

        if(len(single_resolve[0]['answer'])>0):
            finalEntity = single_resolve
        else:
            multi_resolve,_ = parse_search(search_text, category, use_exist_category)

            if(isResolvedSimple(multi_resolve)):
                finalEntity = multi_resolve

        for item in finalEntity:
            returnArr.append({'entity': item, 'notresolved': []})

    return returnArr

def hardSecondParse(entityArr,category,use_exist_category):
    arr = [{'entity': None, 'notresolved': []}]

    for entity in entityArr:
        if len(entity['answer']) > 0:
            arr = extractNotResolved(arr[-1]['notresolved'], category, use_exist_category, arr)
            arr.append({'entity': entity, 'notresolved': []})
        else:
            if arr[-1]['entity']:
                arr.append({'entity': None, 'notresolved': []})
            arr[-1]['notresolved'].append(entity)

    arr = extractNotResolved(arr[-1]['notresolved'], category, use_exist_category, arr)
    return [x['entity'] for x in arr if x['entity']]

def secondTryToResolve(entity, category, use_exist_category):
    print("______________________________Second try to resolve_____________________________")

    entity = simpleOnPairSearch(entity, category)
    entity = hardSecondParse(entity, category, use_exist_category)

    print("______________________________Not resolved...._____________________________")
    [print(x) for x in entity if len(x['answer']) == 0]

    return entity

def ner_parse_search(exist_category, exist_text, use_exist_category):
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
        return ner_parse_search(category, text, use_category)
    else:
        isCategoryInBase = nerdb.isInputExist(nerdb.category, category)
        if (isCategoryInBase):
            entity = nerdb.search(category, [cell_text], False)
            resolved = isResolved(entity)

            if not resolved:
                return ner_parse_search(category, text, use_category)

            integrity = isIntegrity(text, category, [x["entity"] for x in entity])

            answer = jsonify(_integrity=integrity, _resolved=resolved, entity=entity, category=category)

            return jsonify(answer=answer.get_data(as_text=True))
        else:
            print("category not in base")
            return ner_parse_search(category, text, use_category)

    return jsonify(answer=None)

@app.route('/ner/parse/search/tag', methods=['POST'])
def parse_search_tag():
    text = request.json['query']

    _category, _entity = ner.parse(text,app_options['window_size'],cleanTags=False)
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
    category, entity = ner.parse(text,app_options['window_size'])
    integrity = isIntegrity(text, category, entity)
    return jsonify(_integrity=integrity,entity=entity, category=category)

@app.route('/ner/parse/tag', methods=['POST'])
def parse_tag():
    text = request.json['query']
    category, entity = ner.parse_tags(text,app_options['window_size'])
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
