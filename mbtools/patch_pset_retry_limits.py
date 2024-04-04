import argparse
from pathlib import Path
from mbtools import utils
from bs4 import BeautifulSoup
from mbtools.generate_mbz_toc import parse_toc
import os
import json


def get_lesson_practice_pages(mbz_path):
    (md_string, activity_list) = parse_toc(mbz_path)
    filename_set = set()

    for activity in activity_list:
        if 'practice' in activity['lesson_page'].lower():
            filename_set.add(activity['content_id'])
    return filename_set


def patch_pset(html_dir, practice_lesson_set):
    for path in Path(html_dir).glob('*.html'):
        should_write = False

        with open(path, 'r') as f:
            filename = os.path.basename(path)
            file_uuid = os.path.splitext(filename)[0]
            soup = BeautifulSoup(f.read(), 'html.parser')
            for elem in soup.find_all(name="div", class_="os-raise-ib-pset"):

                if file_uuid in practice_lesson_set:
                    should_write = True
                    elem['data-retry-limit'] = '2'
                    set_pset_problems(elem)
                else:
                    should_write = True
                    elem['data-retry-limit'] = '0'
        if should_write:
            utils.write_html_soup(path, soup)


def set_pset_problems(elem):
    for problem_elem in elem.find_all(name="div",
                                      class_="os-raise-ib-pset-problem"):
        problem_type = problem_elem.get('data-problem-type')
        if problem_type in ["multiplechoice", "dropdown"]:
            solution_options = problem_elem.get('data-solution-options')
            if solution_options:
                num_options = len(json.loads(solution_options))
                problem_elem['data-retry-limit'] = str(num_options - 1)


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "html_directory", type=str,
        help="relative path to HTML files")
    parser.add_argument(
        "mbz_path", type=str,
        help="path to mbz"
    )
    args = parser.parse_args()
    html_directory = Path(args.html_directory).resolve(strict=True)
    mbz_path = Path(args.mbz_path).resolve(strict=True)
    practice_lesson_set = get_lesson_practice_pages(mbz_path)
    patch_pset(html_directory, practice_lesson_set)


if __name__ == "__main__":  # pragma: no cover
    main()
