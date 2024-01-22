from argparse import ArgumentParser
from argparse import Namespace
from be.osm import download_prague_poi_data
from be.osm import download_prague_address_data
from be.osm import download_prague_road_data
from be.neo import load_prague_poi
from be.neo import load_prague_address_nodes
from be.neo import load_prague_road_nodes
from be.neo import load_prague_road_rels
from be.neo import create_prague_road_indexes
from be.neo import create_prague_address_road_rels
from be.neo import create_prague_poi_address_fulltext_index
from be.neo import neo_clean_db


def main():
    parser = ArgumentParser(
        prog='cli',
        description='execute commands'
    )
    subparsers = parser.add_subparsers(title='commands')

    parser_download = subparsers.add_parser('download')
    parser_download.set_defaults(func=download_data)

    parser_db = subparsers.add_parser('db')
    subparsers_db = parser_db.add_subparsers(title='db commands')

    parser_db_load = subparsers_db.add_parser('load')
    parser_db_load.add_argument('dataset', choices=['poi', 'road', 'address'])
    parser_db_load.set_defaults(func=load_data)

    parser_db_load = subparsers_db.add_parser('clean')
    parser_db_load.set_defaults(func=clean_db)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args=args)


def clean_db(*args, **kwargs) -> None:
    neo_clean_db()


def load_data(args: Namespace, **kwargs) -> None:
    if args.dataset == 'poi':
        print('Loading Prague POIs')
        load_prague_poi()
    if args.dataset == 'address':
        print('Loading Prague addresses')
        load_prague_address_nodes()
        create_prague_address_road_rels()
        create_prague_poi_address_fulltext_index()
    if args.dataset == 'road':
        print('Loading Prague roads')
        create_prague_road_indexes()
        load_prague_road_nodes()
        load_prague_road_rels()


def download_data(*args, **kwargs) -> None:
    print('Downloading Prague POIs')
    download_prague_poi_data()
    print('Downloading Prague addresses')
    download_prague_address_data()
    print('Downloading Prague roads')
    download_prague_road_data()


if __name__ == "__main__":
    main()