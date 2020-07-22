# Readme


To get the data please download from https://drive.google.com/file/d/1cIHIIp9dQ5FA2--pF6LjtxB47vqyDIzH/view?usp=sharing
This will supply all of the data of the generated datasets and the visual genome data.
This file should be unzipped and placed in this directory. (there shold now be a 'data' file within this directory)

Install all of the dependencies from the pipfile or requirements.txt. 
Make sure that python version is at least version 3. I used Python 3.6.9

To demo the functions created in this project please see the demo video or run the jupyter notebook 'demo.ipynb'.


To get repeatable results for the tests I performed please run the file titled tests.py. This will run all tests on all oracles and print results out. 
This will take some time therefore you can comment out any tests you dont want to run etc.


side notes:
	sg_to_nx_graph.py - contains methods used to convery scene graphs to networkx graphs for datasets 1-8
	sg_to_nx_graph2.py - contains methods used to convery scene graphs to networkx graphs for datasets 9-16
	sg_to_nx_graph3.py - contains methods used to convery scene graphs to networkx graphs for datasets 17-24
