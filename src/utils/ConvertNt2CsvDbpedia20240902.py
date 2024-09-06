import os

input_folder = '/media/masuda/HDS2-UT/QuetsalData20240401/nt/8891.DBPedia-Subset.nt/'
input_paths = os.listdir(input_folder)
output_folder = '/media/masuda/HDS2-UT/QuetsalData20240401/csv/8891.DBPedia-Subset/'

for input_path in input_paths:
    # if input_path.startswith('part_'):
    if input_path.startswith('part_jj'):
        print(input_path)
        with open(input_folder+input_path, 'r') as input_file:
            with open(output_folder + input_path, 'w') as output_file:
                for line in input_file:
                    try:
                        line = line.replace(' .\n', '\n')
                        parts = line.split(' ')
                        subj = parts[0]
                        pred = parts[1]
                        obje = ' '.join(parts[2:])
                        if obje.find('\n') >= 0:
                            obje = obje.replace('\n', '')  # 2024/9/5
                        if obje.find('^^') >= 0:
                            obje = obje.split('^^')[0]
                        if obje == '"':
                            obje = '"_"'  # 2024/9/5
                        if obje.find('\\""@en') >= 0 and obje.find('etc') >= 0:
                            obje = obje.replace('\\""@en', '"')
                        if pred.startswith('<http'):
                            output_file.write(subj+','+pred+','+obje+'\n')
                        else:
                            print(line)
                    except Exception as e:
                        print(e)
