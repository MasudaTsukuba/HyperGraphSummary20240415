import pandas as pd

input_path = '/home/masuda/test20240830.csv'
df = pd.read_csv(input_path, quotechar='"', skipinitialspace=True)
print(df)
pass
with open(input_path, 'r') as input_file:
    lines = input_file.readlines()
    print(lines)
    pass

input_path = '/media/masuda/HDS2-UT/QuetsalData20240401/csv/8890.ChEBI/'

with open(input_path + 'part_ae', 'r') as input_file:
    for index, line in enumerate(input_file):
        if line.find('http://bio2rdf.org/chebi:43780') >= 0 and line.find('http://purl.org/dc/elements/1.1/title') >= 0:
            print(index, line)
        if line.find('http://bio2rdf.org/chebi:49108') >= 0 and line.find(
                'http://bio2rdf.org/ns/bio2rdf#synonym') >= 0:
            print(index, line)
