import os
from eden.graph import vectorize
import networkx as nx
from networkx.readwrite import json_graph
import ujson as json
from tqdm import tqdm
import matplotlib.pyplot as plt
import urllib
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE
from sklearn import metrics
from oracle import oracle1


def plot(X, y):
    size = 8
    cmap = "rainbow"
    plt.figure(figsize=(size, size))
    plt.xticks([])
    plt.yticks([])
    plt.axis("off")
    plt.scatter(X[:, 0], X[:, 1], alpha=0.4, c=y, cmap=cmap, s=25, edgecolors="k")
    plt.show()


if __name__ == "__main__":
    graphs = []
    count = 0
    for entry in tqdm(os.scandir("data/filtered/final_data/zebra-cat-computer/1/")):
        if entry.name.endswith("json"):
            graphs.append(json_graph.node_link_graph(json.loads(open(entry).read())))
    y = []
    for g in graphs:
        y.append(oracle1(g))

    print("vectorize")
    X = vectorize(graphs, complexity=2, nbits=16)

    print("TruncatedSVD")
    Xd = TruncatedSVD(n_components=50).fit_transform(X)
    print("TSNE")
    X_embedded = TSNE(n_components=2).fit_transform(X)

    plot(X_embedded, y)

