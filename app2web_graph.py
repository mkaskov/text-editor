import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from ner import ner_db as NERDB
from util import textUtil as tu
import networkx as nx

# Obtain the flask app object
app = Flask(__name__)
CORS(app)

_TTP_WORD_SPLIT = "\[_K_\]|\[_At_\]|\[\|\|\]|\[\/K\]|\[K\]|\[At\]|\[\/At\]|гост\s[\d.]+—?\-?[\d]+|ГОСТ\s[\d.]+—?\-?[\d]+|[а-яА-Я]+\/[а-яА-Я\d]+\.{1}[а-яА-Я\d]+\.{1}|[а-яА-Я]+\/\([^()]+\)|[^\s\d.,!?():;/\\|<>\"\'=–—\-+_*\xA0IV\[\]≥≤~”“_ₒ∙°··\x23«»]+\d?\/[^\s.,!?():;/\\|<>\"\'=–—\-+_*\xA0IV\[\]≥≤~”“_ₒ∙°··\x23«»]+|м{1,2}[\d⁰¹²³⁴⁵⁶⁷⁸⁹]|см[\d⁰¹²³⁴⁵⁶⁷⁸⁹]|дм[\d⁰¹²³⁴⁵⁶⁷⁸⁹]|[a-zA-Zа-яА-ЯёЁ]*[^\s\d.\\!?,:;()\"\'<>%«»±^…–—\-*=/+\xA0@·∙\[\]°ₒ”“·≥≤~_\x23]|[\d()\\!?\'\"<>%,:;±«»^…–—\-*=/+@·∙\[\]°ₒ”“·≥≤~_\x23]|\.{3}|\.{1}"
url_database='ttpuser:ttppassword@localhost:5432/ttp'

global core
global nerdbGraph
global nerdb

class Core(object):
    global _TTP_WORD_SPLIT

    def __init__(self, _TTP_WORD_SPLIT_STRING):
        self._TTP_WORD_SPLIT = re.compile(_TTP_WORD_SPLIT_STRING)

def getQueryData(request):
    query = request.json['query']
    query = tu.decode_from_java(query)

    if query.find('[/cellid]') == -1:  query = "[cellid]-1[/cellid] " + query

    input_data = query[query.index('[/cellid]') + len("[/cellid]"):]
    text_cell_id = int(query[len("[cellid]"):query.index('[/cellid]')])

    return input_data, text_cell_id

def extractQueryData(input_data, text_cell_id):
    CELL_SPLIT = re.compile("\[\|\|\]")

    #clear input text
    input_data = re.sub("[\s]+", " ", input_data)
    input_data = tu.replace_celsius(input_data)

    tableRow = re.split(CELL_SPLIT, input_data.strip())

    category = ""
    category_cell_id = -1

    for i,cat in enumerate(tableRow):
        if nerdbGraph.isInputExist(nerdbGraph.category, cat):
            category_cell_id = i
            category = tu.removeSamples(cat,core).strip()

    if len(category)==0:
        if nerdbGraph.isInputExist(nerdbGraph.category, tableRow[0]): category = tu.removeSamples(tableRow[0], core).strip()

    text = tableRow[text_cell_id].strip()

    return category,text,category_cell_id,tableRow

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

def extractData(request,delta):
    input_data, text_cell_id = getQueryData(request)
    category, text, use_category, category_cell_id, row, cell_text = prepareForSearch(input_data, text_cell_id)
    base = nerdbGraph.getBaseByCat(category)

    finded = []

    cell_text = tu.getRawSpace(cell_text, core)

    for i, item in base.iterrows():
        if item['input'] in cell_text:
            finded.append({"pos": cell_text.index(item['input']), "item": item})

    finded = sorted(finded, key=lambda find_: (find_['pos'], len(find_['item']['input'])))

    source_array = cell_text.split(" ")

    finded_arrays = [x['item']['input'].split(' ') for x in finded]

    finded_arrays_index = []
    finded_arrays_text = []

    for x in finded_arrays:
        if x[0] in source_array:
            startIndex = source_array.index(x[0])
            endIndex = startIndex
            subFinded = True
            for item in x:
                if item == source_array[endIndex]:
                    endIndex += 1
                else:
                    subFinded = False


            if (subFinded):
                finded_arrays_index.append((startIndex, endIndex, endIndex - startIndex - delta))
                finded_arrays_text.append(x)


    return category,cell_text,source_array,finded_arrays_index,finded_arrays_text

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

def isResolved(entity):
    for item in entity:
        if len(item['answer'])==0: return False
    return True

def isInregrity(source_arr,entity):
    entity_arr = [tu.getRaw(x['entity'],core) for x in entity]

    source_txt = re.sub("[\s]+", "", tu.getRaw(" ".join(source_arr),core))
    entity_txt = re.sub("[\s]+","","".join(entity_arr))

    isInregrity = source_txt==entity_txt
    if not isInregrity:
        print (source_txt)
        print (entity_txt)

    return isInregrity

@app.route('/ner/parse/search', methods=['POST'])
def parse_search():
    delta = 0.01
    category,text,text_arr,edges,entity_arr = extractData(request,delta)

    str_len = len(text_arr)
    indexes = getFindedIndexes(str_len,edges,delta)

    entity = []
    len_finded = len(indexes)

    print ("")
    print ("__________________________________________________________________________")

    for index,x in enumerate(indexes):

        if index>0 and index<len_finded:
            if edges[indexes[index]][0]!=edges[indexes[index-1]][1]:
                curr_arr = text_arr[edges[indexes[index - 1]][1]:edges[indexes[index]][0]]
                curr_text = " ".join(curr_arr)
                entity += nerdb.search(category, [curr_text])

        elif index==0 and edges[x][0]>0:
            curr_arr = text_arr[0:edges[x][0]]
            curr_text = " ".join(curr_arr)
            entity += nerdb.search(category, [curr_text])

        elif index+1==str_len:
            curr_arr = text_arr[edges[indexes[-1]][1] + 1:str_len]
            curr_text = " ".join(curr_arr)
            entity += nerdb.search(category, [curr_text])

        curr_arr = entity_arr[x]
        curr_text = " ".join(curr_arr)
        entity += nerdb.search(category,[curr_text])

        print ("[",x,"]",edges[x],curr_text)

    if len(indexes)>1 and edges[indexes[-1]][1]+1<str_len:
        entity+=nerdb.search(category, [" ".join(text_arr[edges[indexes[-1]][1]:str_len])])

    if len(indexes)==1 and edges[indexes[0]][1]!=str_len:
        entity += nerdb.search(category, [" ".join(text_arr[edges[indexes[0]][1]:str_len])])

    if len(indexes)==0:
        entity += nerdb.search(category, [" ".join(text_arr)])

    _resolved = isResolved(entity)
    _integrity = isInregrity(text_arr,entity)

    if _resolved and _integrity:
        print ("")
    else:
        print ("")
        print ("len text arr:",len(text_arr))
        print (text_arr)
        print ("len findedindex: ",len(indexes))
        print ("findedindex: ",indexes)
        print ("len edge list: ",len(edges))
        print ("edge list",edges)
        print ("entitylist")
        print (entity_arr)
        print ("isResolved:",_resolved)
        print ("isIntegrity:",_integrity)


    answer = jsonify(_integrity=_integrity, _resolved=_resolved, entity=entity, category=category)
    return jsonify(answer=answer.get_data(as_text=True))

if __name__ == "__main__":
    core = Core(_TTP_WORD_SPLIT)
    nerdb = NERDB.NerDB(url_database, core, connectToDdBool=True)
    nerdbGraph = NERDB.NerDB(url_database, core, connectToDdBool=True, isGraph=True)
    app.run(host='0.0.0.0', port=5003, debug=True, use_reloader=False, threaded=False)
