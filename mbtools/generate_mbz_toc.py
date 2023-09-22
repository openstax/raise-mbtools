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


def parse_toc(mbz_path):
    md_string = ''
    activity_list = []

    moodle_backup = MoodleBackup(mbz_path)
    md_string += make_title()
    for section in moodle_backup.sections():
        md_string += make_nested_bullet(1, section.title)
        for act in moodle_backup.activities(section.id):
            if isinstance(act, MoodlePage):
                for html_elem in act.html_elements():
                    uuid = html_elem.get_attribute_values(
                        "data-content-id")[0]
                    md_string += make_nested_bullet(
                        2, make_link(act.name, uuid))
                    page_dict = {}
                    page_dict['section'] = section.title
                    page_dict['content_id'] = uuid
                    page_dict['activity_name'] = act.name
                    page_dict['lesson_page'] = ""
                    page_dict['visible'] = act.is_visible()
                    page_dict['lesson_page_type'] = 'content'

                activity_list.append(page_dict)
            elif isinstance(act, MoodleLesson):
                md_string += make_nested_bullet(2, act.name)
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
                    md_string += make_nested_bullet(
                        3, make_link(current_page.name, uuid))
                    lesson_dict = {}
                    lesson_dict['section'] = section.title
                    lesson_dict['content_id'] = uuid
                    lesson_dict['activity_name'] = act.name
                    lesson_dict['lesson_page'] = current_page.name
                    lesson_dict['visible'] = act.is_visible()
                    lesson_dict['lesson_page_type'] = current_page.page_type()
                    activity_list.append(lesson_dict)

                    if (current_page.next == "0"):
                        break
                    else:
                        current_page = id2page[current_page.next]
    return (md_string, activity_list)


def create_toc_md(output_path, parsed_toc):
    with open(output_path, 'w') as f:
        f.write(parsed_toc)


def create_toc_csv(output_path, activity_list):
    with open(output_path, "w") as outfile:
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
                        help='Path/name of the output file to be generated')
    parser.add_argument('--csv', action='store_true',
                        help="Generate a TOC CSV file")

    args = parser.parse_args()
    mbz_path = Path(args.mbz_path).resolve(strict=True)
    output_path = args.output_path
    csv = args.csv
    (md_string, activity_list) = parse_toc(mbz_path)
    if csv:
        create_toc_csv(output_path, activity_list)
    else:
        create_toc_md(output_path, md_string)


if __name__ == "__main__":  # pragma: no cover
    main()
