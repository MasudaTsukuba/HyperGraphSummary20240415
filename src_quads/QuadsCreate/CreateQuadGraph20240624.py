"""
CreateQuadGraph20240624.py
Create a quad graph from the hyper graph summaries
2024/6/24, T. Masuda
Amagasa Laboratory, University of Tsukuba
"""

import os
from rdflib import ConjunctiveGraph, URIRef  # use ConjunctiveGraph for the quad graph

cg = ConjunctiveGraph()  # create an instance of ConjunctiveGraph
data_path = '../../data/'  # Hyper graph summaries are here
files = os.listdir(data_path)
for file in files:
    if file.find('_080_') >= 0 and file.find('part') < 0:  # file for Source (subject), label (predicate), Target (object)
        prefix = file.split('_')[0]  # generate a graph name from the file name
        with open(data_path + file, 'r') as input_file:
            lines = input_file.readlines()  # read all the lines at once
            for index, line in enumerate(lines):  # process each line
                if index > 0:  # skip the title line
                    terms = line.split(',')  # file is in CSV format
                    subj = terms[0].replace('\n', '')  # ???
                    subj = URIRef(subj.replace('<', '').replace('>', ''))  # remove < and > and convert to URIRef
                    pred = terms[1]
                    pred = URIRef(pred.replace('<', '').replace('>', ''))
                    obje = terms[2].replace('\n', '')
                    obje = URIRef(obje.replace('<', '').replace('>', ''))
                    graph = URIRef(f'http://{prefix}')  # graph name
                    cg.add((subj, pred, obje, graph))  # add a quad
        pass
cg.serialize(destination='quad_graph.jsonld', format='json-ld')  # save into a file
pass
