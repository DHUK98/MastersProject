import ujson as json
import visual_genome.local as vg
import pickle
import numpy as np
from tqdm import tqdm
import os

#  Save scene graph objects from the data file 'data/by-id/'
def save_scene_graphs_as_objs(start_index=1, end_index=108079,min_rels=0,split_size=0):
    """
    Helper function to convert scene graphs from the visual genome 'data/by-id/' directory into pickle object files

    Input:
        start_index
        end_index
        min_rels
        split_size - number of scene graphs per object file
    """
    split_points = [min(x,end_index) for x in range(split_size,end_index + split_size,split_size)]
    prev = 1
    for i in split_points:
        print(prev,i)
        temp_scene_graphs = vg.get_scene_graphs(start_index=prev,end_index=i,min_rels=15)
        print(len(temp_scene_graphs))
        fh = open('data/scene_graph_objs/'+str(i)+'.obj','wb')
        pickle.dump(temp_scene_graphs,fh)
        temp_scene_graphs = [] 
        prev = i

# Check if a scene graph contains specified objects
def scene_graph_contains(sg,objects):
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
            if n in objects:
                return True
    return False

def filter_scene_graphs(path,filters):
    """ 
    Filter scene graphs based on list of object names  
    
    Input: 
        path - directory storing object files of lists of scene graphs
        filters - list of names of objects

    Output:
        filtered_sgs - filtered list of scene graphs 
    """
    filtered_sgs = []
    for fn in tqdm(os.listdir(path)):
        with open(os.path.join(path,fn),'rb') as f:
            sgs = pickle.load(f)
            for g in sgs:
                if scene_graph_contains(g,filters):
                    filtered_sgs.append(g)
    return filtered_sgs




