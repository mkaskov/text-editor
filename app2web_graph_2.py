import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from util import textUtil as tu
import networkx as nx
from graph import graph_db as GraphDB
from string import punctuation
import re
import docker_prepare
from ner import ner
from nnet import initialization, core

app = Flask(__name__)
CORS(app)

global core
global graphDb

def isResolved(entity):
    for item in entity:
        if len(item['answer'])==0: return False
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
    category = tu.removeSamples(tableRow[text_cell_id-1], core).strip().lower() if text_cell_id >0 else ""

    if len(category)==0:
        _category, _entity = ner.parse(tableRow[text_cell_id].strip(), 30, cleanTags=False)

        if len(_category)>0:
            _category = tu.removeSamples(_category[0][0], core).strip().lower()
            if graphDb.isCatExist(_category):
                category = _category

    text = re.sub("[\s]+", " ", tableRow[text_cell_id]).strip()
    text = re.sub("[\u00ad]+","",text)

    return category, text

def findEntries(category, text):
    base = graphDb.queryByCategory(category)

    finded = []

    for i, item in base.iterrows():
        if item['input'] in text:

            _index = text.find(" "+item['input'])
            zero_index = text.find(item['input'])

            if len(item['input'])>0:
                if _index>0:
                  finded.append({"pos": _index+1, "item": item['input']})
                elif zero_index == 0:
                    finded.append({"pos": 0, "item": item['input']})

    finded = sorted(finded, key=lambda find_: (find_['pos'], len(find_['item'])))

    return finded

def getFindedIndexes(str_len,e_list,delta):
    G = nx.Graph()
    G.add_node(0)
    G.add_node(str_len)

    # Добавление обычных переходов
    for elem in e_list:
        G.add_edge(elem[0], elem[1], weight=elem[1] - elem[0] - delta)

    # Добавление "нулевых" переходов
    for (u1,v1) in G.nodes(data='weight'):
        for (u2,v2) in G.nodes(data='weight'):
            if u1!=u2:
                if not(G.has_edge(u1,u2)):
                    w = 2+abs(u1-u2)**2
                    G.add_edge(u1,u2, weight=w)

        path_ = nx.dijkstra_path(G, 0, str_len)

    len_path = len(path_)

    findedIndexes = []

    for i in range(len_path):
        if i+1<len_path:
            for ind,x in enumerate(e_list):
                if x[0]==path_[i] and x[1]==path_[i+1]:
                    findedIndexes.append(ind)

    return findedIndexes

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

@app.route('/ner/parse/search', methods=['POST'])
def parse_search():
    delta = 0.01

    category,text = extractQueryData(request)

    text_lower = tu.prepreGraphText(text)

    len_text = len(text_lower)

    if len(category)>0:
        finded = findEntries(category, text_lower)
        print ("_____________________________________________________")
        print ("len finded:",len(finded))
        print ("len text:",len_text)
        print ()
        edges = []

        for x in finded:
            edges.append((x['pos'],x['pos']+len(x['item'])))

        print (finded)
        print (edges)

        indexes = getFindedIndexes(len_text,edges,delta)

        entity = []

        categoryBase = graphDb.queryByCategoryDropDuplicates(category)

        for index, x in enumerate(indexes):
            print (finded[x])
            print (indexes[index],edges[x])

            curr_text = ""

            if index > 0 and index < len_text and edges[indexes[index]][0] != edges[indexes[index - 1]][1]:
                curr_text = text[edges[indexes[index - 1]][1]:edges[indexes[index]][0]]

            elif index == 0 and edges[x][0] > 0:
                curr_text = text[0:edges[x][0]]

            elif index + 1 == len_text:
                curr_text = text[edges[indexes[-1]][1] + 1:len_text]

            entity = updateEntity(curr_text, entity, categoryBase)
            entity += graphDb.search(categoryBase, [finded[x]['item']])

        if len(indexes)>1 and edges[indexes[-1]][1]+1<=len_text:
            curr_text = text[edges[indexes[-1]][1]:len_text]
            entity = updateEntity(curr_text, entity, categoryBase)

        if len(indexes) == 1 and edges[indexes[0]][1] != len_text:
            curr_text = text[edges[indexes[0]][1]:len_text]
            entity = updateEntity(curr_text, entity, categoryBase)

        if len(indexes) == 0:
            entity += graphDb.search(categoryBase, [text_lower])

        # Print stats
        print ("category:",category)
        print (text_lower)
        print ()

        _resolved = isResolved(entity)
        _integrity = isInregrity(text_lower, entity)

        print ("resolved:",_resolved)
        print ("integrity:",_integrity)
        for x in entity:
            print (x)

        answer = jsonify(_integrity=_integrity, _resolved=_resolved, entity=entity, category=category)
        return jsonify(answer=answer.get_data(as_text=True))

    else:
        print ("_______________ERROR____________________")
        print ("category:", category)
        print (text_lower)
        answer = jsonify(_integrity=True, _resolved=False, entity=[{"entity": text_lower, "answer": []}], category=category)
        return jsonify(answer=answer.get_data(as_text=True))

if __name__ == "__main__":
    FLAGS, _TTP_WORD_SPLIT, _buckets, app_options = initialization.getParams()
    if app_options["fixdataset"]: docker_prepare.fix_dataset()
    core = core.Core(FLAGS, _TTP_WORD_SPLIT, _buckets, app_options)
    ner.setGlobalCore(core)
    graphDb = GraphDB.GraphDB(app_options["url_database"], core)
    app.run(host='0.0.0.0', port=FLAGS.port, debug=True, use_reloader=False, threaded=False)