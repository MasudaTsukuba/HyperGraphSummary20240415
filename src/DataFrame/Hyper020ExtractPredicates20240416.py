

import pandas as pd
from  Hyper000Common20240621 import read_prefix, read_dataframe
# prefix = ''


# def read_dataframe(csv_file_path):
#     with open('../../../prefix', 'r') as file:
#         prefix_ = file.read()
#     df = pd.read_csv(csv_file_path)
#     return df, prefix_


def extract_predicates(df, prefix):
    predicates = df['predicate'].unique()
    print('number of unique predicates:', len(predicates))
    unique_predicates = pd.DataFrame(predicates, columns=['predicate']).sort_values(by=['predicate'])
    unique_predicates.to_csv(f'../../data/{prefix}_020_unique_predicates.csv', index=False)
    pass


def extract_subject_predicate_pairs(df, prefix):
    subject_predicate_pairs = df[['subject', 'predicate']].drop_duplicates(subset=['subject', 'predicate'])
    print('number of subject predicate pairs:', len(subject_predicate_pairs))
    unique_subject_predicate_pairs = (pd.DataFrame(subject_predicate_pairs, columns=['subject', 'predicate'])
                         .sort_values(by=['subject', 'predicate']))
    unique_subject_predicate_pairs.to_csv(f'../../data/{prefix}_030_unique_subject_predicate_pairs.csv', index=False)
    # print('number of subject predicate pairs:', len(unique_subject_predicate_pairs))


def main(csv_file_path):
    print('Hyper020ExtractPredicates20240416.py.')
    df = read_dataframe(csv_file_path)
    prefix = read_prefix()
    extract_predicates(df, prefix)
    extract_subject_predicate_pairs(df, prefix)


if __name__ == '__main__':
    prefix = read_prefix()
    csv_file_path = f'../../data/{prefix}_010_all_triples.csv'
    main(csv_file_path)
