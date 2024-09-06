from Hyper000Common20240621 import process_all


def main():
    # split -l 100000 geoname_all.csv
    prefix_string = '8893.GeoNames'
    root_path = f'/media/masuda/HDS2-UT/QuetsalData20240401/csv/{prefix_string}/'
    process_all(root_path, prefix_string)


if __name__ == '__main__':
    main()
