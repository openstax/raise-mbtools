from mbtools import utils
from pathlib import Path
import argparse

from mbtools.models import MoodleLesson, MoodlePage


def __init__(self, mbz_path):
    self.mbz_path = Path(mbz_path)


def replace_content_tags(mbz_path, output_file_path,
                         filter=["page", "lesson"]):

    activities = utils.parse_backup_activities(mbz_path)
    output_html_files = {}

    for act in activities:
        if isinstance(act, MoodleLesson) and "lesson" in filter \
                or isinstance(act, MoodlePage) and "page" in filter:
            for html_elem in act.html_elements():
                html_file = html_elem.replace_content_tag()
                if html_file:
                    output_html_files.update(html_file)
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

    parser.add_argument("-filter", nargs="+", default=["lesson", "page"],
                        choices=['lesson', 'page'],
                        help="Add optional filters 'page' and/or 'lesson'")

    args = parser.parse_args()
    mbz_path = Path(args.mbz_path).resolve(strict=True)
    filter = args.filter
    output_directory = Path(args.output_directory).resolve(strict=True)
    return replace_content_tags(mbz_path, output_directory, filter)


if __name__ == "__main__":
    main()
