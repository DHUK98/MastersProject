import networkx as nx
import ujson as json
import numpy as np
from tqdm import tqdm
from networkx.readwrite import json_graph
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from eden.graph import vectorize
from sklearn.decomposition import TruncatedSVD
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import cross_val_score
import os
from collections import Counter
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt


def oracle(G):
    nodes = G.nodes(data=True)
    rightbetter = [data["svec"]["x"] for id, data in nodes if data["label"] in ["cat"]]
    if len(rightbetter) > 0:
        return int(max(rightbetter) / 20) + 1
    #  return 1 if 75 > max(rightbetter) > 25 else 0
    #  right = [
    #  (id, data)
    #  for id, data in nodes
    #  if data["label"] in ["zebra"] and data["svec"]["x"] >= 50
    #  #  and data["svec"]["w"] * data["svec"]["h"] > 2500
    #  ]
    #  left = [
    #  (id, data)
    #  for id, data in nodes
    #  if data["label"] in ["cat"] and data["svec"]["x"] + data["svec"]["w"] < 70
    #  #  and data["svec"]["w"] * data["svec"]["h"] > 4000
    #  ]
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
    for entry in tqdm(os.scandir("data/filtered/cat_z_new")):
        if entry.name.endswith("json"):
            with open(entry, "r") as f:
                graphs.append(json_graph.node_link_graph(json.loads(f.read())))
        count += 1
    labels = []
    for i in range(len(graphs)):
        labels.append(oracle(graphs[i]))
    class_weight = Counter(labels)
    print(class_weight)
    X = vectorize(graphs, complexity=2)
    print(
        "Instances: %d Features: %d with an avg of %d features per instance"
        % (X.shape[0], X.shape[1], X.getnnz() / X.shape[0])
    )
    svd = TruncatedSVD(n_components=16)

    svd_results = svd.fit_transform(X)
    tsne = TSNE(n_components=2, verbose=1)
    tsne_results = tsne.fit_transform(svd_results)
    print(tsne_results)
    #  plt.scatter([i[0] for i in tsne_results], [i[1] for i in tsne_results])
    plot(tsne_results, labels)
    plt.show()

    #  print("vectorized, training random forest")
    #  X_train, X_test, y_train, y_test = train_test_split(
    #  X, labels, train_size=0.7, random_state=42
    #  )
    #  print((X_train).shape[0])
    #  print((X_test).shape[0])
    #  #  clf = RandomForestClassifier(n_jobs=-1, n_estimators=1000)
    #  clf = SGDClassifier(average=True, shuffle=True, n_jobs=-1)
#
#  clf.fit(X_train, y_train)
#  #  print("trained")
#  print(y_test[235])
#  print(clf.predict(X_test[235]))
#  print(clf.score(X_test, y_test))
