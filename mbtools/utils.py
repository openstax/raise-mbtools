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


def parse_backup_activities(mbz_dir):
    """
    Given a string with path to an extracted moodle backup directory return
    model objects for course activities
    """
    mbz_path = Path(mbz_dir).resolve(strict=True)
    moodle_backup = parse_moodle_backup(mbz_path)
    return moodle_backup.activities()


def parse_backup_quizzes(mbz_dir):
    """
    Given a string with path to an extracted moodle backup directory return
    model objects for course quizzes
    """
    mbz_path = Path(mbz_dir).resolve(strict=True)
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


def find_references_containing(content_etree, src_content=None):
    """
    Given a etree object and a prefix for a resource, this function will
    return the src values from the etree that contain the src_content prefix
    """
    matching_elems = []
    if src_content is None:
        matching_elems = content_etree.xpath(
            '//*[@src]'
        )
    else:
        matching_elems = content_etree.xpath(
            f'//*[contains(@src, "{src_content}")]'
        )
    return [el.get("src") for el in matching_elems]


def replace_attribute_values_tree(content_tree, attrs, swap_mapping):
    swaps = {}
    for attr in attrs:
        for elem in content_tree.xpath(f'//*[@{attr}]'):
            im_filename = elem.attrib[attr]
            if im_filename in swap_mapping.keys():
                elem.attrib[attr] = swap_mapping[im_filename]
                swaps[im_filename] = swap_mapping[im_filename]
    return swaps
