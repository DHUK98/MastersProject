import visual_genome.local as vg
import networkx as nx
from vg_data_utils import get_scene_graphs
import numpy as np
import time
from tqdm import tqdm
import ujson as json
import os
import itertools
from networkx.readwrite import json_graph
from render_graph import render_graph


def sg_to_nx(sg, distance=100, weighted=True, mst=False, near=0):
    w = sg.image.width
    h = sg.image.height
    g = nx.DiGraph(w=w, h=h, url=sg.image.url, id=sg.image.id)
    for r in sg.relationships:
        if weighted:
            sx = int(r.subject.x / w * distance)
            sy = int(r.subject.y / h * distance)
            ox = int(r.object.x / w * distance)
            oy = int(r.object.y / h * distance)
            dist = int(dist_between_points(sx, sy, ox, oy))
            g.add_edge(
                r.subject.id, r.object.id, label=r.predicate.lower(), weight=dist
            )
        else:
            g.add_edge(r.subject.id, r.object.id, label=r.predicate.lower())

    for o in sg.objects:
        attributes = {d.lower(): 1 for d in o.attributes}
        pos = {
            "x": int(o.x / w * distance),
            "y": int(o.y / h * distance),
            "w": int(o.width / w * distance),
            "h": int(o.height / h * distance),
        }
        attributes.update(pos)
        g.add_node(o.id, label=str(o).lower(), svec=attributes)

    if mst:
        solve_mst(g, weighted=weighted)

    if near > 0:
        add_edge_between_all(g, thresh=near, weighted=weighted)
    return g


def add_edge_between_all(nxg, thresh=1, weighted=True, label="near"):
    temp = nx.Graph()
    w = nxg.graph["w"]
    h = nxg.graph["h"]

    attributes = nx.get_node_attributes(nxg, "svec")
    edges = list(itertools.permutations(nxg.nodes, 2))
    ttt = [e for e in edges if not e[0] == e[1]]
    n_edged = []
    for e in edges:
        n, nn = e
        na = attributes[n]
        nna = attributes[nn]

        sx = na["x"]
        sy = na["y"]
        ox = nna["x"]
        oy = nna["y"]
        dist = int(dist_between_points(sx, sy, ox, oy))
        if dist <= thresh:
            if weighted:
                n_edged.append((n, nn, {"label": label, "weight": dist}))
            else:
                n_edged.append((n, nn, {"label": label}))
    temp.add_edges_from(n_edged)
    for u, v, g in temp.edges(data=True):
        if nxg.has_edge(u, v):
            continue
        if weighted:
            nxg.add_edge(u, v, label=label, weight=g["weight"])
            nxg.add_edge(v, u, label=label, weight=g["weight"])
        else:
            nxg.add_edge(u, v, label=label)
            nxg.add_edge(v, u, label=label)


def solve_mst(nxg, weighted=True, label="near"):
    temp = nx.Graph()
    w = nxg.graph["w"]
    h = nxg.graph["h"]

    attributes = nx.get_node_attributes(nxg, "svec")
    edges = list(itertools.permutations(nxg.nodes, 2))
    ttt = [e for e in edges if not e[0] == e[1]]
    n_edged = []
    for e in edges:
        n, nn = e
        na = attributes[n]
        nna = attributes[nn]
        sx = na["x"]
        sy = na["y"]
        ox = nna["x"]
        oy = nna["y"]
        dist = int(dist_between_points(sx, sy, ox, oy))
        n_edged.append((n, nn, {"label": label, "weight": dist}))
    temp.add_edges_from(n_edged)
    temp = nx.minimum_spanning_tree(temp)
    for u, v, g in temp.edges(data=True):
        if nxg.has_edge(u, v):
            continue
        if weighted:
            nxg.add_edge(u, v, label=g["label"], weight=g["weight"])
            nxg.add_edge(v, u, label=g["label"], weight=g["weight"])
        else:
            nxg.add_edge(u, v, label=g["label"])
            nxg.add_edge(v, u, label=g["label"])


def dist_between_points(x, y, x2, y2):
    return (((x2 - x) ** 2 + (y2 - y) ** 2)) ** 0.5


if __name__ == "__main__":
    scene_graphs = get_scene_graphs(filters=["zebra", "cat", "computer"])
    print(len(scene_graphs))

    directory = "data/filtered/final_data/zebra-cat-computer/1"
    if not os.path.exists(directory):
        os.makedirs(directory)
    for sg in tqdm(scene_graphs):
        id = sg.image.id
        g = sg_to_nx(sg, mst=True, near=3, weighted=True, distance=10)
        print(nx.info(g))
        render_graph(g,axis=10)
        break
        #  data = json_graph.node_link_data(g)
        #  with open(f"{directory}/{id}.json", "w") as file:
        #  file.write(json.dumps(data))
