import os

input_folder = '/media/masuda/HDS2-UT/QuetsalData20240401/nt/8891.DBPedia-Subset.nt/'
input_file_all = input_folder + 'dbpedia_all.nt'

with open(input_file_all, 'r') as input_file:
    for index, line in enumerate(input_file):
        if index % 100000 == 0:
            if index % 10000000 == 0:
                print()
            print('.', end='')
        try:
            parts = line.split()
            if parts[1].startswith('<http://'):
                pass
            else:
                print()
                print(line)
        except Exception as e:
            print()
            print(e, line)
