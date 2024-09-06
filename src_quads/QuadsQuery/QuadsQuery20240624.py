"""
QuadQuery20240624.py
Execute a quad query against a guad graph 'quad_grap.jsonld' created by CreateQuadGraph20240624.py
2024/6/24, T. Masuda
Amagasa Laboratory, University of Tsukuba
"""

import os

from rdflib import ConjunctiveGraph
# from src_quads.QuadsQuery.SparqlParse20240624 import SparqlParse
from src_quads.QuadsQuery.ConvertQuery20240703 import ConvertQuery
# sparql_parse = SparqlParse()
convert_query = ConvertQuery()  # create an instance of ConvertQuery

cg = ConjunctiveGraph()  # create an instance of ConjunctiveGraph

cg.parse('./QuadsCreate/quad_graph.jsonld')  # read the input file

query_string = """
SELECT * WHERE { GRAPH ?g {?s ?p ?o . }}
"""  # read all the quads
results = cg.query(query_string)  # get the results
xxx = results.bindings  # extract the results
print(len(xxx))
pass

query_string = """  # another query
SELECT * WHERE { 
GRAPH ?g1 {?s <http://www.w3.org/2002/07/owl#sameAs> ?o . }
}
"""
results = cg.query(query_string)
xxx = results.bindings
print(len(xxx))
pass

query_path = '/media/masuda/HDS2-UT/IdeaProjects/quetsal20150315/queries/'  # queries for Quetsal
query_files = os.listdir(query_path)
for query_file in query_files:
    if not query_file.startswith('B'):
        print(query_file)
        with open(query_path + query_file, 'r') as query_input_file:
            query_string = query_input_file.read()
            # B1
            #         query_string = """
            #         PREFIX tcga: <http://tcga.deri.ie/schema/>
            # SELECT  ?expValue
            # WHERE
            # {
            #   {
            #    ?s	tcga:bcr_patient_barcode	<http://tcga.deri.ie/TCGA-37-3789>.
            #    <http://tcga.deri.ie/TCGA-37-3789>	tcga:result	?results.
            #    ?results  tcga:RPKM ?expValue.
            #   }
            # UNION
            #   {
            #    ?uri	tcga:bcr_patient_barcode	<http://tcga.deri.ie/TCGA-37-3789>.
            #    <http://tcga.deri.ie/TCGA-37-3789>	tcga:result	?geneResults.
            #    ?geneResults  tcga:scaled_estimate ?expValue.
            #   }
            # }
            #         """

            # query_string = """
            #         PREFIX tcga: <http://tcga.deri.ie/schema/>
            # SELECT  ?expValue
            # WHERE
            # {
            #    ?s	tcga:bcr_patient_barcode	<http://tcga.deri.ie/TCGA-37-3789>.
            #    <http://tcga.deri.ie/TCGA-37-3789>	tcga:result	?results.
            #    ?results  tcga:RPKM ?expValue.
            #   }
            #         """

            # C1
            # query_string = """
            # PREFIX drugbank: <http://www4.wiwiss.fu-berlin.de/drugbank/resource/drugbank/>
            #     PREFIX drugtype: <http://www4.wiwiss.fu-berlin.de/drugbank/resource/drugtype/>
            #     PREFIX kegg: <http://bio2rdf.org/ns/kegg#>
            #     PREFIX chebi: <http://bio2rdf.org/ns/bio2rdf#>
            #     PREFIX purl: <http://purl.org/dc/elements/1.1/>
            #     SELECT distinct ?drug	?drugDesc ?molecularWeightAverage 	?compound   ?ReactionTitle    ?ChemicalEquation
            #     WHERE
            #     {{
            #     ?drug 			drugbank:description 	 ?drugDesc .
            #     ?drug 			drugbank:drugType 	 drugtype:smallMolecule .
            #     ?drug 	     drugbank:keggCompoundId ?compound.
            #     ?enzyme 		kegg:xSubstrate 	?compound .
            #     ?Chemicalreaction 	kegg:xEnzyme 		?enzyme .
            #     ?Chemicalreaction	kegg:equation 		?ChemicalEquation .
            #     ?Chemicalreaction 	purl:title 		?ReactionTitle
            #     OPTIONAL
            #         {
            #             ?drug drugbank:molecularWeightAverage ?molecularWeightAverage.
            #             FILTER (?molecularWeightAverage > 114)
            #         }
            #     }
            #     UNION{
            #     ?drug 			drugbank:description 	 ?drugDesc .
            #     }}
            #     Limit 1000
            # """
            converted_query_string = convert_query.convert_query(query_string.replace('\t', ' '))  # convert the query
            if converted_query_string != '':
                rrr = cg.query(query_string)
                # converted_query_string = """
                # ELECT *
                # WHERE {
                # {
                # GRAPH ?graph1
                # { ?drug <http://www4.wiwiss.fu-berlin.de/drugbank/resource/drugbank/description> ?drugDesc . }
                #
                # OPTIONAL { GRAPH ?graph8
                # {
                #  ?drug <http://www4.wiwiss.fu-berlin.de/drugbank/resource/drugbank/molecularWeightAverage> ?molecularWeightAverage . }
                #  FILTER (?molecularWeightAverage > "114"^^<http://www.w3.org/2001/XMLSchema#integer>)
                # }}
                # UNION
                # {
                # GRAPH ?graph9
                # { ?drug <http://www4.wiwiss.fu-berlin.de/drugbank/resource/drugbank/description> ?drugDesc . }
                # }
                # }
                #                 """
                try:
                    results = cg.query(converted_query_string)  # get the results
                    xxx = results.bindings
                    print('   ', len(xxx))
                    # print(xxx)
                except Exception as e:
                    pass
                pass
