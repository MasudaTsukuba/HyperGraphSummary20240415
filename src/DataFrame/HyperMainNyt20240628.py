
from Hyper000Common20240621 import process_all


def main():
    # execute this command first
    # split -l 100000 nyt_all.csv part_
    prefix_string = '8897.NYT'
    root_path = f'/media/masuda/HDS2-UT/QuetsalData20240401/csv/{prefix_string}/'
    process_all(root_path, prefix_string)


if __name__ == '__main__':
    main()
