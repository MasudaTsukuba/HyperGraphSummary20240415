

import pandas as pd


def read_dataframe():
    df = pd.read_csv('../data/all_triples.csv')
    return df


def extract_predicates(df):
    predicates = df['predicate'].unique()
    print(len(predicates))
    unique_predicates = pd.DataFrame(predicates, columns=['predicate']).sort_values(by=['predicate'])
    unique_predicates.to_csv('../data/unique_predicates.csv', index=False)
    pass


def extract_subject_predicate_pairs(df):
    subject_predicate_pairs = df[['subject', 'predicate']].drop_duplicates(subset=['subject', 'predicate'])
    print(len(subject_predicate_pairs))
    unique_subject_predicate_pairs = (pd.DataFrame(subject_predicate_pairs, columns=['subject', 'predicate'])
                         .sort_values(by=['subject', 'predicate']))
    unique_subject_predicate_pairs.to_csv('../data/unique_subject_predicate_pairs.csv', index=False)
    print(len(unique_subject_predicate_pairs))


def main():
    df = read_dataframe()
    extract_predicates(df)
    extract_subject_predicate_pairs(df)


if __name__ == '__main__':
    main()
