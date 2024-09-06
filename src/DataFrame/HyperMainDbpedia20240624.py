from Hyper000Common20240621 import process_all


def main():
    # create CSV files from NT files, 2024/9/2
    # src/utils/ConvertNt2CsvDbpedia20240902.py
    prefix_string = '8891.DBPedia-Subset'
    root_path = f'/media/masuda/HDS2-UT/QuetsalData20240401/csv/{prefix_string}/'
    process_all(root_path, prefix_string)


if __name__ == '__main__':
    main()
