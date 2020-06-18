from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
from tqdm import tqdm
import ujson as json
import urllib.request
import os


def render_graph(G, with_image=True, object_positions=True, axis=100, grid=True):
    nodes = G.nodes(data=True)
    edges = G.edges(data=True)
    nodes_labels = nx.get_node_attributes(G, "label")
    edge_labels = nx.get_edge_attributes(G, "label")
    w = nx.get_edge_attributes(G, "weight")

    near_edges = [(u, v, d) for u, v, d in edges if d["label"] == "near"]
    for u, v, _ in near_edges:
        del edge_labels[(u, v)]
    print(G.graph["url"])
    if not object_positions:
        pos = nx.spring_layout(G)
    else:
        svec = nx.get_node_attributes(G, "svec")
        posisitions = [(t["x"], axis - t["y"]) for t in svec.values()]
        pos = dict(zip(svec.keys(), posisitions))
    if with_image:
        f = urllib.request.urlopen(G.graph["url"])
        a = plt.imread(f, 0)
        plt.imshow(a, extent=[0, axis, 0, axis])

    node_size = 200
    nx.draw_networkx_nodes(G, pos, node_color="r", node_size=node_size, alpha=0.8)
    nx.draw_networkx_labels(G, pos, nodes_labels, font_size=12)
    nx.draw_networkx_edges(
        G, pos, edgelist=edge_labels, width=1.0, alpha=1, node_size=node_size
    )
    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=near_edges,
        width=1,
        alpha=0.3,
        edge_color="r",
        node_size=node_size,
    )
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.xlim(0 - axis * 0.1, axis * 1.1)
    plt.ylim(0 - axis * 0.1, axis * 1.1)
    plt.xticks(np.arange(0 - axis * 0.1, axis * 1.1, step=1))
    plt.yticks(np.arange(0 - axis * 0.1, axis * 1.1, step=1))
    if grid:
        plt.grid()
    plt.show()


if __name__ == "__main__":
    for entry in tqdm(os.scandir("data/filtered/final_data/zebra-cat-computer/1")):
        if entry.name.endswith("json"):
            with open(entry, "r") as f:
                graph = json_graph.node_link_graph(json.loads(f.read()))
                render_graph(graph)
                break
