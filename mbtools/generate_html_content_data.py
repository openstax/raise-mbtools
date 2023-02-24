import argparse
from pathlib import Path
from mbtools import utils
from uuid import uuid4
from bs4 import BeautifulSoup
import csv


CLASSES_TO_INJECT = [
    "os-raise-ib-input",
    "os-raise-ib-pset-problem"]


def inject_ib_uuids(html_dir, output_path):
    ib_input_instances_dict = []
    ib_pset_problems_dict = []
    for path in Path(html_dir).rglob('*.html'):

        with open(path, 'r') as f:

            soup = BeautifulSoup(f.read(), 'html.parser')
            for tag in CLASSES_TO_INJECT:
                for elem in soup.find_all(class_=tag):
                    if tag == "os-raise-ib-input":
                        ib_input_instances_dict.append({
                            "content_id": elem["data-content-id"],
                            "variant": Path(path).stem,
                            "content": elem.find(name="div", class_="os-raise-ib-input-content"),
                            "prompt":elem.find(name="div", class_="os-raise-ib-input-prompt")
                        })
                    if tag == "os-raise-ib-pset-problem":
                        ib_pset_problems_dict.append({
                            "content_id": elem["data-content-id"],
                            "variant": Path(path).stem,
                            "content": elem.find(name="div", class_="os-raise-ib-input-content"),
                            "prompt":elem.find(name="div", class_="os-raise-ib-input-prompt"),
                            "pset_id": '',
                            "problem_type": elem["data-problem-type"],
                            "solution": elem["data-solution"],
                            "solution_options": elem["data-solution-options"] if  elem["data-problem-type"] != "input" else ''
                        })

    print(ib_pset_problems_dict[0])
    print(ib_input_instances_dict[0])

def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "html_directory", type=str,
        help="relative path to HTML files")

    parser.add_argument(
        "output_directory", type=str,
        help="relative path to output directory")

    args = parser.parse_args()
    html_directory = Path(args.html_directory).resolve(strict=True)
    output_directory = Path(args.output_directory).resolve(strict=True)

    inject_ib_uuids(html_directory, output_directory)


if __name__ == "__main__":  # pragma: no cover
    main()
