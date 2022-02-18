from pathlib import Path
from lxml import etree, html
from bs4 import BeautifulSoup


class MoodleBackup:
    def __init__(self, mbz_path):
        self.mbz_path = Path(mbz_path)
        backup_xml_path = self.mbz_path / "moodle_backup.xml"
        self.etree = etree.parse(str(backup_xml_path))

    def activities(self):
        activity_elems = self.etree.xpath("//contents/activities/activity")
        activities = []
        for activity_elem in activity_elems:
            activity_type = activity_elem.find("modulename").text
            activity_path = \
                self.mbz_path / activity_elem.find("directory").text
            activities.append(MoodleActivity(activity_type, activity_path))
        return activities


class MoodleActivity:
    def __init__(self, activity_type, activity_path):
        self.activity_path = Path(activity_path)
        self.activity_type = activity_type
        self.activity_filename = \
            str(self.activity_path / f"{self.activity_type}.xml")
        self.etree = etree.parse(self.activity_filename)

    def html_elements(self):
        # We currently only expect / support parsing HTML from lesson and page
        # activities
        if self.activity_type == "lesson":
            xpath_query = "//pages/page/contents"
        elif self.activity_type == "page":
            xpath_query = "//page/content"
        else:
            return []

        return [MoodleHtmlElement(el) for el in self.etree.xpath(xpath_query)]


class MoodleHtmlElement:
    def __init__(self, parent):
        self.parent = parent
        self.etree = html.fromstring(self.parent.text)

    def find_references_containing(self, src_content):
        matching_elems = self.etree.xpath(
            f'//*[contains(@src, "{src_content}")]'
        )

        return [el.get("src") for el in matching_elems]

    def tostring(self):
        # Pass things through bs4 so we can avoid adding closing tags and
        # closing slashes that lxml may otherwise emit on void elements
        return BeautifulSoup(
            etree.tostring(self.etree),
            "html.parser"
        ).encode(formatter="html5")
