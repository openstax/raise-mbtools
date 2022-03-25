from pathlib import Path
from xml.dom import NotFoundErr
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
            activities.append(
                MoodleActivity(activity_type, activity_path, self.mbz_path))
        return activities


class MoodleQuestionBank:
    def __init__(self, mbz_path):
        self.mbz_path = Path(mbz_path)
        self.questionbank_path = self.mbz_path / "questions.xml"
        self.etree = etree.parse(str(self.questionbank_path))

    def questions(self, ids=None):
        questions = []
        if ids is None:
            query = \
                '//question_categories/question_category/questions/question'
            all_elems = self.etree.xpath(query)
            for elem in all_elems:
                questions.append(MoodleQuestion(elem, elem.attrib['id']))
        else:
            for id in ids:
                query = '//question_categories/question_category/questions/'\
                        f'question[@id={id}]'
                elems = self.etree.xpath(query)
                if len(elems) == 0:
                    raise(NotFoundErr)
                else:
                    questions.append(MoodleQuestion(elems[0], id))
            if len(questions) != len(ids):
                raise(NotFoundErr)
        return questions


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
            xpath_query = "//pages/page/answers/answer_text"
            elements.extend(self.etree.xpath(xpath_query))
            return [MoodleHtmlElement(el) for el in elements]
        elif self.activity_type == "page":
            xpath_query = "//page/content"
            elements = self.etree.xpath(xpath_query)
            return [MoodleHtmlElement(el) for el in elements]
        elif self.activity_type == "quiz":
            xpath_query = \
                "//quiz/question_instances/question_instance/questionid"
            ids = []
            for question in self.etree.xpath(xpath_query):
                ids.append(question.text)

            question_objs = \
                MoodleQuestionBank(self.mbz_path).questions(ids)
            elements = []
            for question in question_objs:
                elements.extend(question.html_elements())
            return elements
        else:
            return []


class MoodleQuestion:
    def __init__(self, question_elm, id):
        self.etree = question_elm
        self.id = id

    def html_elements(self):
        elements = []
        question_texts = self.etree.xpath(
                f"//question[@id={self.id}]/questiontext")
        for question_html in question_texts:
            elements.append(
                MoodleHtmlElement(question_html))
        answer_texts = self.etree.xpath(
                f"//question[@id={self.id}]/answers/answer/answertext")
        for answer_html in answer_texts:
            elements.append(
                MoodleHtmlElement(answer_html))
        return elements


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
        ).encode(formatter="html5").decode('utf-8')
