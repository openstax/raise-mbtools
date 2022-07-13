import argparse
from pathlib import Path
from mbtools.models import MoodleLesson, MoodlePage
from mbtools.utils import parse_backup_activities


def make_link(uuid):
    return "./html/" + uuid + ".html"


def make_bullet(name, uuid):
    return f'* [{name}]({make_link(uuid)})\n'


def make_subheader(title):
    return f'## {title}  \n'


def create_toc(mbz_path, md_filepath):
    activities = parse_backup_activities(mbz_path)
    with open(md_filepath, 'w') as f:
        f.write("# Table of Contents  \n")
        for act in activities:
            if isinstance(act, MoodlePage):
                f.write(make_subheader(act.name()))
                for html_elem in act.html_elements():
                    uuid = html_elem.get_attribute_values("data-content-id")[0]
                    f.write(make_bullet(act.name(), uuid))
            elif isinstance(act, MoodleLesson):
                f.write(make_subheader(act.name()))
                for page in act.lesson_pages():
                    html_elem = page.html_element()
                    uuid = html_elem.get_attribute_values("data-content-id")[0]
                    f.write(make_bullet(page.name(), uuid))


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
