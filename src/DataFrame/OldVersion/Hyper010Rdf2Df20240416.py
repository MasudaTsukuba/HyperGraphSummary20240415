"""
Hyper010Rdf2Df20240416.py
2024/4/16, T. Masuda
Amagasa Laboratory, University of Tsukuba
"""
import os
import pandas as pd
import rdflib
from rdflib import Graph

# data_path = '/media/masuda/HDS2-UT/QuetsalData20240401/8898.SWDFood'
data_path = '/media/masuda/HDS2-UT/QuetsalData20240401/8893.GeoNames'
prefix = data_path.split('/')[-1]
with open('../../../prefix', 'w') as file:
    file.write(prefix)

g = Graph()


def read_rdf_files():
    files = os.listdir(data_path)
    for file in files:
        if (file.endswith('.rdf') and file != 'iswc-aswc-2007-complete.rdf') or file.endswith('.n3'):
            # print(file)
            try:
                g.parse(data_path+'/'+file)
            except Exception as e:
                print(e)
    print('length of graph: ', len(g))


def save_to_dataframe():
    query_string = f"""SELECT ?subject ?predicate ?object WHERE {{ ?subject ?predicate ?object . }}"""
    results = g.query(query_string)
    data = []
    for result in results.bindings:
        subject = str(result[rdflib.term.Variable('subject')])
        predicate = str(result[rdflib.term.Variable('predicate')])
        object_ = str(result[rdflib.term.Variable('object')])
        data.append((subject, predicate, object_))
    graph_dataframe_ = pd.DataFrame(data, columns=['subject', 'predicate', 'object'])
    sorted_df = graph_dataframe_.sort_values(by=['predicate', 'subject', 'object'])
    sorted_df.to_csv(f'../../data/{prefix}_010_all_triples.csv', index=False)
    print('length of sorted df:', len(sorted_df))
    return graph_dataframe_


def main():
    read_rdf_files()
    graph_dataframe = save_to_dataframe()
    # list_of_predicates, root_of_predicates = extract_predicates()
    # list_of_subjects, root_of_subjects, list_of_subject_predicate_pairs = extract_subjects()
    # subject_authorities = root_of_subjects.get_authorities()
    # list_of_objects, root_of_objects, list_of_triples = extract_objects()
    # object_authorities = root_of_objects.get_authorities()
    pass


if __name__ == '__main__':
    main()
