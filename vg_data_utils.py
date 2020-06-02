import ujson as json
import visual_genome.local as vg
import pickle
import numpy as np
from tqdm import tqdm
import os
import pprint

#  Save scene graph objects from the data file 'data/by-id/'
def save_scene_graphs_as_objs(
    start_index=1, end_index=108079, min_rels=0, split_size=0
):
    """
    Helper function to convert scene graphs from the visual genome 'data/by-id/' directory into pickle object files

   Input:
        start_index
        end_index
        min_rels
        split_size - number of scene graphs per object file
    """
    split_points = [
        min(x, end_index) for x in range(split_size, end_index + split_size, split_size)
    ]
    prev = 1
    for i in split_points:
        print(prev, i)
        temp_scene_graphs = vg.get_scene_graphs(
            start_index=prev, end_index=i, min_rels=15
        )
        print(len(temp_scene_graphs))
        fh = open("data/scene_graph_objs/" + str(i) + ".obj", "wb")
        pickle.dump(temp_scene_graphs, fh)
        temp_scene_graphs = []
        prev = i


# Check if a scene graph contains specified objects
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
    for o in sg.objects:
        for n in o.names:
            if n.lower() in objects:
                return True
    return False

def get_filtered_ids(filters):
    filters.sort()
    image_ids = vg.get_all_image_data('data/')
    images = {img.id: img for img in image_ids}
    ids = list(images.keys())
    out = []
    for id in tqdm(ids):
        data = json.load(open(f'data/by-id/{id}.json'))
        graph = vg.parse_graph_local(data,images[id])
        for o in graph.objects:
            if scene_graph_contains(graph,filters):
                out.append(int(id))
                break
    return out

def write_ids_to_file(filename, ids):
    with open(filename,'w') as out:
        for i in ids:
            out.write(i)
            out.write(' ')

def get_scene_graphs_from_ids(ids):
    image_ids = vg.get_all_image_data('data/')
    images = {img.id: img for img in image_ids}
    out = [] 
    for id in tqdm(ids):
        data = json.load(open(f'data/by-id/{id}.json'))
        graph = vg.parse_graph_local(data,images[id])
        out.append(graph)  
    return out

def load_ids_from_file(path):
    ids = []
    with open(path,'r') as file:
        data = str(file.read())
        ids = list(map(int, data.strip().split(' '))) 
    return ids


def get_scene_graphs_from_filters(filters):
    filters.sort()
    path = f'{"_".join(filters)}.txt'
    filtered_ids =[]
    if not os.path.isfile(path):
        print("Filters dont already exits. Filtering data")
        filtered_ids = get_filtered_ids(filters)  
        print(f"Writing filters to file at '{path}')")
        write_ids_to_file(path,filtered_ids)
    else:
        print("Filtered id already exist loadint from file at '{path}'")
        filtered_ids = load_ids_from_file(path) 
   
    print("Loading scene graphs from filtered ids")
    return get_scene_graphs_from_ids(filtered_ids)
        


filters = ['dog','cat','person']
print(get_scene_graphs_from_filters(filters))



