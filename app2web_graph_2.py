import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from ner import ner_db as NERDB
from util import textUtil as tu
import networkx as nx
from graph import graph_db as GraphDB

app = Flask(__name__)
CORS(app)

_TTP_WORD_SPLIT = "\[_K_\]|\[_At_\]|\[\|\|\]|\[\/K\]|\[K\]|\[At\]|\[\/At\]|гост\s[\d.]+—?\-?[\d]+|ГОСТ\s[\d.]+—?\-?[\d]+|[а-яА-Я]+\/[а-яА-Я\d]+\.{1}[а-яА-Я\d]+\.{1}|[а-яА-Я]+\/\([^()]+\)|[^\s\d.,!?():;/\\|<>\"\'=–—\-+_*\xA0IV\[\]≥≤~”“_ₒ∙°··\x23«»]+\d?\/[^\s.,!?():;/\\|<>\"\'=–—\-+_*\xA0IV\[\]≥≤~”“_ₒ∙°··\x23«»]+|м{1,2}[\d⁰¹²³⁴⁵⁶⁷⁸⁹]|см[\d⁰¹²³⁴⁵⁶⁷⁸⁹]|дм[\d⁰¹²³⁴⁵⁶⁷⁸⁹]|[a-zA-Zа-яА-ЯёЁ]*[^\s\d.\\!?,:;()\"\'<>%«»±^…–—\-*=/+\xA0@·∙\[\]°ₒ”“·≥≤~_\x23]|[\d()\\!?\'\"<>%,:;±«»^…–—\-*=/+@·∙\[\]°ₒ”“·≥≤~_\x23]|\.{3}|\.{1}"
url_database='ttpuser:ttppassword@db:5432/ttp'

global core
global graphDb

class Core(object):
    global _TTP_WORD_SPLIT

    def __init__(self, _TTP_WORD_SPLIT_STRING):
        self._TTP_WORD_SPLIT = re.compile(_TTP_WORD_SPLIT_STRING)

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

    return category, tableRow[text_cell_id].strip()

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

@app.route('/ner/parse/search', methods=['POST'])
def parse_search():
    delta = 0.01

    category,text = extractQueryData(request)
    category = re.sub("[\s]", " ", category)
    text = re.sub("[\s]", " ", text).strip()
    text_lower = re.sub("[\s]", " ", text).strip().lower()
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

            if index > 0 and index < len_text:
                if edges[indexes[index]][0] != edges[indexes[index - 1]][1]:
                    curr_text = text[edges[indexes[index - 1]][1]:edges[indexes[index]][0]]
                    entity += graphDb.search(categoryBase, [curr_text])

            elif index == 0 and edges[x][0] > 0:
                curr_text = text[0:edges[x][0]]
                entity += graphDb.search(categoryBase, [curr_text])

            elif index + 1 == len_text:
                curr_text = text[edges[indexes[-1]][1] + 1:len_text]
                entity += graphDb.search(categoryBase, [curr_text])

            entity += graphDb.search(categoryBase, [finded[x]['item']])

        if len(indexes)>1 and edges[indexes[-1]][1]+1<=len_text:
            entity += graphDb.search(categoryBase, [text[edges[indexes[-1]][1]:len_text]])

        if len(indexes) == 1 and edges[indexes[0]][1] != len_text:
            entity += graphDb.search(categoryBase, [text[edges[indexes[0]][1]:len_text]])

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
    core = Core(_TTP_WORD_SPLIT)
    graphDb = GraphDB.GraphDB(url_database, core)
    app.run(host='0.0.0.0', port=5003, debug=True, use_reloader=False, threaded=False)