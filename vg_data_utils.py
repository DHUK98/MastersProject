import ujson as json
import visual_genome.local as vg
import pickle
import numpy as np
from tqdm import tqdm
import os
import pprint


def scene_graph_contains(sg, objects):
    """ 
    Check if a scene graph contains any objects from a specified list

    Input: 
        sg - the scene graph to check
        filters - list of names of objects
    
    Output:
        True - if the scene graph does contain any of the specified objects
        False - otherwise
    """
    for object in sg.objects:
        for name in object.names:
            if name.lower() in objects:
                return True
    return False


def get_filtered_image_ids(images, filters):
    filters.sort()
    ids = list(images.keys())
    out = []
    for id in tqdm(ids):
        data = json.load(open(f"data/by-id/{id}.json"))
        graph = vg.parse_graph_local(data, images[id])
        for o in graph.objects:
            if scene_graph_contains(graph, filters):
                out.append(str(id))
                break
    return out


def get_scene_graphs_from_image_ids(images, ids):
    out = []
    for id in tqdm(ids):
        id = int(id)
        data = json.load(open(f"data/by-id/{id}.json"))
        graph = vg.parse_graph_local(data, images[id])
        out.append(graph)
    return out


def write_image_ids_to_file(path, ids):
    with open(path, "w") as out:
        for i in ids:
            out.write(i)
            out.write(" ")


def load_image_ids_from_file(path):
    ids = []
    with open(path, "r") as file:
        data = str(file.read())
        ids = list(map(int, data.strip().split(" ")))
    return ids


def get_scene_graphs(filters=[], data_dir="data/"):
    """
    Load Visual Genome scene graphs with filters applied.
    Creates a file containing the id's of scene graph within
    the filtered subset to allow for faster loading when the
    same subset needs to be loaded at anther time.

    Input: 
        - filters:  List of stings of objects to filter scene
                    graphs for
        - data_dir: path to visual genome data directory
    """
    image_ids = vg.get_all_image_data(data_dir)
    images = {img.id: img for img in image_ids}
    filters.sort()
    path = f'{data_dir}/filtered/{"_".join(filters)}.txt'
    ids = []
    if not len(filters) == 0:
        if not os.path.isfile(path):
            print("Filters dont already exits. Filtering data")
            ids = get_filtered_image_ids(images, filters)
            print(f"Writing filters to file at '{path}')")
            write_image_ids_to_file(path, ids)
        else:
            print(f"Filtered id already exist loadint from file at '{path}'")
            ids = load_image_ids_from_file(path)
    else:
        ids = list(images.keys())
    print("Loading scene graphs from filtered ids")
    return get_scene_graphs_from_image_ids(images, ids)


if __name__ == "__main__":
    filters = ["dog", "cat", "person", "chicken"]
    print(len(get_scene_graphs(filters=filters)))
