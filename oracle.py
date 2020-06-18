from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import TruncatedSVD
from sklearn.linear_model import SGDClassifier
from sklearn.manifold import TSNE
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph
import networkx as nx
from eden.graph import vectorize
from tqdm import tqdm
import ujson as json
import numpy as np
from collections import Counter
import os

from sklearn import metrics
from sklearn.neighbors import NearestNeighbors


def oracle2(G):
    nodes = G.nodes(data=True)
    edges = G.edges(data=True)
    zebras = [(id, data["label"]) for id, data in nodes if data["label"] in ["cat"]]
    objects = [(id, data["label"]) for id, data in nodes if data["label"] in ["cat"]]
    #  for z, clab in zebras:
    #  for o, olab in objects:
    #  if z == o:
    #  continue
    #  if G.has_edge(z, o):
    #  return 1
    return len(zebras)


def oracle1(G):
    nodes = G.nodes(data=True)
    rightbetter = [
        data["svec"]["x"] + (data["svec"]["w"] / 2)
        for id, data in nodes
        if data["label"] in ["cat"]
    ]
    if len(rightbetter) > 0:
        return int((sum(rightbetter) / len(rightbetter)) / 2) + 1
    return 0


def plot(X, y):
    size = 8
    cmap = "rainbow"
    plt.figure(figsize=(size, size))
    plt.xticks([])
    plt.yticks([])
    plt.axis("off")
    plt.scatter(X[:, 0], X[:, 1], alpha=0.5, c=y, cmap=cmap, s=20, edgecolors="k")
    plt.show()


if __name__ == "__main__":
    graphs = []
    count = 0
    for entry in tqdm(os.scandir("data/filtered/final_data/zebra-cat-computer/8")):
        if entry.name.endswith("json"):
            with open(entry, "r") as f:
                graphs.append(json_graph.node_link_graph(json.loads(f.read())))
        count += 1
    labels = []
    for i in range(len(graphs)):
        labels.append(oracle1(graphs[i]))
    class_weight = Counter(labels)
    print(class_weight)
    X = vectorize(graphs, complexity=3)
    print(
        "Instances: %d Features: %d with an avg of %d features per instance"
        % (X.shape[0], X.shape[1], X.getnnz() / X.shape[0])
    )
    graphs, g_val = train_test_split(graphs, random_state=42)

    X, X_val, labels, y_val = train_test_split(
        X, labels, test_size=0.1, random_state=42
    )
    print(Counter(y_val))
    sm = SMOTE(random_state=42)
    X, labels = sm.fit_sample(X, labels)

    X_train, X_test, y_train, y_test = train_test_split(
        X, labels, train_size=0.25, random_state=42
    )
    print(Counter(y_train))
    print(Counter(y_test))
    clf = SGDClassifier(average=True, class_weight="balanced", shuffle=True, n_jobs=-1)
    #  clf = RandomForestClassifier(n_jobs=-1, n_estimators=100, class_weight="balanced")
    clf.fit(X_train, y=y_train)
    for i in range(len(y_val) - 1):
        if y_val[i] > 0:
            pred = clf.predict(X_val[i])
            print(g_val[i].graph["url"])
            print(f"pred: {pred}, label: {y_val[i]})")
            print()

    print(clf.score(X_test, y_test))
    print(clf.score(X_val, y_val))
    #  scores = cross_val_score(clf, X, labels, cv=10, scoring="accuracy")
    #  print(scores)
    #  print("AUC ROC: %.4f +- %.4f" % (np.mean(scores), np.std(scores)))
