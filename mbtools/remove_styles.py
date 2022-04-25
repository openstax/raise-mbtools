from pathlib import Path
from . import models
from lxml.etree import tostring
import argparse


def remove_styles(mbz_dir):
    mbz_path = Path(mbz_dir).resolve(strict=True)
    moodle_backup = models.MoodleBackup(mbz_path)
    activities = moodle_backup.activities()
    for activity in activities:
        for elem in activity.html_elements():
            elem.remove_attr("style")
        with open(activity.activity_filename, "w") as f:
            f.write(tostring(activity.etree,
                             pretty_print=True,
                             encoding='utf8').decode())

    question_bank = models.MoodleQuestionBank(mbz_path)
    questions = question_bank.questions()
    for question in questions:
        for elem in question.html_elements():
            elem.remove_attr("style")
        with open(question_bank.questionbank_path, 'w') as f:
            f.write(tostring(question_bank.etree,
                             pretty_print=True,
                             encoding='utf8').decode())


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('mbz_path', type=str,
                        help='relative path to unzipped mbz')
    args = parser.parse_args()
    mbz_path = Path(args.mbz_path).resolve(strict=True)
    remove_styles(mbz_path)


if __name__ == "__main__":
    main()
