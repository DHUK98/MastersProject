from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
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
    zebras = [(id, data["label"]) for id, data in nodes if data["label"] in ["zebra"]]
    objects = [
        (id, data["label"])
        for id, data in nodes
        if data["label"] in ["tree", "grass", "water"]
    ]
    for z, clab in zebras:
        for o, olab in objects:
            if G.has_edge(z, o):
                return 1
    return 0


def oracle1(G):
    nodes = G.nodes(data=True)
    rightbetter = [
        data["svec"]["x"] + (data["svec"]["w"] / 2)
        for id, data in nodes
        if data["label"] in ["cat"]
    ]
    if len(rightbetter) > 0:
        return int(max(rightbetter) / 50) + 1
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
    for entry in tqdm(os.scandir("data/filtered/cat-zebra")):
        if entry.name.endswith("json"):
            with open(entry, "r") as f:
                graphs.append(json_graph.node_link_graph(json.loads(f.read())))
        count += 1
    labels = []
    for i in range(len(graphs)):
        labels.append(oracle2(graphs[i]))
    class_weight = Counter(labels)
    print(class_weight)
    X = vectorize(graphs, complexity=2)
    print(
        "Instances: %d Features: %d with an avg of %d features per instance"
        % (X.shape[0], X.shape[1], X.getnnz() / X.shape[0])
    )

    K = metrics.pairwise.pairwise_kernels(X, metric="linear")
    print(K[1])

    #  X_train, X_test, y_train, y_test = train_test_split(
    #  X, labels, train_size=0.25, random_state=42
    #  )
    #  sm = SMOTE(random_state=42)
    #  X_train, y_train = sm.fit_sample(X_train, y_train)
    #  X_test, y_test = sm.fit_sample(X_test, y_test)

    #  clf = RandomForestClassifier(n_jobs=-1, n_estimators=1000)
    #  clf = SGDClassifier(average=True, shuffle=True, n_jobs=-1)
    #  clf.fit(X_train, y_train)
    #  print(y_test[235])
    #  print(clf.predict(X_test[235]))
    #  print(clf.score(X_test, y_test))
