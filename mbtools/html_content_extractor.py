from mbtools import utils
from pathlib import Path
import argparse


def __init__(self, mbz_path):
    self.mbz_path = Path(mbz_path)


def replace_content_tags(mbz_path, output_file_path):
    activities = utils.parse_backup_activities(mbz_path)
    output_html_files = {}
    for act in activities:
        for html_elem in act.html_elements():

            output_html_files.update(html_elem.replace_content_tag())
            with open(act.activity_filename, "wb") as f:
                act.etree.write(f, encoding="utf-8",
                                pretty_print=True,
                                xml_declaration=True)

    write_html_files(output_html_files, output_file_path)
    return output_html_files


def write_html_files(output_html_files, output_file_path):
    for file_name, file_content in output_html_files.items():
        with open(f"{output_file_path}/{file_name}.html", "w") as file:
            file.write(file_content)


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('mbz_path', type=str,
                        help='relative path to unzipped mbz')
    parser.add_argument('output_directory', type=str,
                        help='Path to where html files will be output')
    args = parser.parse_args()
    mbz_path = Path(args.mbz_path).resolve(strict=True)
    output_directory = Path(args.output_directory)
    replace_content_tags(mbz_path, output_directory)


if __name__ == "__main__":
    main()
