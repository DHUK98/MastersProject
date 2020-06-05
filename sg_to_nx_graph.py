import visual_genome.local as vg
import networkx as nx
from vg_data_utils import get_scene_graphs
import numpy as np
import time
from tqdm import tqdm
from eden.display import draw_graph
import ujson as json
import os
import itertools
from networkx.readwrite import json_graph


def sg_to_nx(sg):
    w = sg.image.width
    h = sg.image.height

    g = nx.DiGraph(w=w, h=h, url=sg.image.url, id=sg.image.id)
    for r in sg.relationships:
        g.add_edge(
            r.subject.id, r.object.id, label=r.predicate,
        )
    for o in sg.objects:
        attributes = {d: 1 for d in o.attributes}
        pos = {
            "x": int(o.x / w * 100),
            "y": int(o.y / h * 100),
            "w": int(o.width / w * 100),
            "h": int(o.height / h * 100),
        }
        attributes.update(pos)
        g.add_node(o.id, label=str(o), svec=attributes)
    return g


def solve_mst(nxg):
    temp = nx.Graph()
    attributes = nx.get_node_attributes(nxg, "svec")
    edges = list(itertools.permutations(nxg.nodes, 2))
    ttt = [e for e in edges if not e[0] == e[1]]
    n_edged = []
    for e in edges:
        n, nn = e
        na = attributes[n]
        nna = attributes[nn]
        dist = dist_between_points(na["x"], na["y"], nna["x"], nna["y"])
        dist = int(dist)
        n_edged.append((n, nn, {"label": "near", "weight": dist}))
    temp.add_edges_from(n_edged)
    temp = nx.minimum_spanning_tree(temp)
    for u, v, g in temp.edges(data=True):
        if nxg.has_edge(u, v):
            continue
        nxg.add_edge(u, v, label="near", weight=g["weight"])
        nxg.add_edge(v, u, label="near", weight=g["weight"])


def dist_between_points(x, y, x2, y2):
    return (((x2 - x) ** 2 + (y2 - y) ** 2)) ** 0.5


if __name__ == "__main__":
    scene_graphs = get_scene_graphs(filters=["cat", "zebra"])
    for sg in tqdm(scene_graphs):
        id = sg.image.id
        g = sg_to_nx(sg)
        solve_mst(g)

        data = json_graph.node_link_data(g)
        with open(f"data/filtered/cat-zebra/{id}.json", "w") as file:
            zebra.write(json.dumps(data))
