from pathlib import Path
import models


def parse_backup_activities(mbz_dir):
    """
    Given a string with path to an extracted moodle backup directory return
    model objects for course activities
    """
    mbz_path = Path(mbz_dir).resolve(strict=True)
    moodle_backup = models.MoodleBackup(mbz_path)
    return moodle_backup.activities()


def parse_question_bank_for_html(mbz_dir):
    """
    Given a string with path to a question_bank directory from an extracted
    moodle backup, return model for a question bank
    """

    mbz_path = Path(mbz_dir).resolve(strict=True)
    question_objects = models.MoodleQuestionBank(mbz_path).questions()
    html = []
    for question in question_objects:
        for item in question.get_all_html_elements():
            html.append(item.text)
    return html


def parse_question_bank_for_ids(mbz_dir, ids):
    """
    Given a string with a path to a question_bank directory from an
    extracted modle backup and a list of question ids, extract the question
    objects with the associated ids from the question bank
    """
    mbz_path = Path(mbz_dir).resolve(strict=True)
    question_objects = models.MoodleQuestionBank(mbz_path).questions_by_id(ids)
    html = []
    for question in question_objects:
        for item in question.get_all_html_elements():
            html.append(item.text)
    return html


def find_external_media_references(activity):
    """Given an activity find external media file references"""
    media_references = []

    for html_elem in activity.html_elements():
        media_references += html_elem.find_references_containing(
            "amazonaws.com"
        )

    return media_references


def find_moodle_media_references(activity):
    """Given an activity find moodle media file references"""
    media_references = []

    for html_elem in activity.html_elements():
        media_references += html_elem.find_references_containing(
            "@@PLUGINFILE@@"
        )

    return media_references


def main():
    activities = parse_backup_activities("../.vscode/wisewire-raise-thin-slice-patch1-20220207")
    media_references = []
    for activity in activities:
        media_references += find_external_media_references(activity)

    print(media_references)

if __name__ == "__main__":
    main()
