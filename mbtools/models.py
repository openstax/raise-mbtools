import uuid
from pathlib import Path
from xml.dom import NotFoundErr
from lxml import etree, html
from bs4 import BeautifulSoup


class MoodleBackup:
    def __init__(self, mbz_path):
        self.mbz_path = Path(mbz_path)
        backup_xml_path = self.mbz_path / "moodle_backup.xml"
        self.etree = etree.parse(str(backup_xml_path))
        self.q_bank = MoodleQuestionBank(self.mbz_path)

    def activities(self):
        activity_elems = self.etree.xpath("//contents/activities/activity")
        activities = []
        for activity_elem in activity_elems:
            activity_type = activity_elem.find("modulename").text
            activity_path = \
                self.mbz_path / activity_elem.find("directory").text
            if activity_type == 'lesson':
                activities.append(
                    MoodleLesson(activity_path, self.mbz_path))
            elif activity_type == 'page':
                activities.append(
                    MoodlePage(activity_path, self.mbz_path))
            elif activity_type == 'quiz':
                activities.append(
                    MoodleQuiz(activity_path, self.mbz_path, self.q_bank))
        return activities


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
            elems = self.etree.xpath(query)
            for elem in elems:
                location = "Question Bank, Question: " + elem.attrib['id']
                questions.append(
                    MoodleQuestion(elem,
                                   elem.attrib['id'],
                                   location))
        else:
            for i in range(0, len(ids)):
                query = \
                    '//question_categories/question_category/questions/'\
                    f'question[@id={ids[i]}]'
                elems = self.etree.xpath(query)
                if len(elems) == 0:
                    raise(NotFoundErr)
                else:
                    if locations is None:
                        location = f'Question Bank id={ids[i]}'
                    else:
                        location = locations[i]
                    questions.append(MoodleQuestion(elems[0],
                                                    ids[i],
                                                    location))

        return questions


class MoodleLesson:
    def __init__(self, activity_path, mbz_path):
        self.mbz_path = Path(mbz_path)
        self.activity_path = activity_path
        self.activity_filename = str(self.activity_path / "lesson.xml")
        self.etree = etree.parse(self.activity_filename)

    def html_elements(self):
        elements = []
        lesson_name = self.etree.xpath("//name")[0].text
        pages = self.etree.xpath("//pages/page")
        for page in pages:
            page_id = page.attrib["id"]
            page_title = page.xpath("title")[0].text
            contents = page.xpath("contents")

            location = \
                f'Lesson: {lesson_name} (page id={page_id}) ' \
                f'Page Title: {page_title}'
            elements.append(MoodleHtmlElement(contents[0], location))

            for answer in page.xpath("answers/answer"):
                answer_format = answer.xpath("answerformat")[0]
                # We need to check the answer format to filter out things
                # like buttons which are also serialized as answers but are
                # not HTML
                if answer_format.text == "1":
                    answer_text = answer.xpath("answer_text")[0]
                    answer_location = \
                        f'{location} (answer id: {answer.attrib["id"]})'
                    elements.append(
                        MoodleHtmlElement(answer_text, answer_location))
        return elements


class MoodlePage:
    def __init__(self, activity_path, mbz_path):
        self.mbz_path = Path(mbz_path)
        self.activity_path = activity_path
        self.activity_filename = str(self.activity_path / "page.xml")
        self.etree = etree.parse(self.activity_filename)

    def html_elements(self):
        xpath_query = "//page/content"
        name = self.etree.xpath("//page/name")[0].text
        elements = self.etree.xpath(xpath_query)
        return [MoodleHtmlElement(el, name) for el in elements]


class MoodleQuiz:
    def __init__(self, activity_path, mbz_path, question_bank):
        self.mbz_path = Path(mbz_path)
        self.activity_path = activity_path
        self.activity_filename = str(self.activity_path / "quiz.xml")
        self.etree = etree.parse(self.activity_filename)
        self.question_bank = question_bank

    def html_elements(self):
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
        question_objs = self.question_bank.questions(ids, locations)

        elements = []
        for question in question_objs:
            elements.extend(question.html_elements())
        return elements


class MoodleQuestion:
    def __init__(self, question_elm, id, location):
        self.etree = question_elm
        self.location = location
        self.id = id

    def html_elements(self):
        elements = []
        question_texts = self.etree.xpath(
                f"//question[@id={self.id}]//questiontext")
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
        self.etree_fragments = []
        self.unnested_content = []

        # Catch strings that exist without html tags
        temp = html.fragments_fromstring(self.parent.text)
        for fragment in temp:
            if type(fragment) != html.HtmlElement:
                self.unnested_content.append(fragment)
            elif (fragment.tail is not None and fragment.tail.strip()):
                self.unnested_content.append(fragment.tail)
                fragment.tail = None
                self.etree_fragments.append(fragment)
            else:
                self.etree_fragments.append(fragment)

    def replace_content_tag(self):
        if self.parent.tag in ["content", "contents"]:
            attrib_dict = self.etree_fragments[0].attrib
            if "class" in attrib_dict.keys() and \
                    attrib_dict["class"] == "os-raise-content":
                return None
            content_uuid = str(uuid.uuid4())
            content = self.parent.text
            tag = f'<div class="os-raise-content" ' \
                  f'data-content-id="{ content_uuid }"></div>'

            self.parent.text = tag
            return {"uuid": content_uuid,
                    "content": content}
        return None

    def tostring(self):
        # Pass things through bs4 so we can avoid adding closing tags and
        # closing slashes that lxml may otherwise emit on void elements
        html_content = b''.join(
            [etree.tostring(fragment) for fragment in self.etree_fragments])
        return BeautifulSoup(
            html_content,
            "html.parser"
        ).encode(formatter="html5").decode('utf-8')

    def remove_attr(self, attr):
        for elem in self.etree_fragments[0].xpath(f'//*[@{attr}]'):
            elem.attrib.pop(attr)
        self.parent.text = self.tostring()

    def get_attribute_values(self, attr, exception=None):
        values = []
        for elem in self.etree_fragments[0].xpath(f'//*[@{attr}]'):
            if elem.tag != exception or exception is None:
                values.append(elem.attrib[attr])
        return values

    def get_elements_by_name(self, element_name):
        elems = []
        for child in self.etree_fragments[0].xpath(f'//{element_name}'):
            elems.append(child)
        return elems

    def get_elements_with_string_in_class(self, class_string):
        # NOTE: This method is only checking if the class string is included
        #  in the attribute string versus if the specific class is defined
        xpath_query = f"//*[contains(@class, '{class_string}')]"
        return self.etree_fragments[0].xpath(xpath_query)

    def element_is_fragment(self, elem):
        """Checks if the provided element is a fragment"""
        return elem in self.etree_fragments
