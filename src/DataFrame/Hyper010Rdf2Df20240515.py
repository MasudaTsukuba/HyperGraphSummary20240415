"""
Hyper010Rdf2Df20240515.py
2024/5/15, T. Masuda
Amagasa Laboratory, University of Tsukuba
"""
import os
from Hyper000Common20240621 import read_prefix, write_prefix


def process_triples_in_batches(data_path_, csv_file_path_, batch_size=10000):
    def write_csv_batch(csv_file_, triple_buffer_):
        for triple_parts_ in triple_buffer_:
            csv_file_.write(','.join(triple_parts_) + '\n')

    with open(csv_file_path_, 'w') as csv_file:
        csv_file.write("subject,predicate,object\n")
        files = os.listdir(data_path_)
        for file_ in files:
            if file_.endswith('.nt'):
                with open(f'{data_path_}/{file_}', 'r') as n3_file:
                    triple_buffer = []
                    for line in n3_file:
                        triple_parts = line.strip().split()
                        if len(triple_parts) == 4:
                            triple_buffer.append(triple_parts[0:3])
                            if len(triple_buffer) >= batch_size:
                                write_csv_batch(csv_file, triple_buffer)
                                triple_buffer = []
                    if triple_buffer:
                        write_csv_batch(csv_file, triple_buffer)


def main(data_path, csv_file_path):
    print('Hyper010Rdf2Df20240515.py.')
    process_triples_in_batches(data_path, csv_file_path, batch_size=10000)
    pass


if __name__ == '__main__':
    # data_path = '/media/masuda/HDS2-UT/QuetsalData20240401/8898.SWDFood'
    data_path = '/media/masuda/HDS2-UT/QuetsalData20240401/8893.GeoNames'
    prefix = data_path.split('/')[-1]
    csv_file_path = f'../../data/{prefix}_010_all_triples.csv'
    write_prefix(prefix)
    main(data_path, csv_file_path)
