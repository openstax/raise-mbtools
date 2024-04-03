import argparse
from pathlib import Path
from mbtools import utils
from bs4 import BeautifulSoup
import re
import os
import json

CLASSES_TO_INJECT = ["os-raise-ib-pset"]


def get_lesson_pages(toc_path):
    filename_set = set()
    with open(toc_path, 'r') as file:
        toc_content = file.read()
        practice_links = re.findall(r'\[(.*?)\]\((.*?)\)', toc_content)
        for title, link in practice_links:
            if "practice" in title.lower():
                filename_set.add(os.path.basename(link))
    return filename_set


def patch_pset(html_dir, practice_lesson_set):
    for path in Path(html_dir).rglob('*.html'):
        should_write = False

        with open(path, 'r') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            for elem in soup.find_all(name="div", class_="os-raise-ib-pset"):

                if os.path.basename(path) in practice_lesson_set:
                    should_write = True
                    elem['data-retry-limit'] = '2'
                    set_pset_problem(elem)
                else:
                    should_write = True
                    elem['data-retry-limit'] = '0'
        if should_write:
            utils.write_html_soup(path, soup)


def set_pset_problem(elem):
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
        "toc_path", type=str,
        help="path to toc"
    )
    args = parser.parse_args()
    html_directory = Path(args.html_directory).resolve(strict=True)
    toc_path = args.toc_path
    practice_lesson_set = get_lesson_pages(toc_path)
    patch_pset(html_directory, practice_lesson_set)


if __name__ == "__main__":  # pragma: no cover
    main()
