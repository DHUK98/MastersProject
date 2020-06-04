import visual_genome.local as vg
import networkx as nx
from vg_data_utils import get_scene_graphs
import numpy as np
import time
from tqdm import tqdm
from eden.display import draw_graph


def sg_to_nx(sg):
    g = nx.DiGraph()
    temp_g = nx.Graph()

    w = sg.image.width
    h = sg.image.height

    for r in sg.relationships:
        g.add_edge(
            r.subject.id,
            r.object.id,
            label=r.predicate,
            weight=relative_dist_between_objects(r.subject, r.object, w, h),
        )
    for o in sg.objects:
        attributes = {d: 1 for d in o.attributes}
        g.add_node(o.id, label=str(o), svec=attributes)

        for oo in sg.objects:
            if temp_g.has_edge(o.id, oo.id) or temp_g.has_edge(oo.id, o.id):
                continue
            temp_g.add_edge(
                o.id, oo.id, weight=relative_dist_between_objects(o, oo, w, h)
            )

    t = list(nx.minimum_spanning_edges(temp_g, data=True))
    for u, v, d in t:
        if not (u, v) in g.edges():
            g.add_edge(u, v, label="near", weight=d["weight"])

    return g


def relative_dist_between_objects(d, o, w, h):
    x = d.x + d.width / 2
    y = d.y + d.height / 2
    x2 = o.x + o.width / 2
    y2 = o.y + o.height / 2
    x /= w
    x2 /= w
    y /= h
    y2 /= h
    return (x2 - x) ** 2 + (y2 - y) ** 2


if __name__ == "__main__":
    scene_graphs = get_scene_graphs(filters=["cat", "dog", "person"])

    start = time.time()
    nxg = sg_to_nx(scene_graphs[0])
    end = time.time()
    print(end - start)
    draw_graph(
        nxg,
        secondary_vertex_label="svec",
        size=15,
        vertex_size=1500,
        font_size=14,
        vertex_border=True,
        size_x_to_y_ratio=3,
    )
    print()
    print(scene_graphs[0].image)
    print()
    print(nxg.nodes(data=True))
    print()
    print(nxg.edges(data=True))
