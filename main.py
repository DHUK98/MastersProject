import visual_genome.local as vg
from tqdm import tqdm

# Turn sigle 'scene_graphs.json' into seperate files per image
def gen_files_by_id():
    vg.save_scene_graphs_by_id(data_dir='data/', image_data_dir='data/by-id/')

#  Function to get scene graph objects from the data file 'data/by-id/'
def get_scene_graphs(start_index=0, end_index=-1,min_rels=0):
    temp = []
    for i in tqdm(range(end_index)):
       temp.append(vg.get_scene_graph(i)) 

    return temp

