import argparse
from csv import DictWriter
from pathlib import Path
from . import utils

STYLE_VIOLATION = "ERROR: Uses In-Line Styles"
SOURCE_VIOLATION = "ERROR: Uses External Resource with Invalid Prefix"
MOODLE_VIOLATION = "ERROR: References to Uploaded Files in Moodle DB"
SCRIPT_VIOLATION = "ERROR: Use of <script> element"
IFRAME_VIOLATION = "ERROR: Use of <iframe> with unexpected target"
HREF_VIOLATION = "ERROR: Uses invalid 'href' value in <a> tag"
UNNESTED_VIOLATION = "ERROR: Contains content not nested in HTML Element"

VALID_PREFIXES = ["https://s3.amazonaws.com/im-ims-export/",
                  "https://k12.openstax.org/contents/raise",
                  "https://www.youtube.com/",
                  "https://digitalpromise.org"]

VALID_IFRAME_PREFIXES = ["https://www.youtube.com"]

VALID_HREF_PREFIXES = ["https://vimeo.com",
                       "https://player.vimeo.com",
                       "https://youtube.com",
                       "https://www.youtube.com",
                       "https://youtu.be",
                       "https://characterlab.org/",
                       "https://digitalpromise.org"]

VALID_STYLES = []


class Violation:
    def __init__(self, html_string, issue, location, link=None):
        self.html = html_string
        self.issue = issue
        self.location = location
        self.link = link

    def toDict(self):
        dict = {"issue": self.issue,
                "location": self.location,
                "link": self.link}
        return dict


def validate_mbz(mbz_path):

    html_elements = utils.parse_backup_elements(mbz_path)

    violations = []
    violations.extend(find_unnested_violations(html_elements))
    violations.extend(find_style_violations(html_elements))
    violations.extend(find_source_violations(html_elements))
    violations.extend(find_tag_violations(html_elements))

    return violations


def find_unnested_violations(html_elements):
    violations = []
    for elem in html_elements:
        if len(elem.unnested_content) > 0:
            for fragment in elem.unnested_content:
                violations.append(Violation(elem.tostring(),
                                            UNNESTED_VIOLATION,
                                            elem.location,
                                            fragment))
    return violations


def find_style_violations(html_elements):
    violations = []
    for elem in html_elements:
        attributes = elem.get_attribute_values("style")
        for attr in attributes:
            if attr not in VALID_STYLES and attr != "":
                violations.append(Violation(elem.tostring(),
                                            STYLE_VIOLATION,
                                            elem.location,
                                            attr))
    return violations


def find_tag_violations(html_elements):
    violations = []
    for elem in html_elements:
        hits = elem.get_elements_by_name("script")
        for _ in hits:
            violations.append(Violation(elem.tostring(),
                                        SCRIPT_VIOLATION,
                                        elem.location))
        hits = elem.get_elements_by_name("iframe")
        for hit in hits:
            link = hit.attrib['src']
            if len([prefix for prefix in VALID_IFRAME_PREFIXES
                    if(prefix in link)]) == 0:
                violations.append(Violation(elem.tostring(),
                                            IFRAME_VIOLATION,
                                            elem.location,
                                            link))
        hits = elem.get_elements_by_name("a")
        for hit in hits:
            if "href" in hit.attrib.keys():
                link = hit.attrib["href"]
                if len([prefix for prefix in VALID_HREF_PREFIXES
                        if(prefix in link)]) == 0:
                    violations.append(Violation(elem.tostring(),
                                                HREF_VIOLATION,
                                                elem.location,
                                                link))
    return violations


def find_source_violations(html_elements):
    violations = []
    for elem in html_elements:
        links = elem.get_attribute_values('src', exception='iframe')
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

    violations = validate_mbz(mbz_path)
    with open(output_file, 'w') as f:
        w = DictWriter(f, ['issue', 'location', 'link'])
        w.writeheader()
        for violation in violations:
            w.writerow(violation.toDict())


if __name__ == "__main__":
    main()
