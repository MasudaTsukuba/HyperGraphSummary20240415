"""
QuadsTest20240624.py
Just test the guad graph using Conjunctive Graph
2024/6/24, T. Masuda
Amagasa Laboratory, University of Tsukuba
"""
from rdflib import Graph, ConjunctiveGraph

cg = ConjunctiveGraph()  # create an instance of Conjunctive Graph

cg.parse('test.nquads')  # read graph data
length = len(cg)  # length is 1
my_query = """SELECT * WHERE { GRAPH ?g {?s ?p ?o . }}"""  # query
contexts = cg.contexts()  # ???
for context in contexts:
    pass
results = cg.query(my_query)  # execute a query
xxx = results.bindings
yyy = xxx[0]  # get the first result
sss = yyy['s']  # subject
ggg = yyy['g']  # graph
pass
