from pathlib import Path
from . import models


def write_etree(file_path, etree):
    with open(file_path, "wb") as f:
        etree.write(f, encoding="utf-8",
                    pretty_print=True,
                    xml_declaration=True)


def parse_moodle_backup(mbz_dir):
    """
    Given a string with a path to an extracted moodle backup directory,
    return a moodle backup object
    """
    mbz_path = Path(mbz_dir).resolve(strict=True)
    return models.MoodleBackup(mbz_path)


def parse_backup_activities(mbz_path):
    """
    Given a string with path to an extracted moodle backup directory return
    model objects for course activities
    """
    moodle_backup = parse_moodle_backup(mbz_path)
    return moodle_backup.activities()


def parse_backup_quizzes(mbz_path):
    """
    Given a string with path to an extracted moodle backup directory return
    model objects for course quizzes
    """
    moodle_backup = parse_moodle_backup(mbz_path)
    return moodle_backup.quizzes()


def parse_backup_elements(mbz_dir):
    """
    Given a string with path to an extracted moodle backup directory return
    model objects for course html elements
    """
    html_elements = []
    activities = parse_backup_activities(mbz_dir)
    for activity in activities:
        html_elements.extend(activity.html_elements())
    return html_elements


def parse_question_bank_for_html(mbz_dir, ids=None):
    """
    Given a string with path to a question_bank directory from an extracted
    moodle backup, return model for a question bank
    """

    mbz_path = Path(mbz_dir).resolve(strict=True)
    questions = models.MoodleQuestionBank(mbz_path).questions(ids)
    html = []
    for question in questions:
        for item in question.html_elements():
            html.append(item)
    return html


def find_references_containing(content_etree, src_content):
    """
    Given a etree object and a prefix for a resource, this function will
    return the src values from the etree that contain the src_content prefix
    """
    matching_elems = find_elements_containing(content_etree, src_content)
    return [el.get("src") for el in matching_elems]


def find_elements_containing(content_etree, src_content):
    """
    Given a etree object and a prefix for a resource, this function will
    return the elementss from the etree that contain the src_content prefix
    """
    return content_etree.xpath(
        f'//*[contains(@src, "{src_content}")]'
    )


def replace_src_values_tree(content_tree, src_content, swap_mapping):
    """
    Given an etree object, a prefix, and a mapping from links with that
    prefix to new links, swap all src values according to the mapping.
    """
    num_changes = 0
    for elem in find_elements_containing(content_tree, src_content):
        im_filename = elem.attrib["src"]
        if im_filename in swap_mapping.keys():
            num_changes += 1
            elem.attrib["src"] = swap_mapping[im_filename]
    return num_changes
