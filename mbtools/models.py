from pathlib import Path
from xml.dom import NotFoundErr
from bs4 import BeautifulSoup as bs
from lxml import etree, html
from bs4 import BeautifulSoup
import uuid
import html
class Tag_Extractor(object):
    def __init__(self, object):
        self.object = object


    def replace_tags(self, type):
        output_html_files = {}
        if type == "page":
            # find and replace all html in content tag.
            etree_elements = self.find_etree_page_elements()
            # find html elements and check if they have been changed.
            valid_etree_elements = self.validate_etree_elements(etree_elements)
            # find check and replace HTML content.
            output_html_files = self.change_element(valid_etree_elements)

        elif type == "lesson":
            etree_elements = self.find_etree_lesson_elements()
            valid_etree_elements = self.validate_etree_elements(etree_elements)
            output_html_files = self.change_element(valid_etree_elements)

        return output_html_files
    # reason for these two methods is because inconsistant naming for content.
    def find_etree_lesson_elements(self):
        return self.object.etree.xpath("//pages/page/contents")

    def find_etree_page_elements(self):
        return self.object.etree.xpath("//page/content")

    def validate_etree_elements(self, etree_elements):
        valid_list = []
        for element in etree_elements:
                attrib_dict = element.attrib
                if element.tag == 'div' and \
                        "class" in attrib_dict.keys() and \
                        attrib_dict["class"] == "os-raise-content":
                    print("tag already replaced")
                    continue
                else:
                    valid_list.append(element)


        return valid_list

    def save_xml_changes(self):

        with open(self.object.activity_filename, "wb") as f:
            self.object.etree.write(f, encoding="utf-8", xml_declaration=False)

    def change_element(self, etree_elements):
        #iterate over elements
        # get the content of HTML

        html_file_dict = {}
        for element in etree_elements:
            content = element.text
            content_uuid = str(uuid.uuid4())

            tag =f'<div class="os-raise-content" data-content-id="{content_uuid}"></div>'
            element.text = tag
            html_file_dict[content_uuid] = content
        print(html_file_dict)
        # change original file content.
        self.save_xml_changes()
        return html_file_dict



class MoodleBackup:
    def __init__(self, mbz_path):
        self.mbz_path = Path(mbz_path)
        backup_xml_path = self.mbz_path / "moodle_backup.xml"
        self.etree = etree.parse(str(backup_xml_path))
        self.q_bank = MoodleQuestionBank(self.mbz_path)

    def activities(self, filter=[]):
        activity_elems = self.etree.xpath("//contents/activities/activity")
        activities = []
        for activity_elem in activity_elems:
            activity_type = activity_elem.find("modulename").text
            activity_path = \
                self.mbz_path / activity_elem.find("directory").text
            if activity_type == 'lesson' :
                if len(filter) == 0 or "lesson" in filter:

                    activities.append(
                        MoodleLesson(activity_path, self.mbz_path))
            elif activity_type == 'page':
                if len(filter) == 0 or "page" in filter:
                    activities.append(
                        MoodlePage(activity_path, self.mbz_path))
            elif activity_type == 'quiz':
                if len(filter) == 0 or "quiz" in filter:
                    activities.append(
                        MoodleQuiz(activity_path, self.mbz_path))
        return activities


class MoodleQuestionBank:
    def __init__(self, mbz_path):
        self.mbz_path = Path(mbz_path)
        self.questionbank_path = self.mbz_path / "questions.xml"
        self.etree = etree.parse(str(self.questionbank_path))

    def replace_tags(self):
        return {}
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
            if len(questions) != len(ids):
                raise(NotFoundErr)
        return questions



class MoodleLesson:
    def __init__(self, activity_path, mbz_path):
        self.mbz_path = Path(mbz_path)
        self.activity_path = activity_path
        self.activity_filename = str(self.activity_path / "lesson.xml")
        self.etree = etree.parse(self.activity_filename)

    def replace_tags(self):
        return Tag_Extractor(self).replace_tags("lesson")



    def html_elements(self):
        elements = []
        lesson_name = self.etree.xpath("//name")[0].text
        pages = self.etree.xpath("//pages/page")
        for page in pages:
            page_id = page.attrib["id"]
            page_title = page.xpath("title")[0].text
            contents = page.xpath("contents")

            location = \
                f'Lesson: {lesson_name} Page_id={page_id}'\
                f'Page Title: {page_title}'
            elements.append(MoodleHtmlElement(contents[0], location))

            if len(page.xpath("answers")) > 0:
                answer_texts = page.xpath("answers/answer_text")
                for answer in answer_texts:
                    answer_location = f'{location} Answer: {answer.text}'
                    elements.append(
                        MoodleHtmlElement(answer, answer_location))
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
    def replace_tags(self):
        return Tag_Extractor(self).replace_tags("page")

class MoodleQuiz:
    def __init__(self, activity_path, mbz_path, question_bank):
        self.mbz_path = Path(mbz_path)
        self.activity_path = activity_path
        self.activity_filename = str(self.activity_path / "quiz.xml")
        self.etree = etree.parse(self.activity_filename)
        self.question_bank = question_bank

    def replace_tags(self):
        return {}

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

    def replace_tags(self):
        return {}
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
        # self.etree = html.fromstring(self.parent.text)

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

    def get_attribute_values(self, attr, exception=None):
        values = []
        if attr in self.etree.attrib.keys():
            values.append(self.etree.attrib[attr])
        for elem in self.etree.xpath(".//*"):
            if elem.tag != exception or exception is None:
                if attr in elem.attrib.keys():
                    values.append(elem.attrib[attr])
        return values

    def get_child_elements(self, element_name):
        elems = []
        for child in self.etree.xpath(".//*"):
            if child.tag == element_name:
                elems.append(child)
        return elems
