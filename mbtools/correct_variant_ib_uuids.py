import argparse
from pathlib import Path
from bs4 import BeautifulSoup
from uuid import uuid4
from mbtools import utils

CLASSES_TO_INJECT = [
    "os-raise-ib-input",
    "os-raise-ib-pset",
    "os-raise-ib-pset-problem"
]


def correct_uuids(html_directory):
    existing_uuids = set()

    for html_file in Path(html_directory).glob('*.html'):
        with open(html_file, 'r') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            for tag in CLASSES_TO_INJECT:
                for elem in soup.find_all(name="div", class_=tag):
                    if elem.get('data-content-id'):
                        existing_uuids.add(elem.get('data-content-id'))

    for child in Path(html_directory).iterdir():
        if child.is_dir():
            # child is a variant directory

            for html_file in child.glob('*.html'):
                should_write = False
                with open(html_file, 'r') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
                    for tag in CLASSES_TO_INJECT:
                        for elem in soup.find_all(name="div", class_=tag):
                            if elem.get('data-content-id') in existing_uuids:
                                should_write = True
                                elem['data-content-id'] = uuid4()

                if should_write:
                    utils.write_html_soup(html_file, soup)


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "html_directory", type=str,
        help="relative path to HTML files")

    args = parser.parse_args()
    html_directory = Path(args.html_directory).resolve(strict=True)
    correct_uuids(html_directory)


if __name__ == "__main__":  # pragma: no cover
    main()
