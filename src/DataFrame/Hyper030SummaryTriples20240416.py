"""
Hyper030SummaryTriples20240416.py
Create a CSV file for Gephi visualization software
2024/4/16, T. Masuda
Amagasa Laboratory, University of Tsukuba
"""
import pandas as pd
import re
from Hyper000Common20240621 import read_prefix, read_dataframe
# prefix = ''


# def read_dataframe():
#     with open('../../../prefix', 'r') as file:
#         prefix_ = file.read()
#     df = pd.read_csv(f'../../data/{prefix_}_010_all_triples.csv')  # created by Hyper010Rdf2Df20240416.py
#     return df, prefix_


def extract_authority(input_string, subject=True):
    pattern = r'(?<=[^"])/|/(?=[^"])'  # ignore / within double quotes
    parts = re.split(pattern, input_string)
    authority = parts[0]
    if not authority.startswith('http:__'):  # blank nodes and literals
        authority = 'http://blank'
        # if not subject:
        #     authority = 'http://literal'
    authority = authority.replace('http:__', 'http://')  # convert back to http://
    return authority


def extract_common_authorities(csv_file_path):
    print('extract_common_authorities')
    df = read_dataframe(csv_file_path)
    prefix = read_prefix()
    new_triple_data: list[tuple[str, str, str]] = []
    new_vertex_data: list[tuple[str, str]] = []
    for index, row in df.iterrows():
        subject = str(row['subject'])
        predicate = str(row['predicate'])
        object_ = str(row['object'])
        subject_authority = extract_authority(subject.replace('http://', 'http:__'))
        object_authority = extract_authority(object_.replace('http://', 'http:__'), subject=False)
        if subject_authority != 'http://blank' and object_authority != 'http://blank':
            new_triple_data.append((subject_authority, predicate, object_authority))
            new_vertex_data.append((subject_authority, subject_authority))
            new_vertex_data.append((object_authority, object_authority))
    # df_authority = pd.DataFrame(new_data, columns=['subject_authority', 'predicate', 'object_authority'])
    # unique_df_authority = df_authority.drop_duplicates(subset=['subject_authority', 'predicate', 'object_authority'])
    df_authority = pd.DataFrame(new_triple_data, columns=['Source', 'label', 'Target'])
    unique_df_authority = df_authority.drop_duplicates(subset=['Source', 'label', 'Target'])
    print('number of unique authorities:', len(unique_df_authority))
    unique_df_authority.to_csv(f'../../data/{prefix}_080_unique_authority_triples.csv', index=False)

    df_vertex = pd.DataFrame(new_vertex_data, columns=['Id', 'label'])
    unique_df_vertex = df_vertex.drop_duplicates(subset=['Id', 'label'])
    unique_df_vertex.to_csv(f'../../data/{prefix}_090_unique_authority_vertices.csv', index=False)


if __name__ == '__main__':
    prefix = read_prefix()
    csv_file_path = f'../../data/{prefix}_010_all_triples.csv'
    extract_common_authorities(csv_file_path)
