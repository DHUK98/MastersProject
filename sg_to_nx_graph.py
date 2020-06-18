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
        add_edges_between_close_objects(g, thresh=near, weighted=weighted)
    return g


def solve_mst(nxg, weighted=True, label="near"):
    temp = nx.Graph()
    w = nxg.graph["w"]
    h = nxg.graph["h"]

    attribs = nx.get_node_attributes(nxg, "svec")
    edges = list(itertools.combinations(nxg.nodes, 2))
    for u, v in edges:
        dist = int(
            dist_between_points(
                attribs[u]["x"], attribs[u]["y"], attribs[v]["x"], attribs[v]["y"]
            )
        )
        temp.add_edge(u, v, label=label, weight=dist)
    temp = nx.minimum_spanning_tree(temp)

    for u, v, g in temp.edges(data=True):
        if not nxg.has_edge(u, v):
            if weighted:
                nxg.add_edge(u, v, label=g["label"], weight=g["weight"])
            else:
                nxg.add_edge(u, v, label=g["label"])
        if not nxg.has_edge(v, u):
            if weighted:
                nxg.add_edge(v, u, label=g["label"], weight=g["weight"])
            else:
                nxg.add_edge(v, u, label=g["label"])


def add_edges_between_close_objects(nxg, thresh=1, weighted=True, label="near"):
    w = nxg.graph["w"]
    h = nxg.graph["h"]

    attribs = nx.get_node_attributes(nxg, "svec")
    edges = list(itertools.combinations(nxg.nodes, 2))
    for u, v in edges:
        dist = dist_between_points(
            attribs[u]["x"], attribs[u]["y"], attribs[v]["x"], attribs[v]["y"]
        )
        if dist <= thresh:
            if nxg.has_edge(u, v) or nxg.has_edge(v, u):
                continue
            if weighted:
                nxg.add_edge(u, v, label=label, weight=int(dist))
                nxg.add_edge(v, u, label=label, weight=int(dist))
            else:
                nxg.add_edge(u, v, label=label)
                nxg.add_edge(v, u, label=label)


def dist_between_points(x, y, x2, y2):
    return (((x2 - x) ** 2 + (y2 - y) ** 2)) ** 0.5


if __name__ == "__main__":
    scene_graphs = get_scene_graphs(filters=["zebra", "cat", "computer"])
    print(len(scene_graphs))

    directory = "data/filtered/final_data/zebra-cat-computer/8"
    if not os.path.exists(directory):
        os.makedirs(directory)

    for sg in tqdm(scene_graphs):
        mul = 0.1
        distance = 100 * mul
        near = 25 * mul
        weighted = False

        g = sg_to_nx(sg, mst=True, near=near, weighted=weighted, distance=distance)

        id = sg.image.id
        data = json_graph.node_link_data(g)
        with open(f"{directory}/{id}.json", "w") as file:
            file.write(json.dumps(data))
