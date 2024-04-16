
import re
import pandas as pd


def read_dataframe():
    df = pd.read_csv('../data/all_triples.csv')
    return df


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


def extract_subjects(df):
    subjects = df['subject'].unique()
    print(len(subjects))
    unique_subjects = pd.DataFrame(subjects, columns=['subject']).sort_values(by=['subject'])
    unique_subjects.to_csv('../data/unique_subjects.csv', index=False)
    pass


def extract_subject_authorities(df):
    subjects = df['subject'].unique()
    list_of_subjects = list(subjects)
    root_of_subjects = create_tree(list_of_subjects)
    subject_authorities = root_of_subjects.get_authorities()
    df_subject_authorities = pd.DataFrame(subject_authorities, columns=['subject_authority'])
    df_subject_authorities.to_csv('../data/subject_authorities.csv', index=False)


def main():
    df = read_dataframe()
    extract_subjects(df)
    extract_subject_authorities(df)


if __name__ == '__main__':
    main()
