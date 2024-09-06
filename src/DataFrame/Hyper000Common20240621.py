import os

import pandas as pd
import re


def read_prefix():
    with open('../../../prefix', 'r') as file:
        prefix_ = file.read()
    return prefix_


def write_prefix(prefix):
    with open('../../prefix', 'w') as file:
        file.write(prefix)


def read_dataframe(csv_file_path):
    print('reading to data frame:', csv_file_path)
    # col_names = ['s', 'p', 'o', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    col_names = []
    col_names.append('subject')
    col_names.append('predicate')
    col_names.append('object')
    for i in range(2000):
        col_names.append(str(i))
    df = pd.read_csv(csv_file_path, names=col_names, quotechar='"', skipinitialspace=True, dtype=str)  # important!!! skipinitialspace=True to allow a space after a comma
    return df


def split_string(string):
    path = []
    if type(string) == float:
        path0 = '<http:__literal>'
        return path
    if string.startswith('_:'):
        string = 'http://blank'
    path0 = (str(string).replace('<', '').replace('>', '')
             .replace('http://', 'http:__')
             .replace('file:///', 'file:___'))
    if path0.startswith('http'):
        pass
    elif path0.startswith('file:'):
        path0 = 'http:__file'
    else:
        path0 = 'http:__literal'
    # if path0.find('file://') >= 0:
    #     path0 = path0.replace('file:///', 'file:___')
    if path0.endswith('/'):
        path0 = path0[:-1]
    if path0.startswith('http'):
        path = re.split(r'(?<=[^"])/|/(?=[^"])', path0)
    return path


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

    def add_to_tree(root_, path_):
        current_node = root_
        for segment in path_:
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
        # if string.startswith('_:'):
        #     string = 'http://blank'
        # path0 = (str(string).replace('<', '').replace('>', '')
        #          .replace('http://', 'http:__')
        #          .replace('file:///', 'file:___'))
        # if path0.startswith('http'):
        #     pass
        # elif path0.startswith('file:'):
        #     pass
        # else:
        #     path0 = 'http:__literal'
        # # if path0.find('file://') >= 0:
        # #     path0 = path0.replace('file:///', 'file:___')
        # if path0.endswith('/'):
        #     path0 = path0[:-1]
        # if path0.startswith('http'):
        #     path = re.split(r'(?<=[^"])/|/(?=[^"])', path0)
        string = string.strip()
        path = split_string(string)
        if path != []:
            add_to_tree(root, path)

    # Print the tree structure
    # print_tree(root)
    return root


def extract_predicates(df, prefix):
    print('extract_predicates')
    predicates = df['predicate'].unique()
    print('number of unique predicates:', len(predicates))
    unique_predicates = pd.DataFrame(predicates, columns=['predicate']).sort_values(by=['predicate'])
    unique_predicates.to_csv(f'../../data/{prefix}_020_unique_predicates.csv', index=False)
    pass


def extract_subject_predicate_pairs(df, prefix):
    print('extract_subject_predicate_pairs')
    # df_xxx = df[['subject', 'predicate']]
    # df_xxx.to_csv(f'../../data/{prefix}_030_xxx_subject_predicate_pairs.csv', index=False)  # debug
    subject_predicate_pairs = df[['subject', 'predicate']].drop_duplicates(subset=['subject', 'predicate'])
    # subject_predicate_pairs.to_csv(f'../../data/{prefix}_030_subject_predicate_pairs.csv', index=False)  # debug
    print('number of subject predicate pairs:', len(subject_predicate_pairs))
    unique_subject_predicate_pairs = (pd.DataFrame(subject_predicate_pairs, columns=['subject', 'predicate'])
                         .sort_values(by=['subject', 'predicate']))
    unique_subject_predicate_pairs.to_csv(f'../../data/{prefix}_030_unique_subject_predicate_pairs.csv', index=False)
    # print('number of subject predicate pairs:', len(unique_subject_predicate_pairs))


def extract_subjects(df, prefix):
    print('extract_subjects')
    subjects = df['subject'].unique()
    print('number of unique subjects:', len(subjects))
    unique_subjects = pd.DataFrame(subjects, columns=['subject']).sort_values(by=['subject'])
    unique_subjects.to_csv(f'../../data/{prefix}_040_unique_subjects.csv', index=False)
    pass


def extract_subject_authorities(df, prefix):
    print('extract_subject_authorities')
    subjects = df['subject'].unique()
    list_of_subjects = list(subjects)
    root_of_subjects = create_tree(list_of_subjects)
    subject_authorities = root_of_subjects.get_authorities()
    df_subject_authorities = pd.DataFrame(subject_authorities, columns=['subject_authority'])
    df_subject_authorities.to_csv(f'../../data/{prefix}_050_subject_authorities.csv', index=False)


def extract_objects(df, prefix):
    print('extract_objects')
    objects = df['object'].unique()
    print('number of objects:', len(objects))
    unique_objects = pd.DataFrame(objects, columns=['object']).sort_values(by=['object'])
    unique_objects.to_csv(f'../../data/{prefix}_060_unique_objects.csv', index=False)
    pass


def extract_object_authorities(df, prefix):
    print('extract_object_authorities')
    objects = df['object'].unique()
    list_of_objects = list(objects)
    list_of_objects2 = []
    for ooo in list_of_objects:
        if ooo:
            list_of_objects2.append(ooo.strip())
    root_of_objects = create_tree(list_of_objects2)
    object_authorities = root_of_objects.get_authorities()
    df_object_authorities = pd.DataFrame(object_authorities, columns=['object_authority'])
    df_object_authorities.to_csv(f'../../data/{prefix}_070_object_authorities.csv', index=False)


def extract_authority(input_string, subject=True):
    pattern = r'(?<=[^"])/|/(?=[^"])'  # ignore / within double quotes
    parts = re.split(pattern, input_string)
    authority = parts[0]
    # if not authority.startswith('http:__'):  # blank nodes and literals
    #     authority = 'http://blank'
    # if not subject:
    #     authority = 'http://literal'
    authority = authority.replace('http:__', 'http://')  # convert back to http://
    return authority


def extract_common_authorities(df, prefix):
    print('extract_common_authorities')
    # df = read_dataframe(csv_file_path)
    # prefix = read_prefix()
    new_triple_data: list[tuple[str, str, str]] = []
    new_vertex_data: list[tuple[str, str]] = []
    for index, row in df.iterrows():
        subject = str(row['subject']).strip()
        predicate = str(row['predicate']).strip()
        object_ = str(row['object']).strip()
        # subject_authority = extract_authority(subject.replace('http://', 'http:__'))
        # object_authority = extract_authority(object_.replace('http://', 'http:__'), subject=False)
        # if subject_authority != 'http://blank' and object_authority != 'http://blank':
        #     new_triple_data.append((subject_authority, predicate, object_authority))
        #     new_vertex_data.append((subject_authority, subject_authority))
        #     new_vertex_data.append((object_authority, object_authority))
        try:
            subject_authority = split_string(subject)[0].replace('http:__', 'http://')
            subject_authority = f'<{subject_authority}>'
            object_authority = split_string(object_)[0].replace('http:__', 'http://')
            object_authority = f'<{object_authority}>'
            if object_authority.find('http://dbpedia') >= 0:
                pass  # debug
            new_triple_data.append((subject_authority, predicate, object_authority))
            new_vertex_data.append((subject_authority, subject_authority))
            new_vertex_data.append((object_authority, object_authority))
        except Exception as e:
            pass  # error
    # df_authority = pd.DataFrame(new_data, columns=['subject_authority', 'predicate', 'object_authority'])
    # unique_df_authority = df_authority.drop_duplicates(subset=['subject_authority', 'predicate', 'object_authority'])
    df_authority = pd.DataFrame(new_triple_data, columns=['Source', 'label', 'Target'])
    unique_df_authority = df_authority.drop_duplicates(subset=['Source', 'label', 'Target'])
    print('number of unique authorities:', len(unique_df_authority))
    unique_df_authority.to_csv(f'../../data/{prefix}_080_unique_authority_triples.csv', index=False)

    df_vertex = pd.DataFrame(new_vertex_data, columns=['Id', 'label'])
    unique_df_vertex = df_vertex.drop_duplicates(subset=['Id', 'label'])
    unique_df_vertex.to_csv(f'../../data/{prefix}_090_unique_authority_vertices.csv', index=False)


def merge_csv(prefix_string):
    data_path = f'../../data/'
    related_files = os.listdir(data_path)
    for index in range(1020, 1100, 10):  # 20, 30, 40, 50, 60, 70, 80, 90
        index_string = str(index)[1:]
        if index == 1020 or index == 1050 or index == 1070 or index == 1080 or index == 1090:  # 2024/9/3
            pass
            df = None
            output_file = ''
            initial = True  # special treatment for the first time
            for related_file in related_files:
                if related_file.startswith(prefix_string) \
                        and related_file.find(index_string) >= 0 \
                        and related_file.find('part_') >= 0:
                    if initial:
                        df = pd.read_csv(data_path + related_file, quotechar='"')
                        output_file = data_path + prefix_string + '_' + str(related_file)[related_file.find(index_string):]  # special treatment for the first time
                        initial = False
                        pass
                    else:
                        df2 = pd.read_csv(data_path + related_file, quotechar='"')
                        try:
                            df = pd.merge(df, df2, how='outer')
                        except Exception as e:
                            pass  # error
            if df is not None:
                df.to_csv(output_file, index=False)
        pass


def process_segment(csv_file_path, prefix):
    # main010(data_path, csv_file_path)

    df = read_dataframe(csv_file_path)  # read csv file into pandas dataframe

    # main020(csv_file_path)
    extract_predicates(df, prefix)  # extract predicates and save it into a file
    # extract_subject_predicate_pairs(df, prefix)  # extract subject-predicate pairs

    # main022(csv_file_path)
    # extract_subjects(df, prefix)
    extract_subject_authorities(df, prefix)

    # main024(csv_file_path)
    # extract_objects(df, prefix)
    extract_object_authorities(df, prefix)

    # main030(csv_file_path)
    extract_common_authorities(df, prefix)


def remove_work_files():
    data_path = f'../../data/'
    files = os.listdir(data_path)
    for file in files:
        if file.find('part_') >= 0:
            os.remove(data_path + file)
    pass


def process_all(root_path, prefix_string):
    prefix = prefix_string
    part_files = os.listdir(root_path)  # get the list of part_** files
    for part_file in part_files:  # process individual part_** file
        # if part_file.startswith('part_'):
        if part_file.startswith('part_kb'):  # 2024/9/3
            csv_file_path = root_path + part_file
            prefix = prefix_string + part_file
            write_prefix(prefix)
            process_segment(csv_file_path, prefix)
    merge_csv(prefix_string)  # and finally merge the results for all the part_** files
    # remove_work_files()  # delete unnecessary files
