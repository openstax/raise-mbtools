from uuid import uuid4
from pathlib import Path
from lxml import etree, html
from bs4 import BeautifulSoup
from mbtools import utils
QUESTION_TEXT_IGNORE_TYPES = [
    "shortanswer"
]

QUESTION_ANSWER_TEXT_IGNORE_TYPES = [
    "numerical",
    "shortanswer"
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
            sections.append(MoodleSection(s))
        return sections


class MoodleSection:
    def __init__(self, section_elem):
        self.etree = section_elem
        self.id = self.etree.xpath("./sectionid")[0].text
        self.title = self.etree.xpath("./title")[0].text


class MoodleQuestionBank:
    LATEST_VERSION_MARKER = "$@NULL@$"

    def __init__(self, mbz_path):
        self.mbz_path = Path(mbz_path)
        self.questionbank_path = self.mbz_path / "questions.xml"
        self.etree = etree.parse(str(self.questionbank_path))

    @property
    def questions(self):
        return [
            MoodleQuestion(q) for q in self.etree.xpath(
                "//questions/question"
            )
        ]

    @property
    def latest_questions(self):
        questions = []

        for qbe in self.etree.xpath("//question_bank_entry"):
            latest_question = self.get_question_by_entry(
                qbe.attrib["id"],
                self.LATEST_VERSION_MARKER
            )
            questions.append(latest_question)

        return questions

    def get_question_by_entry(self, question_bank_entry_id, version):
        question_bank_entry = self.etree.xpath(
            f'//question_bank_entry[@id="{question_bank_entry_id}"]'
        )[0]

        # The reference may have a specific ID or a marker to indicate latest
        maybe_result = None
        latest_version = 0
        question_versions = question_bank_entry.xpath(".//question_versions")

        for question_version in question_versions:
            curr_version = question_version.xpath("./version")[0].text
            curr_version_int = int(curr_version)
            question = question_version.xpath(".//question")[0]
            if (version == curr_version):
                maybe_result = MoodleQuestion(question)
                break
            if (version == self.LATEST_VERSION_MARKER) and \
               (curr_version_int > latest_version):
                latest_version = curr_version_int
                maybe_result = MoodleQuestion(question)

        if maybe_result is None:
            raise Exception(
                f"Could not find question entry {question_bank_entry_id} "
                f"version {version} in bank"
            )
        return maybe_result

    def get_entry_id_by_question_id(self, question_id):
        question_from_question_id = self.etree.xpath(
            f'//question[@id="{question_id}"]'
        )[0]
        return question_from_question_id.xpath(
            "../../../.."
        )[0].attrib["id"]

    def delete_unused_question_bank_entries(self, used_question_entry_ids):
        query = \
            '//question_bank_entry'
        elems = self.etree.xpath(query)
        for elem in elems:
            question_bank_entry_id = elem.attrib["id"]
            if question_bank_entry_id not in used_question_entry_ids:
                elem.getparent().remove(elem)

    def delete_empty_categories(self):
        elems = self.etree.xpath('//question_categories/question_category')
        for elem in elems:
            questions = elem.xpath(
                './question_bank_entries/question_bank_entry'
            )
            if (len(questions)) == 0:
                elem.getparent().remove(elem)

    def inject_question_uuids(self):
        elems = self.etree.xpath('//question_categories/question_category')
        for elem in elems:
            questions = elem.xpath(
                './question_bank_entries/question_bank_entry'
            )

            for question in questions:
                id_number = question.findall('.//idnumber')
                if not utils.validate_uuid4(id_number[0].text):
                    id_number[0].text = str(uuid4())


class MoodleLessonAnswer:
    def __init__(self, etree, lesson_page):
        self.etree = etree
        self.lesson_page = lesson_page
        self.answer_format = etree.xpath("answerformat")[0].text

    @property
    def location(self):
        return f"{self.lesson_page.location}: Answer Value"

    def answer_text_html(self):
        answer_text = self.etree.xpath("answer_text")[0]
        return MoodleHtmlElement(answer_text, self.location)

    def response_html(self):
        if self.etree.xpath("responseformat")[0].text == "1":
            response = self.etree.xpath("response")[0]
            if response.text is not None:
                response_location = self.location + " Response"
                return MoodleHtmlElement(response, response_location)
            else:
                return None
        else:
            return None

    def html_elements(self):
        elems = [self.answer_text_html()]
        response_html = self.response_html()
        if response_html is not None:
            elems.append(response_html)
        return elems


class MoodleLessonPage:
    def __init__(self, etree):
        self.etree = etree
        self.id = self.etree.attrib['id']
        self.name = self.etree.xpath("title")[0].text
        self.next = self.etree.xpath("nextpageid")[0].text
        self.prev = self.etree.xpath("prevpageid")[0].text

    @property
    def location(self):
        lesson_name = self.etree.xpath("../../name")[0].text
        return f"{lesson_name} (page: {self.name})"

    def page_type(self):
        qtype = self.etree.xpath("qtype")[0].text
        if qtype == '3':
            return 'multichoice'
        if qtype == '20':
            return 'content'
        raise Exception("qtype attribute value error in "
                        f"{self.name}")  # pragma: no cover

    def answers(self):
        answer_objs = []
        for answer in self.etree.xpath("answers/answer"):
            answer_format = answer.xpath("answerformat")[0]
            # We need to check the answer format to filter out things
            # like buttons which are also serialized as answers but are
            # not HTML
            if answer_format.text == "1":
                answer_objs.append(
                    MoodleLessonAnswer(answer, self)
                )
        return answer_objs

    def html_element(self):
        return MoodleHtmlElement(
            self.etree.xpath("contents")[0],
            self.location
        )

    def html_elements(self):
        elems = []
        elems.append(self.html_element())
        for answer in self.answers():
            elems.extend(answer.html_elements())
        return elems


class MoodleLesson:
    def __init__(self, activity_path, mbz_path):
        self.mbz_path = Path(mbz_path)
        self.activity_path = activity_path
        self.activity_filename = str(self.activity_path / "lesson.xml")
        self.module_filename = str(self.activity_path / "module.xml")
        self.etree = etree.parse(self.activity_filename)
        self.name = self.etree.xpath("//name")[0].text
        self.module_etree = etree.parse(self.module_filename)

    def lesson_pages(self):
        page_objs = []
        for page in self.etree.xpath("//pages/page"):
            page_objs.append(MoodleLessonPage(page))
        return page_objs

    def html_elements(self):
        elems = []
        for page in self.lesson_pages():
            elems.extend(page.html_elements())
        return elems

    def is_visible(self):
        if self.module_etree.xpath("//visible")[0].text == '1':
            return '1'
        if self.module_etree.xpath("//visible")[0].text == '0':
            return '0'
        raise Exception("Visible attribute value error in lesson "
                        f"{self.name}")  # pragma: no cover


class MoodlePage:
    def __init__(self, activity_path, mbz_path):
        self.mbz_path = Path(mbz_path)
        self.activity_path = activity_path
        self.activity_filename = str(self.activity_path / "page.xml")
        self.module_filename = str(self.activity_path / "module.xml")
        self.etree = etree.parse(self.activity_filename)
        self.name = self.etree.xpath("//page/name")[0].text
        self.module_etree = etree.parse(self.module_filename)

    def html_elements(self):
        xpath_query = "//page/content"
        elements = self.etree.xpath(xpath_query)
        return [MoodleHtmlElement(el, self.name) for el in elements]

    def is_visible(self):
        if self.module_etree.xpath("//visible")[0].text == '1':
            return '1'
        if self.module_etree.xpath("//visible")[0].text == '0':
            return '0'
        raise Exception("Visible attribute value error in page "
                        f"{self.name}")  # pragma: no cover


class MoodleQuiz:
    def __init__(self, activity_path, mbz_path, question_bank):
        self.mbz_path = Path(mbz_path)
        self.activity_path = activity_path
        self.activity_filename = str(self.activity_path / "quiz.xml")
        self.etree = etree.parse(self.activity_filename)
        self.question_bank = question_bank
        self.name = self.etree.xpath("//activity/quiz/name")[0].text

    @property
    def quiz_questions(self):
        results = []
        quizzes = self.etree.xpath("//quiz")
        for quiz in quizzes:
            questions = quiz.xpath("./question_instances/question_instance")
            for question in questions:
                results.append(MoodleQuizQuestion(question))
        return results

    def html_elements(self):
        qbank_questions = []
        for question in self.quiz_questions:
            qbank_questions.append(
                self.question_bank.get_question_by_entry(
                    question.qbank_entry_id,
                    question.version
                )
            )

        elements = []
        for question in qbank_questions:
            elements.extend(question.html_elements())
        return elements

    def used_qbank_entry_ids(self):
        entry_ids = [
            question.qbank_entry_id for question in self.quiz_questions
        ]
        for question in self.quiz_questions:
            entry_id = question.qbank_entry_id
            version = question.version
            moodle_question = self.question_bank\
                .get_question_by_entry(entry_id, version)

            children_question_ids = moodle_question.child_question_ids()
            for id in children_question_ids:
                entry_ids.append(
                    self.question_bank
                        .get_entry_id_by_question_id(id)
                )

        return entry_ids


class MoodleQuizQuestion:
    """This class models a <question_instance> inside of quiz.xml"""
    def __init__(self, question_elem):
        self.etree = question_elem
        self.qbank_entry_id = \
            self.etree.xpath(
                "./question_reference/questionbankentryid"
            )[0].text
        self.version = self.etree.xpath("./question_reference/version")[0].text
        self.slot = self.etree.xpath("./slot")[0].text


class MoodleQuestion:
    """This class models a <question> from a <question_bank_entry> in
    questions.xml
    """
    def __init__(self, question_elm):
        self.etree = question_elm
        self.id = self.etree.attrib['id']
        self.version = self.etree.xpath("../../version")[0].text
        self.id_number = self.etree.xpath('../../../../idnumber')[0].text
        self.question_type = self.etree.xpath('./qtype')[0].text
        self.question_bank_entry_id =\
            self.etree.xpath("../../../..")[0].attrib["id"]

    @property
    def text(self):
        return self.etree.xpath('./questiontext')[0].text

    @property
    def location(self):
        return f"Question bank ID {self.id} version {self.version}"

    def html_elements(self):
        elements = []
        question_texts = self.etree.xpath('.//questiontext')
        for question_html in question_texts:
            if self.question_type not in QUESTION_TEXT_IGNORE_TYPES:
                elements.append(
                    MoodleHtmlElement(question_html, self.location))
        answer_texts = self.etree.xpath('.//answers/answer/answertext')
        for answer_html in answer_texts:
            if self.question_type not in QUESTION_ANSWER_TEXT_IGNORE_TYPES:
                elements.append(
                    MoodleHtmlElement(answer_html, self.location))
        return elements

    def child_question_ids(self):
        maybe_child_ids = self.etree.xpath(
            "./plugin_qtype_multianswer_question/multianswer/sequence"
        )
        if maybe_child_ids:
            return maybe_child_ids[0].text.split(',')
        return []

    def multichoice_answers(self):
        answers = self.etree.xpath(
            './/plugin_qtype_multichoice_question/answers/answer')
        answer_objs = []
        for answer in answers:
            answer_objs.append(MoodleMultichoiceAnswer(answer))
        return answer_objs


class MoodleMultichoiceAnswer:
    """This class models an <answer> from the <answers> under a
    MoodleQuestion"""
    def __init__(self, answer):
        self.etree = answer
        self.grade = float(self.etree.xpath('./fraction')[0].text)
        self.text = self.etree.xpath('./answertext')[0].text
        self.feedback = self.etree.xpath('./feedback')[0].text


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
            content_uuid = str(uuid4())
            content = self.parent.text
            tag = f'<div class="os-raise-content" ' \
                  f'data-content-id="{content_uuid}"></div>'

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

    def get_elements_with_exact_class(self, classes):
        # NOTE This method returns a serites of elements whose classes match
        #   exactly one of the classes provided
        elems = []
        for item in classes:
            xpath_query = f"//div[@class='{item}']"
            elems.extend(self.etree_fragments[0].xpath(xpath_query))
        return elems

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
