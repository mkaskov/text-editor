from flask import Flask, request, jsonify
from flask_cors import CORS
from util import textUtil as tu

from graph import graph_db as GraphDB
from string import punctuation
import re
import docker_prepare
from ner import ner
from nnet import initialization, core
from graph import graph

app = Flask(__name__)
CORS(app)

global core
global graphDb

def isResolved(entity):
    for item in entity:
        if len(item['answer'])==0: return False
    return True

def isFullNotResolved(entity):
    for item in entity:
        if len(item['answer'])>0: return False
    return True

def isInregrity(source_txt,entity):
    entity_arr = [x['entity'] for x in entity]
    entity_txt = "".join(entity_arr).lower()

    isInregrity = source_txt==entity_txt
    if not isInregrity:
        print (source_txt)
        print (entity_txt)

    return isInregrity

def getQueryData(request):
    query = request.json['query']
    query = tu.decode_from_java(query)

    if query.find('[/cellid]') == -1:  query = "[cellid]-1[/cellid] " + query

    input_data = query[query.index('[/cellid]') + len("[/cellid]"):]
    text_cell_id = int(query[len("[cellid]"):query.index('[/cellid]')])

    return input_data, text_cell_id

def extractQueryData(request):
    input_data, text_cell_id = getQueryData(request)
    CELL_SPLIT = re.compile("\[\|\|\]")
    tableRow = re.split(CELL_SPLIT, input_data.strip())

    text = tu.regexClean(tableRow[text_cell_id])

    category = tu.removeSamples(tableRow[text_cell_id-1], core).strip().lower() if text_cell_id >0 else ""

    if not graphDb.isCatExist(category):
        for i in range(0, text_cell_id):
            newCat = tu.removeSamples(tableRow[i], core).strip().lower()
            if len(newCat)>0 and not newCat.isdigit():
                if graphDb.isCatExist(newCat):
                    category = newCat
                    break

    if len(category)==0:
        catbase,maxLen = graphDb.getCategoryList()

        cat_search = text[0:maxLen+10].lower()

        finded = []

        for i,item in catbase.iterrows():
            if item['category'] in cat_search:
                index = cat_search.find(item['category'])
                finded.append({"pos":index,"item":item['category']})

        finded = sorted(finded, key=lambda find_: (find_['pos'], len(find_['item'])))

        for x in finded:
            if x['pos']==0:
                category = x['item']
            elif len(category)>0:
                break
            else:
                category = x['item']
                break

    #extra search text
    if text_cell_id>1:
        extra_text = tableRow[text_cell_id-1:text_cell_id+1]
        extra_id = 1
    else:
        extra_text = [tableRow[text_cell_id]]
        extra_id = 0

    if text_cell_id+1<len(tableRow):
        extra_text.append(tableRow[text_cell_id+1])

    for i,item in enumerate(extra_text):
        extra_text[i] = tu.regexClean(extra_text[i])

    return category, text,extra_text,extra_id

def findEntries(category, text):
    base = graphDb.queryByCategory(category)

    finded = []

    for i, item in base.iterrows():
        if len(item['input'])>0 and item['input'] in text:
            # _index = text.find(item['input'])
            # finded.append({"pos": _index, "item": item['input']})
            indexes = [m.start() for m in re.finditer(re.escape(item['input']), text)]
            if len(indexes) == 0:
                indexes = [text.find(item['input'])]
            for x in indexes:
                finded.append({"pos": x, "item": item['input']})

    return sorted(finded, key=lambda find_: (find_['pos'], len(find_['item'])))

def isEmptyEntity(text):
    curr_test = re.sub("[\s\u00ad]+", "", text)
    curr_test = [x for x in curr_test if x not in punctuation]
    return len(curr_test)==0

def updateEntity(curr_text,entity,categoryBase):
    if len(curr_text)==0:
        return entity

    if isEmptyEntity(curr_text) and len(entity) > 0:
        entity[-1]['entity'] = entity[-1]['entity'] + curr_text
        for index_a, answer in enumerate(entity[-1]['answer']):
            entity[-1]['answer'][index_a] = entity[-1]['answer'][index_a] + curr_text
    else:
        entity += graphDb.search(categoryBase, [curr_text])

    return entity

def resolveText(category, text,debug=True):
    delta = 0.01
    text = tu.prepreGraphText(text)
    len_text = len(text)

    finded = findEntries(category, text)

    edges = []

    for x in finded:
        edges.append((x['pos'], x['pos'] + len(x['item'])))

    indexes = graph.getFindedIndexes(len_text, edges, delta)

    entity = []

    categoryBase = graphDb.queryByCategoryDropDuplicates(category)

    for index, x in enumerate(indexes):
        if debug:
            print (finded[x])
            print (indexes[index], edges[x])

        curr_text = ""

        if index > 0 and index < len_text and edges[indexes[index]][0] != edges[indexes[index - 1]][1]:
            curr_text = text[edges[indexes[index - 1]][1]:edges[indexes[index]][0]]

        elif index == 0 and edges[x][0] > 0:
            curr_text = text[0:edges[x][0]]

        elif index + 1 == len_text:
            curr_text = text[edges[indexes[-1]][1] + 1:len_text]

        entity = updateEntity(curr_text, entity, categoryBase)
        entity += graphDb.search(categoryBase, [finded[x]['item']])

    if len(indexes) > 1 and edges[indexes[-1]][1] + 1 <= len_text:
        curr_text = text[edges[indexes[-1]][1]:len_text]
        entity = updateEntity(curr_text, entity, categoryBase)

    if len(indexes) == 1 and edges[indexes[0]][1] != len_text:
        curr_text = text[edges[indexes[0]][1]:len_text]
        entity = updateEntity(curr_text, entity, categoryBase)

    if len(indexes) == 0:
        entity += graphDb.search(categoryBase, [text])

    _resolved = isResolved(entity)
    _integrity = isInregrity(text, entity)

    if debug:
        print ("_____________________________________________________")
        print ("len finded:", len(finded))
        print ("len text:", len_text)
        print ()
        print (finded)
        print (edges)

        # Print stats
        print ("category:", category)
        print (text)
        print ()

        print ("resolved:", _resolved)
        print ("integrity:", _integrity)
        for x in entity:
            print (x)

    return entity,_resolved,_integrity

def resolveTextExtra(category,extra_text,extra_id):
    entity, _resolved, _integrity = resolveText(category, " ".join(extra_text))

    if len(entity[0]['answer']) > 0:
        if extra_id == 1:
            for i, item in enumerate(entity[0]['answer']):
                _index = item.lower().find(extra_text[0].lower())
                if _index == 0:
                    clear_text = item[len(extra_text[0]):len(item)]
                    entity[0]['answer'][i] = clear_text.strip()

        if extra_id + 1 < len(extra_text):
            extra_end = extra_text[extra_id + 1].strip()
            len_end = len(extra_end)

            for i, item in enumerate(entity[0]['answer']):
                extra_ent = item.strip()
                len_ent = len(extra_ent)
                if extra_ent[len_ent - len_end:] == extra_end:
                    entity[0]['answer'][i] = extra_ent[0:len_ent - len_end]

    if len(entity)>1 and extra_id + 1 < len(extra_text):
        last_ent = entity[-1]['entity'].strip()
        if last_ent==extra_text[-1]:
            entity=entity[:len(entity)-1]

    _resolved = isResolved(entity)

    # print ("extra________________")
    # print (extra_text)
    # for x in entity:
    #     print (x)

    return entity, _resolved, _integrity

@app.route('/ner/parse/search', methods=['POST'])
def parse_search():

    category,text,extra_text,extra_id = extractQueryData(request)

    if len(category)>0:

        entity, _resolved, _integrity = resolveText(category,text)

        if isFullNotResolved(entity):
            entity, _resolved, _integrity = resolveTextExtra(category,extra_text,extra_id)

        answer = jsonify(_integrity=_integrity, _resolved=_resolved, entity=entity, category=category)
        return jsonify(answer=answer.get_data(as_text=True))

    else:
        print ("_______________ERROR____________________")
        print ("category:", category)
        print (text)
        answer = jsonify(_integrity=True, _resolved=False, entity=[{"entity": text, "answer": []}], category=category)
        return jsonify(answer=answer.get_data(as_text=True))

if __name__ == "__main__":
    FLAGS, _TTP_WORD_SPLIT, _buckets, app_options = initialization.getParams()
    if app_options["fixdataset"]: docker_prepare.fix_dataset()
    core = core.Core(FLAGS, _TTP_WORD_SPLIT, _buckets, app_options)
    ner.setGlobalCore(core)
    graphDb = GraphDB.GraphDB(app_options["url_database"], core)
    app.run(host='0.0.0.0', port=FLAGS.port, debug=True, use_reloader=False, threaded=False)