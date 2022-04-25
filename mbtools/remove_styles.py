from pathlib import Path
from . import models
from lxml.etree import tostring


def remove_styles(mbz_dir, attrs):
    mbz_path = Path(mbz_dir).resolve(strict=True)
    moodle_backup = models.MoodleBackup(mbz_path)
    activities = moodle_backup.activities()
    for activity in activities:
        for elem in activity.html_elements():
            elem.remove_attr("style", attrs)
        with open(activity.activity_filename, "w") as f:
            f.write(tostring(activity.etree,
                             pretty_print=True,
                             encoding='utf8').decode())
