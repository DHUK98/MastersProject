from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import TruncatedSVD
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.manifold import TSNE
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
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
    computers = [(id, data["label"]) for id, data in nodes if data["label"] in ["cat"]]
    objects = [(id, data["label"]) for id, data in nodes if data["label"] in ["black"]]
    for z, clab in computers:
        for o, olab in objects:
            if G.has_edge(z, o):
                return 1
    return 0


def oracle3(G):
    nodes = G.nodes(data=True)
    edges = G.edges(data=True)
    cats = [data["svec"] for id, data in nodes if data["label"] in ["cat"]]
    for c in cats:
        if "black" in c.keys():
            return 1
    return 0


def oracle4(G):
    nodes = G.nodes(data=True)
    cats = [id for id, data in nodes if data["label"] in ["cat", "zebra"]]
    count = 0
    for c in cats:
        for neighbor in G.neighbors(c):
            if G.nodes[neighbor]["label"] == "pos":
                if G.nodes[neighbor]["svec"]["x"] >= 50:
                    count += 1
                    print(G.nodes[neighbor])

    return 1 if count == len(cats) and len(cats) > 0 else 0


def oracle1(G):
    nodes = G.nodes(data=True)
    objects = [
        data["svec"]["x"]
        for id, data in nodes
        if data["label"] in ["cat", "zebra", "computer"]
    ]

    count = 0
    for o in objects:
        if o >= 50:
            count += 1
    return 1 if count == len(objects) and len(objects) > 0 else 0


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
    for entry in tqdm(
        os.scandir("data/filtered/final_data/zebra-cat-computer/1_attribs-as-nodes")
    ):
        if entry.name.endswith("json"):
            with open(entry, "r") as f:
                graphs.append(json_graph.node_link_graph(json.loads(f.read())))
        count += 1

    labels = []
    for i in range(len(graphs)):
        labels.append(oracle2(graphs[i]))
    class_weight = Counter(labels)
    print(class_weight)
    X = vectorize(graphs, complexity=3)
    print(
        "Instances: %d Features: %d with an avg of %d features per instance"
        % (X.shape[0], X.shape[1], X.getnnz() / X.shape[0])
    )
    predictor = SGDClassifier(
        average=True, class_weight="balanced", shuffle=True, n_jobs=-1
    )
    X_train, X_test, y_train, y_test = train_test_split(
        X, labels, train_size=0.1, random_state=42
    )
    predictor.fit(X_train, y_train)
    rus = RandomUnderSampler(random_state=42)
    #  X_test, y_test = rus.fit_resample(X_test, y_test)
    #  print(predictor.score(X_test, y_test))

    pred = predictor.predict(X_test)
    print(accuracy_score(y_test, pred))
    print(confusion_matrix(y_test, pred))

    #  X, labels = rus.fit_resample(X, labels)
    print(Counter(labels))
    scores = cross_val_score(predictor, X, labels, cv=10, scoring="roc_auc")
    print(scores)
    print("AUC ROC: %.4f +- %.4f" % (np.mean(scores), np.std(scores)))
