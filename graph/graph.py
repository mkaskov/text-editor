import networkx as nx

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