from pathlib import Path
from . import models


def parse_backup_activities(mbz_dir):
    """Given a string with path to an extracted moodle backup directory return
    model objects for course activities
    """
    mbz_path = Path(mbz_dir).resolve(strict=True)
    moodle_backup = models.MoodleBackup(mbz_path)
    return moodle_backup.activities()


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
