import argparse
from lxml import etree
from csv import DictWriter
from pathlib import Path

from mbtools.models import MoodleHtmlElement, MoodleQuestionBank
from . import utils

STYLE_VIOLATION = "ERROR: Uses In-Line Styles"
SOURCE_VIOLATION = "ERROR: Uses External Resource with Invalid Prefix"
MOODLE_VIOLATION = "ERROR: References to Uploaded Files in Moodle DB"
SCRIPT_VIOLATION = "ERROR: Use of <script> element"
IFRAME_VIOLATION = "ERROR: Use of <iframe> with unexpected target"
HREF_VIOLATION = "ERROR: Uses invalid 'href' value in <a> tag"
UNNESTED_VIOLATION = "ERROR: Contains content not nested in HTML Element"
NESTED_IB_VIOLATION = "ERROR: Interactive block nested within HTML"
DUPLICATE_IB_UUID_VIOLATION = "ERROR: Duplicate interactive block UUID"
MISSING_IB_UUID_VIOLATION = "ERROR: Missing interactive block UUID"
INVALID_IB_UUID_VIOLATION = "ERROR: Invalid interactive block UUID"
DUPLICATE_QBANK_UUID_VIOLATION = "ERROR: Duplicate question bank UUID"
INVALID_QBANK_UUID_VIOLATION = "ERROR: Invalid question bank UUID"
TABLE_VIOLATION = "ERROR: Table violation: "

VALID_PREFIXES = [
    "https://k12.openstax.org/contents/raise",
    "https://www.youtube.com/",
    "https://digitalpromise.org"
]

VALID_IFRAME_PREFIXES = [
    "https://www.youtube.com",
    "https://player.vimeo.com",
    "https://www.geogebra.org/material/iframe/id"
]

VALID_HREF_PREFIXES = [
    "https://k12.openstax.org/contents/raise",
    "https://vimeo.com",
    "https://player.vimeo.com",
    "https://youtube.com",
    "https://www.youtube.com",
    "https://youtu.be",
    "https://characterlab.org/",
    "https://digitalpromise.org",
    "https://www.doe.virginia.gov",
    "https://tea.texas.gov",
    "https://www.sfusdmath.org",
    "https://www.engageny.org",
    "https://www.khanacademy.org",
    "https://teacher.desmos.com",
    "https://help.desmos.com",
    "https://www.geogebra.org",
    "https://geogebra.org"
]

VALID_HREF_VALUES = [
    "https://illustrativemathematics.org/",
    "https://openstax.org/",
    "https://www.wisewire.com/",
    "https://student.desmos.com",
    "https://desmos.com/calculator",
    "https://www.desmos.com/calculator",
    "https://student.desmos.com/"
]

VALID_STYLES = []

IB_CLASS_PREFIX = "os-raise-ib-"
IB_ALLOWED_NESTING = ["os-raise-ib-tooltip"]


class Violation:
    def __init__(self, issue, location, link=None):
        self.issue = issue
        self.location = location
        self.link = link

    def toDict(self):
        dict = {"issue": self.issue,
                "location": self.location,
                "link": self.link}
        return dict


def validate_mbz(mbz_path, include_styles=True, include_questionbank=False,
                 include_tables=False):
    question_bank = MoodleQuestionBank(mbz_path)

    html_elements = utils.parse_backup_elements(mbz_path)
    if include_questionbank:
        html_elements += utils.parse_question_bank_latest_for_html(mbz_path)
    html_validations = run_html_validations(html_elements, include_styles,
                                            include_tables)
    qbank_validations = run_qbank_validations(question_bank)
    return html_validations + qbank_validations


def validate_html(html_dir, include_styles=True,
                  include_tables=False):
    all_files = []
    for path in Path(html_dir).rglob('*.html'):
        all_files.append(path)
    html_elements = []
    for file_path in all_files:
        with open(file_path, 'r') as f:
            parent_string = '<content></content>'
            parent_element = etree.fromstring(parent_string)
            parent_element.text = f.read()
            html_elements.append(
                MoodleHtmlElement(parent_element, str(file_path))
            )
    return run_html_validations(html_elements, include_styles, include_tables)


def run_html_validations(html_elements, include_styles, include_tables):
    violations = []
    violations.extend(find_unnested_violations(html_elements))
    if len(violations) > 0:
        return violations
    if include_styles:
        violations.extend(find_style_violations(html_elements))
    if include_tables:
        violations.extend(find_table_violations(html_elements))
    violations.extend(find_source_violations(html_elements))
    violations.extend(find_tag_violations(html_elements))
    violations.extend(find_nested_ib_violations(html_elements))
    violations.extend(find_ib_uuid_violations(html_elements))
    return violations


def find_qbank_uuid_violations(question_bank):
    questions = question_bank.latest_questions
    qbe_to_uuid = {}
    observed_ids = set()
    violations_list = []
    for question in questions:
        qbe_to_uuid[question.question_bank_entry_id] = question.id_number

    for qbe_id, id_number in qbe_to_uuid.items():
        if not utils.validate_uuid4(id_number):
            violations_list.append(Violation(INVALID_QBANK_UUID_VIOLATION,
                                             question_bank.questionbank_path,
                                             f'question id: {qbe_id} uuid: '
                                             f'{id_number}'))
        if id_number in observed_ids:
            violations_list.append(Violation(DUPLICATE_QBANK_UUID_VIOLATION,
                                             question_bank.questionbank_path,
                                             f'question id: {qbe_id} uuid: '
                                             f'{id_number}'))
        observed_ids.add(id_number)
    return violations_list


def run_qbank_validations(question_bank):

    violations = []
    violations.extend(find_qbank_uuid_violations(question_bank))

    return violations


def find_unnested_violations(html_elements):
    violations = []
    for elem in html_elements:
        if len(elem.unnested_content) > 0:
            for fragment in elem.unnested_content:
                violations.append(Violation(UNNESTED_VIOLATION,
                                            elem.location,
                                            fragment))
    return violations


def find_style_violations(html_elements):
    violations = []
    for elem in html_elements:
        attributes = elem.get_attribute_values("style")
        for attr in attributes:
            if attr not in VALID_STYLES and attr != "":
                violations.append(Violation(STYLE_VIOLATION,
                                            elem.location,
                                            attr))
    return violations


def find_tag_violations(html_elements):
    violations = []
    for elem in html_elements:
        hits = elem.get_elements_by_name("script")
        for _ in hits:
            violations.append(Violation(SCRIPT_VIOLATION,
                                        elem.location))
        hits = elem.get_elements_by_name("iframe")
        for hit in hits:
            link = hit.attrib['src']
            if len([prefix for prefix in VALID_IFRAME_PREFIXES
                    if (prefix in link)]) == 0:
                violations.append(Violation(IFRAME_VIOLATION,
                                            elem.location,
                                            link))
        hits = elem.get_elements_by_name("a")
        for hit in hits:
            if "href" in hit.attrib.keys():
                link = hit.attrib["href"]
                prefix_match = [
                    pfx for pfx in VALID_HREF_PREFIXES if (pfx in link)
                ]
                if len(prefix_match) == 0 and link not in VALID_HREF_VALUES:
                    violations.append(Violation(HREF_VIOLATION,
                                                elem.location,
                                                link))
    return violations


def find_source_violations(html_elements):
    violations = []
    for elem in html_elements:
        links = elem.get_attribute_values('src', exception='iframe')
        for link in links:
            if len([prefix for prefix in VALID_PREFIXES if (prefix in link)]) \
                    > 0:    # check if link contains a valid prefix
                continue
            elif "@@PLUGINFILE@@" in link:
                violations.append(Violation(MOODLE_VIOLATION,
                                            elem.location,
                                            link))
            else:
                violations.append(Violation(SOURCE_VIOLATION,
                                            elem.location,
                                            link))
    return violations


def find_nested_ib_violations(html_elements):
    def is_unnestable_ib_component(etree_elem):
        """Helper function that looks at the class string for an element
        and determines if it's an unnestable component. This function avoids
        having to know all of the class names by looking for elements with
        the expected class prefix that don't have parents with the same prefix
        to differentiate component child elements.
        """
        class_string = etree_elem.attrib["class"]

        for class_name in class_string.split(" "):
            if class_name in IB_ALLOWED_NESTING:
                return False

        elem_parent = etree_elem.xpath("..")[0]
        if IB_CLASS_PREFIX in elem_parent.attrib.get("class", ""):
            return False

        return True

    violations = []

    for elem in html_elements:
        maybe_ibs = \
            elem.get_elements_with_string_in_class(
                IB_CLASS_PREFIX
            )
        maybe_broken_ibs = filter(is_unnestable_ib_component, maybe_ibs)
        for ib in maybe_broken_ibs:
            if not elem.element_is_fragment(ib):
                violations.append(Violation(
                    NESTED_IB_VIOLATION,
                    elem.location,
                    ib.attrib["class"]
                ))

    return violations


def find_ib_uuid_violations(html_elements):
    need_ids = [
        "os-raise-ib-input",
        "os-raise-ib-pset",
        "os-raise-ib-pset-problem"
    ]
    violations = []
    uuid_to_location = {}
    for elem in html_elements:
        maybe_ids = elem.get_elements_with_exact_class(need_ids)
        for ib in maybe_ids:
            if "data-content-id" not in ib.attrib.keys():
                # k12-399: Temporarily disabling
                pass
                # violations.append(Violation(
                #     MISSING_IB_UUID_VIOLATION,
                #     elem.location,
                #     None
                # ))
            else:
                uuid = ib.attrib["data-content-id"]
                if uuid in uuid_to_location.keys():
                    double_location = \
                        elem.location + " and " + uuid_to_location[uuid]
                    violations.append(Violation(
                        DUPLICATE_IB_UUID_VIOLATION,
                        double_location,
                        uuid
                    ))
                else:
                    uuid_to_location[uuid] = elem.location
                    # Confirm UUID is valid
                    if not utils.validate_uuid4(uuid):
                        violations.append(Violation(
                            INVALID_IB_UUID_VIOLATION,
                            elem.location,
                            uuid
                        ))
    return violations


def is_table_child_allowed(child_tag):
    ALLOWED_CHILDREN = [
        'table', 'caption', 'thead', 'tbody', 'th', 'tr', 'td', 'caption'
    ]
    return child_tag in ALLOWED_CHILDREN


def find_missing_class_violations(table, elem_location):
    if 'class' not in table.keys():
        msg = "class attribute is missing in <table>"
        return [Violation(TABLE_VIOLATION + msg, elem_location)]
    return []


def find_invalid_children_violations(table, elem_location):
    violations = []
    table_children = [elem.tag for elem in table.getchildren()]

    for child in table_children:
        if not is_table_child_allowed(child):
            msg = f"{child} is not allowed in table"
            violations.append(Violation(TABLE_VIOLATION + msg, elem_location))
    return violations


def find_missing_thead_tbody_violations(table, elem_location):
    violations = []
    table_children = [elem.tag for elem in table.getchildren()]

    if 'thead' not in table_children:
        msg = 'thead missing in table'
        violations.append(Violation(TABLE_VIOLATION + msg, elem_location))
    if 'tbody' not in table_children:
        msg = 'tbody missing in table'
        violations.append(Violation(TABLE_VIOLATION + msg, elem_location))
    return violations


def find_invalid_element_violations(element, elem_location):
    violations = []

    for tr in element:
        if not is_table_child_allowed(tr.tag):
            msg = f"{tr.tag} is not allowed"
            violations.append(Violation(TABLE_VIOLATION + msg, elem_location))

        for td_or_th in tr:
            if not is_table_child_allowed(td_or_th.tag):
                msg = f"{td_or_th.tag} is not allowed"
                violations.append(Violation(TABLE_VIOLATION + msg,
                                            elem_location))

            if td_or_th.tag == 'th':
                violations += find_th_violations(td_or_th, element.tag,
                                                 elem_location)
    return violations


def find_th_violations(td_or_th, element_tag, elem_location):
    violations = []

    if element_tag == 'thead':
        scope = td_or_th.get('scope')
        if scope != 'col':
            msg = 'must include scope attribute in thead th with value col'
            violations.append(Violation(TABLE_VIOLATION + msg, elem_location))

    elif element_tag == 'tbody':
        scope = td_or_th.get('scope')
        if scope != 'row':
            msg = 'must include scope attribute in tbody th with value row'
            violations.append(Violation(TABLE_VIOLATION + msg, elem_location))

    return violations


def find_table_no_th_violation(table, elem_location):
    violations = []

    has_th_in_tbody = False
    has_th_in_thead = False

    for thead_or_tbody in table.getchildren():
        for tr in thead_or_tbody:
            for th_or_td in tr:
                if th_or_td.tag == 'th' and thead_or_tbody.tag == 'tbody':
                    has_th_in_tbody = True

                if th_or_td.tag == 'th' and thead_or_tbody.tag == 'thead':
                    has_th_in_thead = True

    if table.get('class') == 'os-raise-doubleheadertable':
        if not (has_th_in_tbody and has_th_in_thead):
            msg = "doubleheadertable requires th in both thead and tbody"
            violations.append(Violation(TABLE_VIOLATION + msg, elem_location))
    else:
        if not (has_th_in_thead or has_th_in_tbody):
            msg = "th is required in either thead or tbody"
            violations.append(Violation(TABLE_VIOLATION + msg, elem_location))

    return violations


def find_table_violations(html_elements):
    violations = []

    for elem in html_elements:
        tables = elem.get_elements_by_name('table')
        for table in tables:
            elem_location = elem.location

            violations += find_missing_class_violations(table, elem_location)
            violations += find_invalid_children_violations(table,
                                                           elem_location)
            violations += find_missing_thead_tbody_violations(table,
                                                              elem_location)
            violations += find_table_no_th_violation(table, elem_location)
            for element in table.getchildren():
                violations += find_invalid_element_violations(element,
                                                              elem_location)
    return violations


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('mbz_path', type=str,
                        help='relative path to unzipped mbz')
    parser.add_argument('output_file', type=str,
                        help='Path to a file where flags will be outputted')
    parser.add_argument('mode', choices=['mbz', 'html'])
    parser.add_argument(
        '--no-qb',
        action='store_true',
        help="Exclude question bank in validation"
    )
    parser.add_argument(
        '--no-style',
        action='store_false',
        help="Exclude style violations"
    )

    parser.add_argument(
        '--tables',
        action='store_true',
        help="Include table validations"
    )

    args = parser.parse_args()

    mbz_path = Path(args.mbz_path).resolve(strict=True)
    output_file = Path(args.output_file)
    mode = args.mode
    include_questionbank = not args.no_qb
    include_styles = args.no_style
    include_tables = args.tables

    if not output_file.exists():
        output_file.parent.mkdir(parents=True, exist_ok=True)

    violations = []
    if mode == "html":
        violations = validate_html(mbz_path, include_styles, include_tables)
    elif mode == "mbz":
        violations = validate_mbz(mbz_path, include_styles,
                                  include_questionbank, include_tables)
    with open(output_file, 'w') as f:
        w = DictWriter(f, ['issue', 'location', 'link'])
        w.writeheader()
        for violation in violations:
            w.writerow(violation.toDict())


if __name__ == "__main__":
    main()
