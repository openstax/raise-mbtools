import argparse
from pathlib import Path
from mbtools import utils
from uuid import uuid4
from bs4 import BeautifulSoup


CLASSES_TO_INJECT = [
    "os-raise-ib-input",
    "os-raise-ib-pset",
    "os-raise-ib-pset-problem"]


def inject_ib_uuids(html_dir):
    for path in Path(html_dir).rglob('*.html'):
        with open(path, 'r') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            for tag in CLASSES_TO_INJECT:
                for elem in soup.find_all(name="div", class_=tag):
                    if elem.get('data-content-id') is None:
                        elem['data-content-id'] = uuid4()

            utils.write_html_soup(path, soup)


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "html_directory", type=str,
        help="relative path to HTML files")

    args = parser.parse_args()
    html_directory = Path(args.html_directory).resolve(strict=True)
    inject_ib_uuids(html_directory)


if __name__ == "__main__":  # pragma: no cover
    main()
