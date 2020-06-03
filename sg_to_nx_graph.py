import visual_genome.local as vg
import networkx as nx
from vg_data_utils import get_scene_graphs
import numpy as np
import itertools
import time


def sg_to_nx(sg):
    g = nx.DiGraph()
    temp_g = nx.Graph()

    for r in sg.relationships:
        g.add_edge(
            r.subject.id,
            r.object.id,
            label=r.predicate,
            weight=dist_between_objects(r.subject, r.object),
        )

    for o in sg.objects:
        attributes = {d: 1 for d in o.attributes}
        g.add_node(o.id, label=str(o), svec=attributes)

        for oo in sg.objects:
            if temp_g.has_edge(o.id, oo.id) or temp_g.has_edge(oo.id, o.id):
                temp_g.add_edge(r.subject.id, r.object.id, weight=-1)
                continue
            temp_g.add_edge(o.id, oo.id, weight=dist_between_objects(o, oo))

    t = list(nx.minimum_spanning_edges(temp_g, data=False))
    for u, v in t:
        if not (u, v) in g.edges():
            g.add_edge(u, v)

    return g


def dist_between_objects(d, o):
    x = d.x + d.width / 2
    y = d.y + d.height / 2
    x2 = o.x + o.width / 2
    y2 = o.y + o.height / 2
    return np.sqrt((x2 - x) ** 2 + (y2 - y) ** 2)


if __name__ == "__main__":
    scene_graphs = get_scene_graphs(filters=["cat", "dog", "person"])

    sg = scene_graphs[0]
    start = time.time()
    nxg = sg_to_nx(sg)
    end = time.time()
    print(end - start)
    print()
    print(nxg.nodes(data=True))
    print()
    print(nxg.edges(data=True))
