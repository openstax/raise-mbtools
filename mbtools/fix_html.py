from bs4 import BeautifulSoup
import argparse
from pathlib import Path
from mbtools import utils


def fix_html(html_directory):
    inline_tags = ['span']
    block_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    soup = None

    for html_file in Path(html_directory).rglob('*.html'):
        with open(html_file) as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            for tags in [inline_tags, block_tags]:
                for elem in soup.find_all(tags):
                    if len(elem.get_text(strip=True)) == 0\
                         and len(elem.find_all()) == 0:
                        elem.extract()

        utils.write_html_soup(html_file, soup)


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "html_directory", type=str,
        help="relative path to HTML files")

    args = parser.parse_args()
    html_directory = Path(args.html_directory).resolve(strict=True)
    fix_html(html_directory)


if __name__ == "__main__":  # pragma: no cover
    main()
