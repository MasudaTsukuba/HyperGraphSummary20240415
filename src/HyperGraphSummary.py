"""
HyperGraphSummary.py
2024/4/15, T. Masuda
Amagasa Laboratory, University of Tsukuba
"""
import os, re

import rdflib
from rdflib import Graph

data_path = '/media/masuda/HDS2-UT/QuetsalData20240401/8898.SWDFood'
g = Graph()

set_of_predicates = set()
# list_of_predicates = []
set_of_subjects = set()
list_of_subjects = []
set_of_subject_predicate_pairs = set()
set_of_objects = set()
list_of_objects = []
set_of_triples = set()
list_of_triples = []


def read_rdf_files():
    files = os.listdir(data_path)
    for file in files:
        if file.endswith('.rdf') and file != 'iswc-aswc-2007-complete.rdf':
            # print(file)
            try:
                g.parse(data_path+'/'+file)
            except Exception as e:
                print(e)
    print('length of graph: ', len(g))


def create_tree(input_strings):
    class TreeNode:
        def __init__(self, value):
            self.value = value
            self.children = {}

        def get_authorities(self):
            authorities = []
            for child in self.children:
                authorities.append(child)
            return authorities

    def add_to_tree(root, path):
        current_node = root
        for segment in path:
            if segment not in current_node.children:
                current_node.children[segment] = TreeNode(segment)
            current_node = current_node.children[segment]

    def print_tree(node, depth=0):
        if node is None:
            return
        print("  " * depth + node.value)
        for child in node.children.values():
            print_tree(child, depth + 1)

    # Create the root node of the tree
    root = TreeNode("")

    # Add each path to the tree
    for string in input_strings:
        path0 = string.replace('http://', 'http:__')
        if path0.find('file://') >= 0:
            path0 = path0.replace('file:///', 'file:___')
        if path0.endswith('/'):
            path0 = path0[:-1]
        if path0.startswith('http'):
            path = re.split(r'(?<=[^"])/|/(?=[^"])', path0)
            add_to_tree(root, path)

    # Print the tree structure
    print_tree(root)
    return root


def extract_predicates():
    query_string = """SELECT DISTINCT ?predicate WHERE { ?subject ?predicate ?object . } ORDER BY ?predicate """
    results = g.query(query_string)

    for result in results.bindings:
        set_of_predicates.add(result[rdflib.term.Variable('predicate')])
    print('number of predicates: ', len(set_of_predicates))
    list_of_predicates_ = list(set_of_predicates)
    list_of_predicates_.sort()
    root_of_predicates_ = create_tree(list_of_predicates_)
    return list_of_predicates_, root_of_predicates_


def extract_subjects():
    for predicate in set_of_predicates:
        query_string = f"""SELECT DISTINCT ?subject WHERE {{ ?subject <{predicate}> ?object . }} ORDER BY ?subject"""
        results = g.query(query_string)
        for result in results.bindings:
            subject = result[rdflib.term.Variable('subject')]
            if type(subject) is rdflib.term.BNode:
                pass
            else:
                set_of_subjects.add(subject)
                set_of_subject_predicate_pairs.add((subject, predicate))
    list_of_subjects_ = list(set_of_subjects)
    list_of_subjects_.sort()
    print('number of subjects: ', len(set_of_subjects))
    root_of_subjects_ = create_tree(list_of_subjects_)

    list_of_subject_predicate_pairs_ = list(set_of_subject_predicate_pairs)
    list_of_subject_predicate_pairs_.sort()
    print('number of subject-predicate pairs: ', len(set_of_subject_predicate_pairs))
    return list_of_subjects_, root_of_subjects_, list_of_subject_predicate_pairs_


def extract_objects():
    for index, subject_predicate_pair in enumerate(set_of_subject_predicate_pairs):
        subject = subject_predicate_pair[0]
        predicate = subject_predicate_pair[1]
        query_string = f"""SELECT DISTINCT ?object WHERE {{ <{subject}> <{predicate}> ?object . }} ORDER BY ?object"""
        results = g.query(query_string)
        for result in results.bindings:
            object_ = result[rdflib.term.Variable(rdflib.term.Variable('object'))]
            if type(object_) is rdflib.term.Literal:
                pass
            else:
                set_of_objects.add(object_)
                set_of_triples.add((subject, predicate, object_))
    list_of_objects_ = list(set_of_objects)
    list_of_objects_.sort()
    print('number of objects: ', len(set_of_objects))
    root_of_objects_ = create_tree(list_of_objects_)
    list_of_triples_ = list(set_of_triples)
    list_of_triples_.sort()
    print('number of triples: ', len(set_of_triples))
    return list_of_objects_, root_of_objects_, list_of_triples_


def main():
    read_rdf_files()
    list_of_predicates, root_of_predicates = extract_predicates()
    list_of_subjects, root_of_subjects, list_of_subject_predicate_pairs = extract_subjects()
    subject_authorities = root_of_subjects.get_authorities()
    list_of_objects, root_of_objects, list_of_triples = extract_objects()
    object_authorities = root_of_objects.get_authorities()
    pass


if __name__ == '__main__':
    main()
