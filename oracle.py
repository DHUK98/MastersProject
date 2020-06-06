import networkx as nx
import ujson as json
from tqdm import tqdm
from networkx.readwrite import json_graph
from sklearn.ensemble import RandomForestClassifier
from eden.graph import vectorize
import os


def oracle(G):
    nodes = G.nodes(data=True)

    right = [
        (id, data)
        for id, data in nodes
        if data["label"] in ["cat"] and data["svec"]["x"] > 50
        #  and data["svec"]["w"] * data["svec"]["h"] > 4000
    ]
    left = [
        (id, data)
        for id, data in nodes
        if data["label"] in ["cat"] and data["svec"]["x"] + data["svec"]["w"] < 50
        #  and data["svec"]["w"] * data["svec"]["h"] > 4000
    ]
    if len(right) > 1 and len(left) < 1:
        return 1
    return 0


if __name__ == "__main__":
    graphs = []
    count = 0
    for entry in tqdm(os.scandir("data/filtered/cat-zebra")):
        if entry.name.endswith("json"):
            with open(entry, "r") as f:
                graphs.append(json_graph.node_link_graph(json.loads(f.read())))
        count += 1
    labels = []
    num_train_graphs = int(len(graphs) * 0.25)
    num_test_graphs = len(graphs) - num_train_graphs
    train_graphs = graphs[:num_train_graphs]
    test_graphs = graphs[-num_test_graphs:]
    for i in range(len(graphs)):
        ora = oracle(graphs[i])
        #  if ora == 1:
        #  print(graphs[i].graph["url"])
        labels.append(ora)
    train_labels = labels[:num_train_graphs]
    test_labels = labels[-num_test_graphs:]

    X = vectorize(graphs, complexity=3, nbits=16)
    train_X = X[:num_train_graphs]
    test_X = X[-num_test_graphs:]

    clf = RandomForestClassifier(n_jobs=-1, random_state=100, n_estimators=1000)
    clf.fit(train_X, train_labels)

    print(clf.score(test_X, test_labels))
