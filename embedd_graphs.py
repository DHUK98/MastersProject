import os
from eden.graph import vectorize
import networkx as nx
from networkx.readwrite import json_graph
import ujson as json

if __name__ == "__main__":
    graphs = []
    for entry in os.scandir("data/filtered/zebra"):
        if entry.name.endswith("json"):
            graphs.append(json_graph.node_link_graph(json.loads(open(entry).read())))

    print(graphs[0].edges(data=True))
    print()
    print(nx.is_connected(graphs[0].to_undirected()))
    print((graphs[0].nodes(data=True)))
    X = vectorize(graphs, complexity=2, nbits=16, discrete=False)
    print(X)
