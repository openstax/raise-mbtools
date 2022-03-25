from pathlib import Path
from . import models


def parse_backup_activities(mbz_dir):
    """
    Given a string with path to an extracted moodle backup directory return
    model objects for course activities
    """
    mbz_path = Path(mbz_dir).resolve(strict=True)
    moodle_backup = models.MoodleBackup(mbz_path)
    return moodle_backup.activities()


def parse_backup_for_moodle_html_elements(mbz_dir):
    activities = parse_backup_activities(mbz_dir)
    moodle_html_elements = []
    for activitiy in activities:
        moodle_html_elements.extend(activitiy.html_elements())
    return moodle_html_elements


def parse_question_bank_for_html(mbz_dir):
    """
    Given a string with path to a question_bank directory from an extracted
    moodle backup, return model for a question bank
    """

    mbz_path = Path(mbz_dir).resolve(strict=True)
    question_objects = models.MoodleQuestionBank(mbz_path).questions()
    html = []
    for question in question_objects:
        for item in question.get_all_lxml_elements():
            html.append(item.text)
    return html


def parse_question_bank_for_moodle_html_elements(mbz_dir):
    """
    Given a string with path to a question_bank directory from an extracted
    moodle backup, return model for a question bank
    """

    mbz_path = Path(mbz_dir).resolve(strict=True)
    question_objects = models.MoodleQuestionBank(mbz_path).questions()
    elements = []
    for question in question_objects:
        for item in question.get_all_moodle_elements():
            elements.append(item)
    return elements


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
        for item in question.get_all_lxml_elements():
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
