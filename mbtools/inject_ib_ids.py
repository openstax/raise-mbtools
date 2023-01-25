import argparse
from pathlib import Path
from mbtools.models import MoodleHtmlElement
from lxml import etree

CLASSES_TO_INJECT = [
    "os-raise-ib-input",
    "os-raise-ib-pset",
    "os-raise-ib-pset-problem"]


def inject_ib_ids(html_dir):
    all_files = []
    for path in Path(html_dir).rglob('*.html'):
        all_files.append(path)

    for file_path in all_files:
        with open(file_path, 'r') as f:
            parent_string = '<content></content>'
            parent_element = etree.fromstring(parent_string)
            parent_element.text = f.read()
            content = MoodleHtmlElement(parent_element, str(file_path))

        content.add_ib_content_id(CLASSES_TO_INJECT)

        with open(file_path, 'w') as f:
            f.write(content.tostring())


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "html_directory", type=str,
        help="relative path to HTML files")

    args = parser.parse_args()
    html_directory = Path(args.html_directory).resolve(strict=True)
    inject_ib_ids(html_directory)


if __name__ == "__main__":  # pragma: no cover
    main()
