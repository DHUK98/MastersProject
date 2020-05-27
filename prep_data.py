import ujson as json
import visual_genome.local as vg
import pickle
import numpy as np
from tqdm import tqdm


# Turn sigle 'scene_graphs.json' into seperate files per image
def gen_files_by_id():
    vg.save_scene_graphs_by_id()

#  Function to save scene graph objects from the data file 'data/by-id/'
def save_scene_graphs_as_objs(start_index=1, end_index=108077,min_rels=0,split_size=0):
    split_points = gen_split_points(start_index,end_index,split_size)
    prev = 1
    for i in split_points:
        print(prev,i)
        temp_scene_graphs = vg.get_scene_graphs(start_index=prev,end_index=i,min_rels=15)
        print(len(temp_scene_graphs))
        fh = open('data/scene_graph_objs/'+str(i)+'.obj','wb')
        pickle.dump(temp_scene_graphs,fh)
        temp_scene_graphs = [] 
        prev = i


def load_scene_graphs_from_obj(path):
    fh = open(path,'rb')
    temp = pickle.load(fh)
    return temp

def gen_split_points(start_index, end_index, split_size):
    tests = [min(x,end_index) for x in range(split_size,end_index + split_size,split_size)]
    return tests

#  save_scene_graphs_as_objs(split_size=5000)

test = load_scene_graphs_from_obj('data/scene_graph_objs/15000.obj')
t =  test[0]
print(t)

jsontest = json.dumps(test)
print(jsontest)
