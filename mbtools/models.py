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

    def elements(self):
        activity_elems = self.etree.xpath("//contents/activities/activity")
        activities = []
        for activity_elem in activity_elems:
            activity_type = activity_elem.find("modulename").text
            activity_path = \
                self.mbz_path / activity_elem.find("directory").text
            activities.append(
                MoodleActivity(activity_type, activity_path, self.mbz_path))
        html = []
        for activity in activities:
            html.extend(activity.html_elements())
        return html


class MoodleQuestionBank:
    def __init__(self, mbz_path):
        self.mbz_path = Path(mbz_path)
        self.questionbank_path = self.mbz_path / "questions.xml"
        self.etree = etree.parse(str(self.questionbank_path))

    def questions(self, ids=None, locations=None):
        questions = []
        if ids is None:
            query = \
                '//question_categories/question_category/questions/question'
            all_elems = self.etree.xpath(query)
            for elem in all_elems:
                location = "Question Bank, Question: " + elem.attrib['id']
                questions.append(
                    MoodleQuestion(elem, elem.attrib['id'], location))
        else:
            for i in range(0, len(ids)):
                query = '//question_categories/question_category/questions/'\
                        f'question[@id={ids[i]}]'
                elems = self.etree.xpath(query)
                if len(elems) == 0:
                    raise(NotFoundErr)
                else:
                    if locations is None:
                        location = f'Question Bank id={ids[i]}'
                    else:
                        location = locations[i]
                    questions.append(
                        MoodleQuestion(elems[0], ids[i], location))
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
        self.location = ""

    def html_elements(self):
        elements = []
        if self.activity_type == "lesson":
            lesson_name = self.etree.xpath("//name")[0].text
            page_query = "//pages/page"
            pages = self.etree.xpath(page_query)
            for page in pages:
                page_id = page.attrib["id"]
                page_title = page.xpath("title")[0].text
                contents = page.xpath("contents")
                location = \
                    f'Lesson: {lesson_name}, Page_id={page_id},'\
                    f'Page Title: {page_title}'
                elements.append(MoodleHtmlElement(contents[0], location))
                if len(page.xpath("answers")) > 0:
                    answer_texts = page.xpath("answers/answer_text")
                    for answer in answer_texts:
                        answer_location = f'{location} Answer: {answer.text}'
                        elements.append(
                            MoodleHtmlElement(answer, answer_location))
            return elements
        elif self.activity_type == "page":
            xpath_query = "//page/content"
            name = self.etree.xpath("//page/name")[0].text
            elements = self.etree.xpath(xpath_query)
            return [MoodleHtmlElement(el, name) for el in elements]
        elif self.activity_type == "quiz":
            ids = []
            locations = []
            quizes = self.etree.xpath("//quiz")
            for quiz in quizes:
                name = quiz.xpath("name")[0].text
                questions = quiz.xpath("question_instances/question_instance")
                for question in questions:
                    question_id = question.xpath("questionid")[0].text
                    location = f'{name} Question: {question_id}'
                    ids.append(question_id)
                    locations.append(location)

            question_objs = \
                MoodleQuestionBank(self.mbz_path).questions(ids, locations)
            elements = []
            for question in question_objs:
                elements.extend(question.html_elements())
            return elements
        else:
            return []


class MoodleQuestion:
    def __init__(self, question_elm, id, location):
        self.etree = question_elm
        self.location = location
        self.id = id

    def html_elements(self):
        elements = []
        question_texts = self.etree.xpath(
                f"//question[@id={self.id}]/questiontext")
        for question_html in question_texts:
            elements.append(
                MoodleHtmlElement(question_html, self.location))
        answer_texts = self.etree.xpath(
                f"//question[@id={self.id}]/answers/answer/answertext")
        for answer_html in answer_texts:
            elements.append(
                MoodleHtmlElement(answer_html, self.location))
        return elements


class MoodleHtmlElement:
    def __init__(self, parent, location):
        self.parent = parent
        self.location = location
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

    def get_attribute_names(self):
        attributes = []
        soup = BeautifulSoup(etree.tostring(self.etree))
        for tag in soup.find_all():
            attributes.extend(list(tag.attrs))
        return attributes

    def get_attribute_values(self, attr):
        values = []
        soup = BeautifulSoup(etree.tostring(self.etree))
        for tag in soup.find_all():
            if 'src' in tag.attrs:
                values.append(tag.attrs['src'])
        return values

    def get_child_elements(self, element_name):
        elems = []
        soup = BeautifulSoup(etree.tostring(self.etree))
        for tag in soup.find_all():
            if tag.name == element_name:
                if len(tag.contents) == 0:
                    elems.append("")
                else:
                    elems.append(str(tag.contents[0]))
        return elems
