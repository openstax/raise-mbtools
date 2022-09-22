from bs4 import BeautifulSoup
import argparse
from pathlib import Path


def fix_html(html_directory):

    tag_allow_list = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span']
    soup = None
    for html_file in Path(html_directory).iterdir():
        with open(f"{html_directory}/{html_file.name}") as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            for link in soup.find_all(tag_allow_list):
                if len(link.get_text(strip=True)) == 0:
                    link.extract()

        with open(f"{html_directory}/{html_file.name}", 'w') as f:
            f.write(str(soup))


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
