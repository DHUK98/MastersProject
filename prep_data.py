import ujson as json
import visual_genome.local as vg
import pickle
import numpy as np
from tqdm import tqdm
import os

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
    return pickle.load(fh)

def gen_split_points(start_index, end_index, split_size):
    tests = [min(x,end_index) for x in range(split_size,end_index + split_size,split_size)]
    return tests

def scene_graph_contains(sg,filters):
    for o in sg.objects:
        for n in o.names:
            if n in filters:
                return True
    return False

def filter_scene_graphs(path,filters):
    filtered_sgs = []
    for fn in tqdm(os.listdir(path)):
        with open(os.path.join(path,fn),'rb') as f:
            sgs = pickle.load(f)
            for g in sgs:
                if scene_graph_contains(g,filters):
                    filtered_sgs.append(g)
    return filtered_sgs


#  filtered_sgs = filter_scene_graphs('data/scene_graph_objs',['chicken'])
#  pickle.dump(filtered_sgs,open('data/filtered_sgs.obj','wb'))

filtered_sgs = pickle.load(open('data/filtered_sgs.obj','rb'))
print(len(filtered_sgs))

print(filtered_sgs[15].objects)
print(filtered_sgs[15].image)


