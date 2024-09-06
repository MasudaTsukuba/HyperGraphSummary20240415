#
# import tkinter as tk
import pandas as pd
from rdflib import Graph, URIRef
import pydot
# import networkx as nx
# import matplotlib
# import matplotlib.pyplot as plt

df = pd.read_csv('../../data/unique_authority_triples.csv')
g = Graph()
# nx_graph = nx.Graph()
# matplotlib.use('TkAgg', force=True)

for index, row in df.iterrows():
    try:
        s = row['subject_authority'].replace(' [ODP]', '')
        p = row['predicate']
        o = row['object_authority'].replace(' [ODP]', '')
        g.add((URIRef(s), URIRef(p), URIRef(o)))
    except Exception:
        pass

g.serialize('../data/unique_authority_graph.ttl', format='ttl')
# dot_data = g.serialize(format='dot')
# graph = pydot.graph_from_dot_data(dot_data.encode('utf-8'))
# image_path = '../data/rdf_graph.png'
# graph[0].write_png(image_path)
# plt.figure(figsize=(8, 8))
# pos = nx.spring_layout(nx_graph)
# nx.draw(nx_graph, pos, with_labels=True, node_color='skyblue', node_size=2000, edge_color='black', linewidths=1, font_size=15, arrows=True)
# plt.show()
