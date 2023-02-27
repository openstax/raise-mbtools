import argparse
from pathlib import Path
from bs4 import BeautifulSoup
import csv

CLASSES_TO_INJECT = ["os-raise-ib-input", "os-raise-ib-pset-problem"]


def inject_ib_uuids(html_dir, output_path):
    ib_input_instances_dict = []
    ib_pset_problems_dict = []
    for path in Path(html_dir).rglob("*.html"):

        with open(path, "r") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            for tag in CLASSES_TO_INJECT:
                for elem in soup.find_all(class_=tag):
                    if tag == "os-raise-ib-input":
                        ib_input_instances_dict.append(
                            {
                                "id": elem["data-content-id"],
                                "content_id": path.as_posix()[
                                    path.as_posix().find("html/")
                                    + 5: path.as_posix().find("html/")
                                    + 36
                                ],
                                "variant": Path(path).stem,
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
                        ib_pset_problems_dict.append(
                            {
                                "id": elem["data-content-id"],
                                "content_id": path.as_posix()[
                                    path.as_posix().find("html/")
                                    + 5: path.as_posix().find("html/")
                                    + 36
                                ],
                                "variant": Path(path).stem,
                                "content": elem.find(
                                    name="div",
                                    class_="os-raise-ib-pset-problem-content",
                                ),
                                "pset_id": elem.parent["data-content-id"],
                                "problem_type": elem["data-problem-type"],
                                "solution": elem["data-solution"],
                                "solution_options":
                                elem["data-solution-options"]
                                if elem["data-problem-type"] != "input"
                                else "",
                            }
                        )

    with open(f"{output_path}/ib_input_instances.csv", "w") as myFile:
        writer = csv.writer(myFile)
        writer.writerow(["id", "content_id", "variant", "content", "prompt"])
        for dictionary in ib_input_instances_dict:
            writer.writerow(dictionary.values())

    with open(f"{output_path}/ib_pset_problems.csv", "w") as myFile:
        writer = csv.writer(myFile)
        writer.writerow(
            [
                "id",
                "content_id",
                "variant",
                "content",
                "pset_id",
                "problem_type",
                "solution",
                "solution_options",
            ]
        )
        for dictionary in ib_pset_problems_dict:
            writer.writerow(dictionary.values())


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

    inject_ib_uuids(html_directory, output_directory)


if __name__ == "__main__":  # pragma: no cover
    main()
