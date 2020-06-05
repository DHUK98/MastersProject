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

    g = nx.DiGraph(w=w, h=h)
    for r in sg.relationships:
        g.add_edge(
            r.subject.id,
            r.object.id,
            label=r.predicate,
            #  weight=relative_dist_between_objects(r.subject, r.object, w, h),
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
    print(len(edges))

    ttt = [e for e in edges if not e[0] == e[1]]
    print(len(ttt))
    n_edged = []
    for e in edges:
        n, nn = e
        na = attributes[n]
        nna = attributes[nn]
        dist = relative_dist_between_points(
            na["x"], na["y"], nna["x"], nna["y"], nxg.graph["w"], nxg.graph["h"]
        )
        dist = int(dist)
        n_edged.append((n, nn, {"label": "near", "weight": dist}))
    temp.add_edges_from(n_edged)
    temp = nx.minimum_spanning_tree(temp)
    for u, v, g in temp.edges(data=True):
        if nxg.has_edge(u, v):
            continue
        nxg.add_edge(u, v, label="near", weight=g["weight"])
        nxg.add_edge(v, u, label="near", weight=g["weight"])


def relative_dist_between_points(x, y, x2, y2, w, h):
    return (((x2 - x) ** 2 + (y2 - y) ** 2)) ** 0.5


from networkx.drawing.nx_pydot import write_dot

if __name__ == "__main__":
    scene_graphs = get_scene_graphs(filters=["zebra"])
    #  scene_graphs = get_scene_graphs()
    graphs = []
    for sg in tqdm(scene_graphs):
        id = sg.image.id
        g = sg_to_nx(sg)
        solve_mst(g)
        graphs.append(g)
        print(g.edges(data=True))
        print()
        data = json_graph.node_link_data(g)
        #  print(data)
        with open(f"data/filtered/zebra/{id}.json", "w") as file:
            file.write(json.dumps(data))
    G = graphs[1]

    draw_graph(
        G,
        secondary_vertex_label="svec",
        secondary_edge_label="weight",
        size=15,
        vertex_size=500,
        font_size=14,
        vertex_border=True,
        size_x_to_y_ratio=3,
    )
    #  sgs = {}
#
#  print(scene_graphs[0].image)
#  for entry in os.scandir("data/filtered/zebra"):
#  if entry.path.endswith("gefx"):
#  with open(entry) as file:
#  sg = nx.read_gexf(entry.path, node_type=int)
#  sgs[entry.name.split(".")[0]] = sg

#  print(solve_mst(sgs["134"]).edges(data=True))

#  draw_graph(
#  sgs[0],
#  size=15,
#  vertex_size=1500,
#  font_size=14,
#  vertex_border=True,
#  size_x_to_y_ratio=3,
#  )
#  nx.write_multiline_adjlist(g, "test")
#  test = nx.read_multiline_adjlist("test", nodetype=int, create_using=nx.DiGraph)
#  print(list(nx.generate_multiline_adjlist(test)))
