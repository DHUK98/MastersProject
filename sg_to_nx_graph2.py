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
import uuid


def sg_to_nx(sg, distance=100, weighted=True, mst=False, near=0):
    """
    Takes a Visual Genome scene graph and converts it to a netowrkx
    graph.

    Input:
        sg - scene graph to be converted

    Output
    """
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
        pos = {
            "x": int(o.x / w * distance),
            "y": int(o.y / h * distance),
            "w": int(o.width / w * distance),
            "h": int(o.height / h * distance),
        }
        g.add_node(o.id, label=str(o).lower(), svec=pos)

    if mst:
        solve_mst(g, weighted=weighted)

    if near > 0:
        add_edges_between_close_objects(g, thresh=near, weighted=weighted)

    # Add attribute nodes
    for o in sg.objects:
        attributes = [d.lower() for d in o.attributes]
        pos = {
            "x": int(o.x / w * distance),
            "y": int(o.y / h * distance),
            "w": int(o.width / w * distance),
            "h": int(o.height / h * distance),
        }
        for a in attributes:
            a_id = uuid.uuid1().int >> 64
            g.add_node(a_id, label=a, svec=pos)
            g.add_edge(o.id, a_id, label="is")

    return g


def solve_mst(nxg, weighted=True, label="near"):
    """
    Solve minium spanning tree for networkx graph based open
    distance between nodes

    Input:
        nxg - networkx graph to add mst too
        weighted - whether the graph edges will have weights included
        label - the label to add to the new edges created
    """
    temp = nx.Graph()
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


def add_edges_between_close_objects(nxg, thresh, weighted=True, label="near"):
    """
    Add edges between objects within a cetain threshold

    Input:
        nxg - networkx graph to add edges to
        thresh - maximum distance between nodes for edge addition
        weighted - whether the edges will be weighted with their distance
        label - label for newly created edges
    """
    # get the node attributes that contain x,y,w,h
    attribs = nx.get_node_attributes(nxg, "svec")

    # iterate throught all possible edges
    edges = list(itertools.combinations(nxg.nodes, 2))
    for u, v in edges:
        # calculate distance between objects
        dist = dist_between_points(
            attribs[u]["x"], attribs[u]["y"], attribs[v]["x"], attribs[v]["y"]
        )

        # Add edge if the distance is less than the threshold
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

    directory = "data/filtered/final_data/zebra-cat-computer/1_attribs-pos-as-nodes"
    if not os.path.exists(directory):
        os.makedirs(directory)

    for sg in tqdm(scene_graphs):
        mul = 0.1
        distance = 100 * mul
        near = 0 * mul
        weighted = False

        g = sg_to_nx(sg, mst=True, near=near, weighted=weighted, distance=distance)

        id = sg.image.id
        data = json_graph.node_link_data(g)
        with open(f"{directory}/{id}.json", "w") as file:
            file.write(json.dumps(data))
