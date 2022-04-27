from pathlib import Path
from . import models
from mbtools.utils import write_etree
import argparse


def remove_styles(mbz_dir):
    mbz_path = Path(mbz_dir).resolve(strict=True)
    moodle_backup = models.MoodleBackup(mbz_path)
    activities = moodle_backup.activities()
    for activity in activities:
        for elem in activity.html_elements():
            elem.remove_attr("style")
        write_etree(activity.activity_filename, activity.etree)


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('mbz_path', type=str,
                        help='relative path to unzipped mbz')
    args = parser.parse_args()
    mbz_path = Path(args.mbz_path).resolve(strict=True)
    remove_styles(mbz_path)


if __name__ == "__main__":
    main()
