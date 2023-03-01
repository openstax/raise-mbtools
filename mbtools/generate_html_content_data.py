import argparse
from pathlib import Path
from bs4 import BeautifulSoup
import csv
from mbtools import utils

CLASSES_TO_COLLECT = ["os-raise-ib-input", "os-raise-ib-pset-problem"]


def generate_html_content_data(html_dir, output_path):
    ib_input_instances_list = []
    ib_pset_problems_list = []
    for path in Path(html_dir).rglob("*.html"):

        with open(path, "r") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            for tag in CLASSES_TO_COLLECT:
                for elem in soup.find_all(class_=tag):
                    (content_id, variant) = parse_content_id_and_variant(path)
                    if tag == "os-raise-ib-input":
                        ib_input_instances_list.append(
                            {
                                "id": elem["data-content-id"],
                                "content_id": content_id,
                                "variant": variant,
                                "content": elem.find(
                                    name="div",
                                    class_="os-raise-ib-input-content"
                                ),
                                "prompt": elem.find(
                                    name="div",
                                    class_="os-raise-ib-input-prompt"
                                ),
                            }
                        )
                    if tag == "os-raise-ib-pset-problem":
                        ib_pset_problems_list.append(
                            {
                                "id": elem["data-content-id"],
                                "content_id": content_id,
                                "variant": variant,
                                "content": elem.find(
                                    name="div",
                                    class_="os-raise-ib-pset-problem-content",
                                ),
                                "pset_id": elem.parent["data-content-id"],
                                "problem_type": elem["data-problem-type"],
                                "solution": elem["data-solution"],
                                "solution_options": elem.get(
                                    "data-solution-options", ""
                                    )
                            }
                        )

    with open(f"{output_path}/ib_input_instances.csv", "w") as input_outfile,\
         open(f"{output_path}/ib_pset_problems.csv", "w") as pset_outfile:
        input_instance_headers = ib_input_instances_list[0].keys()
        input_result = csv.DictWriter(
            input_outfile,
            fieldnames=input_instance_headers)
        input_result.writeheader()
        input_result.writerows(ib_input_instances_list)

        pset_headers = ib_pset_problems_list[0].keys()
        pset_result = csv.DictWriter(pset_outfile, fieldnames=pset_headers)
        pset_result.writeheader()
        pset_result.writerows(ib_pset_problems_list)


def parse_content_id_and_variant(html_path):
    uuid_or_variant = f"{Path(html_path.name).stem}"
    if utils.validate_uuid4(uuid_or_variant):
        return (uuid_or_variant, "main")
    else:
        content_id = html_path.parent.stem
        return (content_id, uuid_or_variant)


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("html_directory", type=str,
                        help="relative path to HTML files")

    parser.add_argument(
        "output_directory", type=str, help="relative path to output directory"
    )

    args = parser.parse_args()
    html_directory = Path(args.html_directory).resolve(strict=True)
    output_directory = Path(args.output_directory).resolve(strict=True)

    generate_html_content_data(html_directory, output_directory)


if __name__ == "__main__":  # pragma: no cover
    main()
