from pathlib import Path
from xml.dom import NotFoundErr
from lxml import etree, html
from bs4 import BeautifulSoup


class MoodleBackup:
    def __init__(self, mbz_path):
        self.mbz_path = Path(mbz_path)
        self.backup_xml_path = self.mbz_path / "moodle_backup.xml"
        self.etree = etree.parse(str(self.backup_xml_path))

    def activities(self):
        activity_elems = self.etree.xpath("//contents/activities/activity")
        activities = []
        for activity_elem in activity_elems:
            activity_type = activity_elem.find("modulename").text
            activity_path = \
                self.mbz_path / activity_elem.find("directory").text
            activities.append(
                MoodleActivity(activity_type, activity_path, self.mbz_path))
        return activities


class MoodleQuestionBank:
    def __init__(self, mbz_path):
        self.mbz_path = Path(mbz_path)
        self.questionbank_path = self.mbz_path / "questions.xml"
        self.question_etree = etree.parse(str(self.questionbank_path))

    def questions(self):
        question_elms = self.question_etree.xpath(
            "//question_categories/question_category/questions/question"
            )
        question_objects = []
        for question_elm in question_elms:
            id = question_elm.attrib['id']
            question_objects.append(
                MoodleQuestion(question_elm, id)
                )
        return question_objects

    def questions_by_id(self, ids):
        question_elms = self.question_etree.xpath(
            "//question_categories/question_category/questions/question"
            )
        question_objects = []
        for question_elm in question_elms:
            id = question_elm.attrib['id']
            if id in ids:
                question_objects.append(
                    MoodleQuestion(question_elm, id)
                    )
        if len(question_objects) == 0:
            raise(NotFoundErr)
        return question_objects


class MoodleActivity:
    def __init__(self, activity_type, activity_path, mbz_path):
        self.mbz_path = Path(mbz_path)
        self.activity_path = Path(activity_path)
        self.activity_type = activity_type
        self.activity_filename = \
            str(self.activity_path / f"{self.activity_type}.xml")
        self.etree = etree.parse(self.activity_filename)

    def html_elements(self):
        elements = []
        if self.activity_type == "lesson":
            xpath_query = "//pages/page/contents"
            elements = self.etree.xpath(xpath_query)
        elif self.activity_type == "page":
            xpath_query = "//page/content"
            elements = self.etree.xpath(xpath_query)
        elif self.activity_type == "quiz":
            xpath_query = \
                "//quiz/question_instances/question_instance/questionid"
            ids = []
            for question in self.etree.findall(xpath_query):
                ids.append(question.text)
            elements.extend(self._get_questions_from_bank(ids))
        else:
            return []

        return [MoodleHtmlElement(el) for el in elements]

    def _get_questions_from_bank(self, ids):
        elements = []
        question_objs = \
            MoodleQuestionBank(self.mbz_path).questions_by_id(ids)
        for question in question_objs:
            elements.extend(question.get_all_lxml_elements())
        return elements


class MoodleQuestion:
    def __init__(self, question_elm, id):
        self.etree = question_elm
        self.id = id

    def get_all_moodle_elements(self):
        moodle_elements = []
        question_texts = self.etree.xpath(
                f"//question[@id={self.id}]/questiontext")
        for question_html in question_texts:
            moodle_elements.append(MoodleHtmlElement(question_html, self.use_location))
        answer_texts = self.etree.xpath(
                f"//question[@id={self.id}]/answers/answer/answertext")
        for answer_html in answer_texts:
            moodle_elements.append(MoodleHtmlElement(answer_html, self.use_location))
        return moodle_elements


class MoodleHtmlElement:
    def __init__(self, parent, use_location):
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

    def get_attribute_names(self):
        attributes = []
        soup = BeautifulSoup(etree.tostring(self.etree))
        for tag in soup.find_all():
            attributes.extend(list(tag.attrs))
        return attributes

    def use_location(self):
        return self.use_location
