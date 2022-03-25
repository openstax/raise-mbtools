import argparse
from pathlib import Path
from . import utils

STYLE_VIOLATION = "Uses In-Line Styles"


def validate_mbz(mbz_path, output_file):
    # Get html for both content and question_bank
    html_elements = utils.parse_backup_for_moodle_html_elements(mbz_path)
    html_elements.extend(
        utils.parse_question_bank_for_moodle_html_elements(mbz_path))

    violations = {}
    violations.update(find_style_violations(html_elements))
    violations.update(find_script_violations(html_elements))
    violations.update(find_iframe_violations(html_elements))

    violations.update(find_external_source_violations(html_elements))
    violations.update(find_moodle_source_violations(html_elements))

    return violations


def find_style_violations(html_elements):
    violations = {}
    for elem in html_elements:
        attributes = elem.get_attribute_names()
        if "style" in attributes:
            violations[elem.tostring()] = STYLE_VIOLATION
    return violations


def find_script_violations(html_elements):
    pass


def find_iframe_violations(html_elements):
    pass


def find_external_source_violations(html_elements):
    pass


def find_moodle_source_violations(html_elements):
    pass


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
