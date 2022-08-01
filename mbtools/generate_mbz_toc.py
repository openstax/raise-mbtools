import argparse
from pathlib import Path
from mbtools.models import MoodleBackup, MoodleLesson, MoodlePage


def make_link(name, uuid):
    return f'[{name}](./html/{uuid}.html)'


def make_nested_bullet(level, content):
    return f"{' '*(level-1)*4}* {content}\n"


def make_title():
    return "# Table of Contents  \n"


def create_toc(mbz_path, md_filepath):
    moodle_backup = MoodleBackup(mbz_path)
    with open(md_filepath, 'w') as f:
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


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('mbz_path', type=str,
                        help='relative path to the mbz directory')
    parser.add_argument('md_filepath', type=str,
                        help='Path/name of the markdown file to be generated')
    args = parser.parse_args()
    mbz_path = Path(args.mbz_path).resolve(strict=True)
    md_filepath = args.md_filepath

    create_toc(mbz_path, md_filepath)


if __name__ == "__main__":  # pragma: no cover
    main()
