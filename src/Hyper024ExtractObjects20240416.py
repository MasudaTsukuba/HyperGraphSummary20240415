
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
        path0 = str(string).replace('http://', 'http:__')
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


def extract_objects(df):
    objects = df['object'].unique()
    print(len(objects))
    unique_objects = pd.DataFrame(objects, columns=['object']).sort_values(by=['object'])
    unique_objects.to_csv('../data/unique_objects.csv', index=False)
    pass


def extract_object_authorities(df):
    objects = df['object'].unique()
    list_of_objects = list(objects)
    root_of_objects = create_tree(list_of_objects)
    object_authorities = root_of_objects.get_authorities()
    df_object_authorities = pd.DataFrame(object_authorities, columns=['object_authority'])
    df_object_authorities.to_csv('../data/object_authorities.csv', index=False)


def main():
    df = read_dataframe()
    extract_objects(df)
    extract_object_authorities(df)


if __name__ == '__main__':
    main()
