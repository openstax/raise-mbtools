from mbtools import utils
from pathlib import Path
import argparse


class ContentExtractor:
    """
    Given a string with path to an extracted moodle backup directory return
    model objects for course html elements
    """
    def __init__(self, mbz_path):
        self.mbz_path = Path(mbz_path)
        self.output_html_files = {}

    def replace_content_tags(self, output_file_path):
        activities = utils.parse_backup_activities(self.mbz_path)

        for act in activities:
            for html_elem in act.html_elements():

                self.output_html_files.update(html_elem.replace_content_tag())
                with open(act.activity_filename, "wb") as f:
                    act.etree.write(f, encoding="utf-8",pretty_print=True,
                                    doctype='<?xml version="1.0" encoding="UTF-8"?>')

        self.write_html_files(output_file_path)
        return self.output_html_files

    def write_html_files(self, output_file_path):
        for file_name, file_content in self.output_html_files.items():
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
    ContentExtractor(mbz_path).replace_tags(output_directory)


if __name__ == "__main__":
    main()
