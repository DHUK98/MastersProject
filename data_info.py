import networkx as nx
from tqdm import tqdm
from networkx.readwrite import json_graph
import ujson as json
import os
import matplotlib.pyplot as plt
from eden.graph import vectorize
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE


def plot(X, y):
    size = 8
    plt.figure(figsize=(size, size))
    plt.xticks([])
    plt.yticks([])
    plt.axis("off")
    plt.scatter(X[:, 0], X[:, 1], alpha=0.5, c=y, s=20, edgecolors="k")
    plt.legend()
    plt.show()


def label(G):
    nodes = G.nodes(data=True)
    label = []
    out = 0
    zebras = [(id, data["label"]) for id, data in nodes if data["label"] in ["zebra"]]
    computer = [
        (id, data["label"]) for id, data in nodes if data["label"] in ["computer"]
    ]
    cat = [(id, data["label"]) for id, data in nodes if data["label"] in ["cat"]]
    if len(zebras) > 0:
        out += 10
        label.append("zebra")
    if len(cat) > 0:
        out += 5
        label.append("cat")
    if len(computer) > 0:
        label.append("computer")
        out += 1
    return out, " ".join(label)


if __name__ == "__main__":
    graphs = []
    labels = []
    c = []
    for entry in tqdm(os.scandir("data/filtered/final_data/zebra-cat-computer/1")):
        if entry.name.endswith("json"):
            with open(entry, "r") as f:
                graph = json_graph.node_link_graph(json.loads(f.read()))
                c, l = label(graph)
                labels.append(c)
                graphs.append(graph)

    X = vectorize(graphs, complexity=2)
    svd = TruncatedSVD(n_components=16)
    svd_results = svd.fit_transform(X)
    tsne = TSNE(n_components=2, verbose=1, perplexity=100, metric="cosine")
    tsne_results = tsne.fit_transform(svd_results)
    plot(tsne_results, labels)
    plt.show()
