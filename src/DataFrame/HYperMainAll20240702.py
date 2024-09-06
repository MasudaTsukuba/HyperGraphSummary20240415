from HyperMainChebi20240624 import main as main_chebi
from HyperMainDbpedia20240624 import main as main_dbpedia
from HyperMainDrugBank20240628 import main as main_drugbank
from HyperMainGeonames20240621 import main as main_geonames
from HyperMainJamendo20240624 import main as main_jamendo
from HyperMainKegg20240621 import main as main_kegg
from HyperMainLmdb20240628 import main as main_lmdb
from HyperMainNyt20240628 import main as main_nyt
from HyperMainSwdf20240628 import main as main_swdf


def main():
    # main_chebi()
    # main_dbpedia()
    # main_drugbank()
    # main_geonames()
    # main_jamendo()
    main_kegg()
    main_lmdb()
    main_nyt()
    main_swdf()


if __name__ == '__main__':
    main()
