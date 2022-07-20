import uuid
from pathlib import Path
from xml.dom import NotFoundErr
from lxml import etree, html
from bs4 import BeautifulSoup

QUESTION_ANSWER_TEXT_IGNORE_TYPES = [
    "plugin_qtype_numerical_question"
]


class MoodleBackup:
    def __init__(self, mbz_path):
        self.mbz_path = Path(mbz_path)
        backup_xml_path = self.mbz_path / "moodle_backup.xml"
        self.etree = etree.parse(str(backup_xml_path))
        self.q_bank = MoodleQuestionBank(self.mbz_path)

    def activities(self, section_id=None):
        if section_id is None:
            activity_elems = self.etree.xpath("//contents/activities/activity")
        else:
            activity_elems = self.etree.xpath(
                f"//contents/activities/activity[sectionid='{section_id}']"
            )
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

    def quizzes(self):
        activity_elems = self.etree.xpath("//contents/activities/activity")
        activities = []
        for activity_elem in activity_elems:
            activity_type = activity_elem.find("modulename").text
            if activity_type != 'quiz':
                continue
            activity_path = \
                self.mbz_path / activity_elem.find("directory").text
            activities.append(
                MoodleQuiz(activity_path, self.mbz_path, self.q_bank))
        return activities

    def sections(self):
        section_elements = self.etree.xpath("//contents/sections/section")
        sections = []
        for s in section_elements:
            id = s.xpath("sectionid")[0].text
            title = s.xpath("title")[0].text
            sections.append(MoodleSection(id, title, self.mbz_path))
        return sections


class MoodleSection:
    def __init__(self, id, title, mbz_path):
        self.mbz_path = Path(mbz_path)
        self.id = id
        self.title = title


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

    def delete_unused_questions(self, used_question_ids):
        query = \
            '//question_categories/question_category/questions/question'
        elems = self.etree.xpath(query)
        for elem in elems:
            question_id = elem.attrib["id"]
            if question_id not in used_question_ids:
                elem.getparent().remove(elem)

    def delete_empty_categories(self):
        query = '//question_categories/question_category'
        elems = self.etree.xpath(query)
        for elem in elems:
            questions = elem.xpath('questions/question')
            if (len(questions)) == 0:
                elem.getparent().remove(elem)


class MoodleLessonPage:
    def __init__(self, tree, location):
        self.tree = tree
        self.location = location + f' (page: {self.name()})'
        self.id = int(self.tree.attrib['id'])

    def name(self):
        return self.tree.xpath("title")[0].text

    def next(self):
        return int(self.tree.xpath("nextpageid")[0].text)

    def prev(self):
        return int(self.tree.xpath("prevpageid")[0].text)

    def answers(self):
        answer_objs = []
        for answer in self.tree.xpath("answers/answer"):
            answer_objs.append(
                MoodleLessonAnswer(answer, self.location)
            )
        return answer_objs

    def html_element(self):
        return MoodleHtmlElement(self.tree.xpath("contents")[0], self.location)

    def html_elements(self):
        elems = []
        elems.append(self.html_element())
        for answer in self.answers():
            elems.append(answer.html_element())
        return elems


class MoodleLessonAnswer:
    def __init__(self, tree, location):
        self.tree = tree
        self.location = location + f' (answer id: {self.tree.attrib["id"]})'

    def name(self):
        return self.tree.attrib["id"]

    def html_element(self):
        answer_text = self.tree.xpath("answer_text")[0]
        return MoodleHtmlElement(answer_text, self.location)


class MoodleLesson:
    def __init__(self, activity_path, mbz_path):
        self.mbz_path = Path(mbz_path)
        self.activity_path = activity_path
        self.activity_filename = str(self.activity_path / "lesson.xml")
        self.etree = etree.parse(self.activity_filename)

    def name(self):
        return self.etree.xpath("//name")[0].text

    def lesson_pages(self):
        page_objs = []
        for page in self.etree.xpath("//pages/page"):
            page_objs.append(MoodleLessonPage(page, self.name()))
        return page_objs

    def html_elements(self):
        elems = []
        for page in self.lesson_pages():
            elems.extend(page.html_elements())
        return elems


class MoodlePage:
    def __init__(self, activity_path, mbz_path):
        self.mbz_path = Path(mbz_path)
        self.activity_path = activity_path
        self.activity_filename = str(self.activity_path / "page.xml")
        self.etree = etree.parse(self.activity_filename)

    def name(self):
        return self.etree.xpath("//page/name")[0].text

    def html_elements(self):
        xpath_query = "//page/content"
        elements = self.etree.xpath(xpath_query)
        return [MoodleHtmlElement(el, self.name()) for el in elements]


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

    def question_ids(self):
        ids = []
        quizzes = self.etree.xpath("//quiz")
        for quiz in quizzes:
            questions = quiz.xpath("question_instances/question_instance")
            for question in questions:
                question_id = question.xpath("questionid")[0].text
                ids.append(question_id)

        return ids


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
                f"//question[@id={self.id}]//answers/answer/answertext")
        for answer_html in answer_texts:
            answer_qtype = answer_html.xpath("../../..")[0]
            if answer_qtype.tag not in QUESTION_ANSWER_TEXT_IGNORE_TYPES:
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
            if type(fragment) not in [html.HtmlElement, html.HtmlComment]:
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
        return html_fragments_to_string(self.etree_fragments)

    def remove_attr(self, attr):
        for elem in self.etree_fragments[0].xpath(f'//*[@{attr}]'):
            elem.attrib.pop(attr)
        self.update_html()

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

    def update_html(self):
        self.parent.text = self.tostring()


def html_fragments_to_string(fragments):
    # Pass things through bs4 so we can avoid adding closing tags and
    # closing slashes that lxml may otherwise emit on void elements
    html_content = b''.join(
        [etree.tostring(fragment) for fragment in fragments])
    return BeautifulSoup(
        html_content,
        "html.parser"
    ).encode(formatter="html5").decode('utf-8')
