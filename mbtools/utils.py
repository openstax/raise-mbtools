from pathlib import Path
from . import models

CONTENT_PREFIX = "https://k12.openstax.org/contents/raise/"


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
    moodle_backup = models.MoodleBackup(mbz_path)
    return moodle_backup.activities()


def parse_backup_quizzes(mbz_dir):
    """
    Given a string with path to an extracted moodle backup directory return
    model objects for course quizzes
    """
    mbz_path = Path(mbz_dir).resolve(strict=True)
    moodle_backup = models.MoodleBackup(mbz_path)
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
    matching_elems = content_etree.xpath(
        f'//*[contains(@src, "{src_content}")]'
    )
    return [el.get("src") for el in matching_elems]


def get_resources_from_elem(elem, prefix=None):
    """
    Given a MoodleHtmlElement, this returns a list of strings that are the
    references used by the HTML in the element. If a prefix is provided, it
    will only return those references that contain the prefix
    """

    values = elem.get_attribute_values('src')
    values.extend(elem.get_attribute_values('href'))
    im_resources = []
    for val in values:
        if prefix is None or prefix in val:
            im_resources.append(val)

    return im_resources


def collect_resources_from_mbz(mbz_path, prefix=None):
    """
    Given a path to an opened mbz file, this function will return all of the
    references to external sources referenced by the HTML within that mbz. If a
    prefix is provided, it will return the references that contain that
    prefix
    """
    elems = []
    elems.extend(parse_backup_elements(mbz_path))
    resource_urls = []
    for elem in elems:
        resource_urls.extend(get_resources_from_elem(elem, prefix))
    return resource_urls


def replace_attribute_values_tree(content_tree, attrs, swap_mapping):
    swaps = {}
    for attr in attrs:
        for elem in content_tree.xpath(f'//*[@{attr}]'):
            im_filename = elem.attrib[attr]
            if im_filename in swap_mapping.keys():
                elem.attrib[attr] = swap_mapping[im_filename]
                swaps[im_filename] = swap_mapping[im_filename]
    return swaps
