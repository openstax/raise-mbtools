import argparse
from pathlib import Path
from mbtools.models import MoodleBackup, MoodleLesson, MoodlePage
import csv


def make_link(name, uuid):
    return f'[{name}](./html/{uuid}.html)'


def make_nested_bullet(level, content):
    return f"{' '*(level-1)*4}* {content}\n"


def make_title():
    return "# Table of Contents  \n"


def create_toc_md(mbz_path, md_filepath):
    moodle_backup = MoodleBackup(mbz_path)
    with open(f'{md_filepath}/toc.md', 'w') as f:
        f.write(make_title())
        for section in moodle_backup.sections():
            f.write(make_nested_bullet(1, section.title))
            for act in moodle_backup.activities(section.id):
                if isinstance(act, MoodlePage):
                    for html_elem in act.html_elements():
                        uuid = html_elem.get_attribute_values(
                            "data-content-id")[0]
                        f.write(make_nested_bullet(
                            2, make_link(act.name, uuid)))
                elif isinstance(act, MoodleLesson):
                    f.write(make_nested_bullet(2, act.name))
                    id2page = {}
                    current_page = None
                    for page in act.lesson_pages():
                        id2page[page.id] = page
                        if (page.prev == "0"):
                            current_page = page
                    while (True):
                        html_elem = current_page.html_element()
                        uuid = html_elem.get_attribute_values(
                            "data-content-id")[0]
                        f.write(make_nested_bullet(
                            3, make_link(current_page.name, uuid)))
                        if (current_page.next == "0"):
                            break
                        else:
                            current_page = id2page[current_page.next]


def create_toc_csv(mbz_path, csv_filepath):
    moodle_backup = MoodleBackup(mbz_path)
    activity_list = []
    for section in moodle_backup.sections():
        for act in moodle_backup.activities(section.id):
            if isinstance(act, MoodlePage):
                for html_elem in act.html_elements():
                    page_dict = {}
                    page_dict['section'] = section.title
                    page_dict['content_id'] = html_elem.get_attribute_values(
                        "data-content-id")[0]
                    page_dict['activity_name'] = act.name
                    page_dict['lesson_page'] = ""

                    activity_list.append(page_dict)
            elif isinstance(act, MoodleLesson):
                id2page = {}
                current_page = None
                for page in act.lesson_pages():
                    id2page[page.id] = page
                    if (page.prev == "0"):
                        current_page = page
                while (True):
                    html_elem = current_page.html_element()
                    lesson_dict = {}
                    lesson_dict['section'] = section.title
                    lesson_dict['content_id'] = html_elem.get_attribute_values(
                        "data-content-id")[0]
                    lesson_dict['activity_name'] = act.name
                    lesson_dict['lesson_page'] = current_page.name
                    activity_list.append(lesson_dict)
                    if (current_page.next == "0"):
                        break
                    else:
                        current_page = id2page[current_page.next]

    with open(f"{csv_filepath}/toc.csv", "w") as outfile:
        content_headers = activity_list[0].keys()
        result = csv.DictWriter(
            outfile,
            fieldnames=content_headers)
        result.writeheader()
        result.writerows(activity_list)


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('mbz_path', type=str,
                        help='relative path to the mbz directory')
    parser.add_argument('output_path', type=str,
                        help='Path/name of the markdown file to be generated')
    parser.add_argument('--csv', action='store_true',
                        help="Generate a TOC CSV file")

    args = parser.parse_args()
    mbz_path = Path(args.mbz_path).resolve(strict=True)
    output_path = args.output_path
    csv = args.csv
    create_toc_md(mbz_path, output_path)
    if csv:
        create_toc_csv(mbz_path, output_path)


if __name__ == "__main__":  # pragma: no cover
    main()
