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


def plot_graph(G):
    label = nx.get_node_attributes(G, "label")
    svec = nx.get_node_attributes(G, "svec")
    e_label = nx.get_edge_attributes(G, "label")
    e_weights = nx.get_edge_attributes(G, "weight")

    pos = {n: [svec[n]["x"], 100 - svec[n]["y"]] for n in G.nodes}

    f = urllib.request.urlopen(G.graph["url"])
    a = plt.imread(f, 0)
    plt.imshow(a, extent=[-20, 100, 0, 120])

    nodes = nx.draw_networkx_nodes(G, pos, node_size=50, node_color="blue",)
    edges = nx.draw_networkx_edges(
        G, pos, node_size=15, arrowstyle="->", arrowsize=10, edge_color="blue", width=1,
    )
    edge_labels = nx.draw_networkx_edge_labels(
        G, pos, edge_labels=e_label, bbox=dict(alpha=0), font_size=8, rotate=False
    )
    node_labels = nx.draw_networkx_labels(G, pos, labels=label,)
    plt.title(f"image id: {G.graph['id']}")
    plt.show()


def plot(X):
    size = 8
    cmap = "rainbow"
    plt.figure(figsize=(size, size))
    plt.xticks([])
    plt.yticks([])
    plt.scatter(X[:, 0], X[:, 1], alpha=0.2, cmap=cmap, s=20, edgecolors="k")
    #  for i in range(X.shape[0]):
    #  plt.annotate(
    #  str(i), (X[i, 0], X[i, 1]), xytext=(-3, 8), textcoords="offset points"
    #  )
    plt.show()


if __name__ == "__main__":
    graphs = []
    count = 0
    for entry in tqdm(os.scandir("data/filtered/cat-zebra")):
        if entry.name.endswith("json"):
            graphs.append(json_graph.node_link_graph(json.loads(open(entry).read())))
        count += 1
        #  if count > 1000:
        #  break
    print("vectorize")
    X = vectorize(graphs, complexity=2, nbits=16, discrete=False)
    print("TruncatedSVD")
    Xd = TruncatedSVD(n_components=16).fit_transform(X)
    print("TSNE")
    X_embedded = TSNE(n_components=2).fit_transform(Xd)

    print("plot")
    plot(X_embedded)

