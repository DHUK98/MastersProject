from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import balanced_accuracy_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import TruncatedSVD
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.manifold import TSNE
from sklearn.utils import shuffle
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

def oracle_1(G):
    nodes = G.nodes(data=True)
    cat = [id for id, data in nodes if data["label"] in ["cat"]]
    return 1 if len(cat) > 0 else 0


def oracle_2_atribs_as_nodes(G):
    nodes = G.nodes(data=True)
    edges = G.edges(data=True)
    computers = [(id, data["label"]) for id, data in nodes if data["label"] in ["cat"]]
    objects = [(id, data["label"]) for id, data in nodes if data["label"] in ["black"]]
    for z, clab in computers:
        for o, olab in objects:
            if G.has_edge(z, o):
                return 1
    return 0


def oracle_2(G):
    nodes = G.nodes(data=True)
    edges = G.edges(data=True)
    cats = [data["svec"] for id, data in nodes if data["label"] in ["cat"]]
    for c in cats:
        if "black" in c.keys():
            return 1
    return 0


def oracle_3(G):
    nodes = G.nodes(data=True)
    objects = [
        data["svec"]["x"] for id, data in nodes if data["label"] in ["cat", "zebra"]
    ]
    for o in objects:
        if o >= 50:
            return 1
    return 0


def oracle_3_pos_as_nodes(G):
    nodes = G.nodes(data=True)
    cats = [id for id, data in nodes if data["label"] in ["cat", "zebra"]]
    for c in cats:
        for neighbor in G.neighbors(c):
            if G.nodes[neighbor]["label"] == "pos":
                if G.nodes[neighbor]["svec"]["x"] >= 50:
                    return 1
    return 0


def oracle_4(G):
    nodes = G.nodes(data=True)
    cats = [id for id, data in nodes if data["label"] in ["cat"]]
    if len(cats) > 4:
        return 1
    return 0


def accuracy_of_representation_with_oracle(data_file, oracle):
    graphs = []
    for entry in os.scandir(f"data/filtered/final_data/zebra-cat-computer/{data_file}"):
        if entry.name.endswith("json"):
            with open(entry, "r") as f:
                graphs.append(json_graph.node_link_graph(json.loads(f.read())))

    labels = []
    for i in range(len(graphs)):
        labels.append(oracle(graphs[i]))

    X = vectorize(graphs, complexity=3)

    predictor = SGDClassifier(
        average=True, class_weight="balanced", shuffle=True, n_jobs=-1
    )
    X_train, X_test, y_train, y_test = train_test_split(
        X, labels, train_size=0.1, random_state=42
    )
    predictor.fit(X_train, y_train)

    pred = predictor.predict(X_test)
    print(balanced_accuracy_score(y_test, pred))
    print(confusion_matrix(y_test, pred))

    X, labels = shuffle(X, labels)

    scores = cross_val_score(predictor, X, labels, cv=10, scoring="roc_auc")

    print("AUC ROC: %.4f +- %.4f" % (np.mean(scores), np.std(scores)))
    print()


if __name__ == "__main__":
    accuracy_of_representation_with_oracle(
        "2_attribs-as-nodes", oracle_2_atribs_as_nodes
    )
