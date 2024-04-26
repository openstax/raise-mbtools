import argparse
from pathlib import Path
from mbtools.models import MoodleBackup, MoodleLesson, MoodlePage, MoodleQuiz
import csv


def parse_toc(mbz_path, base_url):
    activity_list = []

    moodle_backup = MoodleBackup(mbz_path)

    for section in moodle_backup.sections():
        for act in moodle_backup.activities(section.id):
            if isinstance(act, MoodlePage):
                page_dict = {}
                page_dict['section'] = section.title
                page_dict['activity_name'] = act.name
                page_dict['lesson_page'] = ""
                page_dict['visible'] = act.is_visible()
                page_dict['url'] = f"{base_url}/mod/page/view.php?id={act.module_id}"

                activity_list.append(page_dict)
            elif isinstance(act, MoodleLesson):
                id2page = {}
                current_page = None
                for page in act.lesson_pages():
                    id2page[page.id] = page
                    if (page.prev == "0"):
                        current_page = page
                while (True):
                    lesson_dict = {}
                    lesson_dict['section'] = section.title
                    lesson_dict['activity_name'] = act.name
                    lesson_dict['lesson_page'] = current_page.name
                    lesson_dict['visible'] = act.is_visible()

                    if current_page.prev == "0":
                        # First page of a lesson doesn't need pageid
                        lesson_dict['url'] = f"{base_url}/mod/lesson/view.php?id={act.module_id}"
                    else:
                        lesson_dict['url'] = f"{base_url}/mod/lesson/view.php?id={act.module_id}&pageid={current_page.id}"

                    activity_list.append(lesson_dict)

                    if (current_page.next == "0"):
                        break
                    else:
                        current_page = id2page[current_page.next]
            elif isinstance(act, MoodleQuiz):
                quiz_dict = {}
                quiz_dict['section'] = section.title
                quiz_dict['activity_name'] = act.name
                quiz_dict['lesson_page'] = ""
                quiz_dict['url'] = f"{base_url}/mod/quiz/view.php?id={act.module_id}"
                quiz_dict['visible'] = "1"

                activity_list.append(quiz_dict)
    return activity_list


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
    parser.add_argument('base_url', type=str,
                        help='Base URL for Moodle')
    parser.add_argument('mbz_path', type=str,
                        help='relative path to the mbz directory')
    parser.add_argument('output_path', type=str,
                        help='Path/name of the output file to be generated')

    args = parser.parse_args()
    mbz_path = Path(args.mbz_path).resolve(strict=True)
    output_path = args.output_path

    activity_list = parse_toc(mbz_path, args.base_url)

    create_toc_csv(output_path, activity_list)


if __name__ == "__main__":  # pragma: no cover
    main()
