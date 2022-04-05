import argparse
from pathlib import Path
from . import utils

STYLE_VIOLATION = "ERROR: Uses In-Line Styles"
SOURCE_VIOLATION = "ERROR: Uses External Resource with Invalid Prefix"
MOODLE_VIOLATION = "ERROR: References Uploaded Files in Moodle DB"
SCRIPT_VIOLATION = "ERROR: Uses In-Line Script Element"
IFRAME_VIOLATION = "ERROR: Uses In-Line iFrame Element"

VALID_PREFIXES = ["https://s3.amazonaws.com/im-ims-export/",
                  "https://k12.openstax.org/contents/raise"]


class Violation:

    def __init__(self, html_string, issue, location, details=None):
        self.html = html_string
        self.issue = issue
        self.location = location
        self.details = details

    def tostring(self):
        return f'{self.issue}\n At Location: {self.location}'


def validate_mbz(mbz_path, output_file):
    # Get html for both content and question_bank
    html_elements = utils.parse_backup_elements(mbz_path)

    violations = []
    violations.extend(find_style_violations(html_elements))
    violations.extend(find_source_violations(html_elements))
    violations.extend(find_tag_violations(html_elements))

    return violations


def find_style_violations(html_elements):
    violations = []
    for elem in html_elements:
        attributes = elem.get_attribute_names()
        if "style" in attributes:
            violations.append(Violation(elem.tostring(),
                                        STYLE_VIOLATION,
                                        elem.location))
    return violations


def find_tag_violations(html_elements):
    violations = []
    for elem in html_elements:
        hits = elem.get_child_elements("script")
        if len(hits) > 0:
            for hit in hits:
                violations.append(Violation(elem.tostring(),
                                            SCRIPT_VIOLATION,
                                            elem.location,
                                            hit))
        hits = elem.get_child_elements("iframe")
        if len(hits) > 0:
            for hit in hits:
                violations.append(Violation(elem.tostring(),
                                            IFRAME_VIOLATION,
                                            elem.location,
                                            hit))
    return violations


def find_source_violations(html_elements):
    violations = []
    for elem in html_elements:
        links = elem.get_attribute_values('src')
        for link in links:
            if len([prefix for prefix in VALID_PREFIXES if(prefix in link)]) \
                    > 0:    # check if link contains a valid prefix
                continue
            elif "@@PLUGINFILE@@" in link:
                violations.append(Violation(elem.tostring(),
                                            MOODLE_VIOLATION,
                                            elem.location,
                                            link))
            else:
                violations.append(Violation(elem.tostring(),
                                            SOURCE_VIOLATION,
                                            elem.location,
                                            link))
    return violations


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('mbz_path', type=str,
                        help='relative path to unzipped mbz')
    parser.add_argument('output_file', type=str,
                        help='Path to a file where flags will be outputted')
    args = parser.parse_args()

    mbz_path = Path(args.mbz_path).resolve(strict=True)
    output_file = Path(args.output_file)

    if not output_file.exists():
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("[]")

    validate_mbz(mbz_path, output_file)


# if __name__ == "__main__":
#     main()
