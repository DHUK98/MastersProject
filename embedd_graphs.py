import os
from eden.graph import vectorize
import networkx as nx
from networkx.readwrite import json_graph
import ujson as json
from tqdm import tqdm
import matplotlib.pyplot as plt
import urllib

if __name__ == "__main__":
    graphs = []
    for entry in tqdm(os.scandir("data/filtered/cat-zebra")):
        if entry.name.endswith("json"):
            graphs.append(json_graph.node_link_graph(json.loads(open(entry).read())))
        break
    G = graphs[0]
    label = nx.get_node_attributes(G, "label")
    svec = nx.get_node_attributes(G, "svec")
    e_label = nx.get_edge_attributes(G, "label")
    e_weights = nx.get_edge_attributes(G, "weight")

    pos = {n: [svec[n]["x"], svec[n]["y"]] for n in G.nodes}

    f = urllib.request.urlopen(G.graph["url"])
    a = plt.imread(f, 0)
    plt.imshow(a, interpolation="nearest", aspect="auto", extent=[0, 100, 0, 100])

    nodes = nx.draw_networkx_nodes(G, pos, node_size=50, node_color="blue",)
    edges = nx.draw_networkx_edges(
        G, pos, node_size=15, arrowstyle="->", arrowsize=10, edge_color="blue", width=1,
    )
    edge_labels = nx.draw_networkx_edge_labels(
        G, pos, edge_labels=e_label, bbox=dict(alpha=0), font_size=8, rotate=False
    )
    node_labels = nx.draw_networkx_labels(G, pos, labels=label,)
    plt.axis([0, 100, 0, 100])
    plt.title(f"image id: {G.graph['id']}")
    plt.tight_layout()
    plt.show()

