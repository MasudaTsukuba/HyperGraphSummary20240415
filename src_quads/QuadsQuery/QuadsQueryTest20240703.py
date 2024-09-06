"""
QuadsQueryTest20240703.py
2024/7/3, T. Masuda
Amagasa laboratory, University of Tsukuba
"""
import os
from rdflib import ConjunctiveGraph
# from src_quads.QuadsQuery.SparqlParse20240624 import SparqlParse
from src_quads.QuadsQuery.ConvertQuery20240703 import ConvertQuery

# sparql_parse = SparqlParse()
convert_query = ConvertQuery()  # create an instance of ConvertQuery
cg = ConjunctiveGraph()  # create am instance of ConjunctiveGraph
cg.parse('./QuadsCreate/quad_graph.jsonld')  # read the graph data

# query C4
query_string = """
SELECT ?predicate ?object WHERE {
   { <http://dbpedia.org/resource/Barack_Obama> ?predicate ?object }
   UNION    
   { ?subject <http://www.w3.org/2002/07/owl#sameAs> <http://dbpedia.org/resource/Barack_Obama> .
     ?subject ?predicate ?object } 
}
"""

converted_query_string = convert_query.convert_query(query_string.replace('\t', ' '))  # convert the query
try:
    results = cg.query(converted_query_string)  # execute the query
    xxx = results.bindings  # get the results
    print('   ', len(xxx))
    print(xxx)
except Exception as e:
    pass
