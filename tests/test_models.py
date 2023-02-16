import pytest
from lxml import etree
from mbtools.models import MoodleHtmlElement, MoodleLessonPage, \
    MoodleQuestionBank, MoodleQuiz


def test_answerformat_filter(tmp_path):
    lesson_page_xml = """
<lesson>
  <name>Lesson name</name>
  <pages>
    <page id="0">
      <prevpageid>0</prevpageid>
      <nextpageid>0</nextpageid>
      <contents>Lesson content</contents>
      <title>Lesson page title</title>
      <answers>
        <answer id="1">
          <answerformat>0</answerformat>
          <answer_text>Not HTML answer content</answer_text>
          <responseformat>0</responseformat>
        </answer>
        <answer id="2">
          <answerformat>1</answerformat>
          <answer_text>HTML answer content</answer_text>
          <response>correct!</response>
          <responseformat>1</responseformat>
        </answer>
        <answer id="3">
          <answerformat>1</answerformat>
          <answer_text>HTML answer content</answer_text>
          <response></response>
          <responseformat>0</responseformat>
        </answer>
      </answers>
    </page>
  </pages>
</lesson>
  """

    lesson_page_etree = etree.fromstring(lesson_page_xml).xpath("//page")[0]
    lesson_page = MoodleLessonPage(lesson_page_etree)
    html_elems = lesson_page.html_elements()
    assert len(html_elems) == 4
    assert "Not HTML answer content" not in \
        [elem.parent.text for elem in html_elems]


def test_html_element_get_elements_with_string_in_class():
    html_content = """
<div>
  <p class="foo bar">Element foo bar</p>
  <p class="bar">Element bar</p>
  <p class="foobaz">Element foobaz</p>
</div>
    """
    parent = etree.fromstring("<content></content>")
    parent.text = html_content
    elem = MoodleHtmlElement(parent, "")
    foo_elems = elem.get_elements_with_string_in_class("foo")
    bar_elems = elem.get_elements_with_string_in_class("bar")
    jedi_elems = elem.get_elements_with_string_in_class("jedi")

    assert set([elem.text for elem in foo_elems]) == \
        set(["Element foo bar", "Element foobaz"])
    assert set([elem.text for elem in bar_elems]) == \
        set(["Element bar", "Element foo bar"])
    assert len(jedi_elems) == 0


def test_html_elements_element_is_fragment():
    html_content = """
<div>
  <p class="bar"></p>
</div>
<div class="foo bar"></div>
    """
    parent = etree.fromstring("<content></content>")
    parent.text = html_content
    elem = MoodleHtmlElement(parent, "")
    foo_elems = elem.get_elements_with_string_in_class("foo")
    assert elem.element_is_fragment(foo_elems[0])

    bar_elems = elem.get_elements_with_string_in_class("bar")
    assert not elem.element_is_fragment(bar_elems[0])


def test_question_answertext_filter(tmp_path):
    question_bank_xml = """
<?xml version="1.0" encoding="UTF-8"?>
<question_categories>
    <question_bank_entries>
      <question_bank_entry id="1">
  <idnumber>1234</idnumber>
  <question_category>
    <question_versions>
      <version>1</version>
      <questions>
        <question id="1">
          <qtype>numerical</qtype>
          <plugin_qtype_numerical_question>
            <answers>
              <answer>
                <answertext>112</answertext>
              </answer>
            </answers>
          </plugin_qtype_numerical_question>
        </question>
      </questions>
    </question_versions>
  </question_category>
      </question_bank_entry>
    </question_bank_entries>

</question_categories>
    """.strip()

    with open(tmp_path / "questions.xml", "w") as qb:
        qb.write(question_bank_xml)

    question_bank = MoodleQuestionBank(tmp_path)
    question_bank_html = []
    qbank_questions = question_bank.questions
    assert len(qbank_questions) == 1
    for question in qbank_questions:
        question_bank_html.extend(question.html_elements())

    assert len(question_bank_html) == 0


def test_question_text_filter(tmp_path):
    question_bank_xml = """
<?xml version="1.0" encoding="UTF-8"?>
<question_categories>
    <question_bank_entries>
      <question_bank_entry id="1">

  <idnumber>1234</idnumber>
  <question_category>
    <question_versions>
      <version>1</version>
      <questions>
        <question id="1">
          <qtype>shortanswer</qtype>
          <questiontext>{1:SHORTANSWER:%100%2#Congratulations!}</questiontext>
        </question>
      </questions>
    </question_versions>
  </question_category>
        </question_bank_entry>
      </question_bank_entries>

</question_categories>
    """.strip()

    with open(tmp_path / "questions.xml", "w") as qb:
        qb.write(question_bank_xml)

    question_bank = MoodleQuestionBank(tmp_path)
    question_bank_html = []
    qbank_questions = question_bank.questions
    assert len(qbank_questions) == 1
    for question in qbank_questions:
        question_bank_html.extend(question.html_elements())

    assert len(question_bank_html) == 0


def test_quiz_used_qbank_entry_ids(tmp_path, mbz_builder, quiz_builder):
    quiz = quiz_builder(
        id=1,
        name="Quiz 1",
        questions=[
            {
                "id": "31",
                "slot": 1,
                "page": 1,
                "questionid": "11"
            },
            {
                "id": "32",
                "slot": 1,
                "page": 2,
                "questionid": "22"
            }
        ]
    )

    mbz_builder(
        tmp_path,
        activities=[quiz],
        questionbank_questions=[
            {
                "id": 11,
                "idnumber": 1234,
                "html_content": "<p>Question 1</p>"
            },
            {
                "id": 22,
                "idnumber": 1235,
                "html_content": "<p>Question 2</p>"
            }
        ]
    )
    quiz = MoodleQuiz(
        tmp_path / "activities/quiz_1",
        tmp_path,
        MoodleQuestionBank(tmp_path)
    )
    assert quiz.used_qbank_entry_ids() == ["11", "22"]


def test_questionbank_delete_unused_question_bank_entries(tmp_path):
    questionbank_xml = """
<?xml version="1.0" encoding="UTF-8"?>
<question_categories>
  <question_category id="1">
    <question_bank_entries>
      <question_bank_entry id="1">
        <idnumber>1231</idnumber>
        <question_version>
          <question_versions>
            <version>1</version>
            <questions>
              <question id="question1">
                <qtype></qtype>
              </question>
            </questions>
          </question_versions>
        </question_version>
     </question_bank_entry>
      <question_bank_entry id="2">
        <idnumber>1232</idnumber>
        <question_version>
          <question_versions>
            <version>1</version>
            <questions>
              <question id="question2">
                <qtype></qtype>
              </question>
            </questions>
          </question_versions>
        </question_version>
     </question_bank_entry>
    </question_bank_entries>
  </question_category>
  <question_category id="2">
    <question_bank_entries>
      <question_bank_entry id="3">
        <idnumber>1233</idnumber>
        <question_version>
          <question_versions>
            <version>1</version>
            <questions>
              <question id="question3">
                <qtype></qtype>
              </question>
            </questions>
          </question_versions>
        </question_version>
     </question_bank_entry>
      <question_bank_entry id="4">
      <idnumber>1234</idnumber>
        <question_version>
          <question_versions>
            <version>1</version>
            <questions>
              <question id="question4">
                <qtype></qtype>
              </question>
            </questions>
          </question_versions>
        </question_version>
     </question_bank_entry>
    </question_bank_entries>
  </question_category>
</question_categories>
    """

    (tmp_path / "questions.xml").write_text(questionbank_xml.strip())
    questionbank = MoodleQuestionBank(tmp_path)
    questionbank.delete_unused_question_bank_entries(["2"])

    questions = questionbank.questions
    assert len(questions) == 1
    assert questions[0].id == "question2"


def test_questionbank_delete_empty_categories(tmp_path):
    questionbank_xml = """
<?xml version="1.0" encoding="UTF-8"?>
<question_categories>
  <question_category id="1">
    <question_bank_entries>
      <question_bank_entry id="1">
        <question_version>
          <question_versions>
            <version>1</version>
            <questions>
              <question id="question1">
              </question>
            </questions>
          </question_versions>
        </question_version>
     </question_bank_entry>
      <question_bank_entry id="2">
        <question_version>
          <question_versions>
            <version>1</version>
            <questions>
              <question id="question2">
              </question>
            </questions>
          </question_versions>
        </question_version>
     </question_bank_entry>
    </question_bank_entries>
  </question_category>
  <question_category id="2">
    <question_bank_entries>
    </question_bank_entries>
  </question_category>
</question_categories>
    """

    (tmp_path / "questions.xml").write_text(questionbank_xml.strip())
    questionbank = MoodleQuestionBank(tmp_path)
    questionbank.delete_empty_categories()

    question_categories = questionbank.etree.xpath("//question_category")
    assert len(question_categories) == 1


def test_questionbank_get_question_by_entry(tmp_path):
    questionbank_xml = """
<?xml version="1.0" encoding="UTF-8"?>
<question_categories>
  <question_category id="1">
    <question_bank_entries>
      <question_bank_entry id="1">
        <idnumber>1234</idnumber>
        <question_version>
          <question_versions>
            <version>1</version>
            <questions>
              <question id="question1">
                <qtype></qtype>
              </question>
            </questions>
          </question_versions>
          <question_versions>
            <version>2</version>
            <questions>
              <question id="question1">
                <qtype></qtype>
              </question>
            </questions>
          </question_versions>
        </question_version>
     </question_bank_entry>
      <question_bank_entry id="2">
        <idnumber>1235</idnumber>
        <question_version>
          <question_versions>
            <version>1</version>
            <questions>
              <question id="question2">
                <qtype></qtype>
              </question>
            </questions>
          </question_versions>
        </question_version>
     </question_bank_entry>
    </question_bank_entries>
  </question_category>
</question_categories>
    """

    (tmp_path / "questions.xml").write_text(questionbank_xml.strip())
    questionbank = MoodleQuestionBank(tmp_path)

    assert questionbank.get_question_by_entry("1", "1") is not None

    question1_latest = questionbank.get_question_by_entry("1", "$@NULL@$")
    assert question1_latest.version == "2"

    question2 = questionbank.get_question_by_entry("2", "1")
    assert question2.id == "question2"

    with pytest.raises(Exception):
        questionbank.get_question_by_entry("1", "3")


def test_questionbank_get_latest_questions(tmp_path):
    questionbank_xml = """
<?xml version="1.0" encoding="UTF-8"?>
<question_categories>
  <question_category id="1">
    <question_bank_entries>
      <question_bank_entry id="1">
        <idnumber>1234</idnumber>
        <question_version>
          <question_versions>
            <version>1</version>
            <questions>
              <question id="question1v1">
                <qtype></qtype>
              </question>
            </questions>
          </question_versions>
          <question_versions>
            <version>2</version>
            <questions>
              <question id="question1v2">
                <qtype></qtype>
              </question>
            </questions>
          </question_versions>
        </question_version>
     </question_bank_entry>
      <question_bank_entry id="2">
      <idnumber>1235</idnumber>
        <question_version>
          <question_versions>
            <version>11</version>
            <questions>
              <question id="question2v11">
                <qtype></qtype>
              </question>
            </questions>
          </question_versions>
        </question_version>
        <question_version>
          <question_versions>
            <version>10</version>
            <questions>
              <question id="question2v10">
                <qtype></qtype>
              </question>
            </questions>
          </question_versions>
        </question_version>
     </question_bank_entry>
    </question_bank_entries>
  </question_category>
</question_categories>
    """

    (tmp_path / "questions.xml").write_text(questionbank_xml.strip())
    questionbank = MoodleQuestionBank(tmp_path)

    assert len(questionbank.questions) == 4

    latest_questions = questionbank.latest_questions
    assert len(latest_questions) == 2
    assert latest_questions[0].version == "2"
    assert latest_questions[1].version == "11"


def test_find_multianswer_child_question(tmp_path):
    question_bank_xml = """
<?xml version="1.0" encoding="UTF-8"?>
<question_categories>
  <question_category>
    <question_bank_entry id="123">
      <idnumber>1234</idnumber>
      <question_version>
        <question_versions>
          <version>1</version>
          <questions>
            <question id="1">
              <qtype>multianswer</qtype>
              <plugin_qtype_multianswer_question>
                <multianswer>
                  <sequence>20,21</sequence>
                </multianswer>
              </plugin_qtype_multianswer_question>
              <questiontext></questiontext>
            </question>
          </questions>
        </question_versions>
      </question_version>
    </question_bank_entry>
    <question_bank_entry id="124">
      <idnumber>1234</idnumber>
      <question_version>
        <question_versions>
          <version>1</version>
          <questions>
            <question id="20">
              <qtype></qtype>
              <questiontext></questiontext>
            </question>
          </questions>
        </question_versions>
      </question_version>
    </question_bank_entry>
    <question_bank_entry id="125">
      <idnumber>1234</idnumber>
      <question_version>
        <question_versions>
          <version>1</version>
          <questions>
            <question id="21">
              <qtype></qtype>
              <questiontext></questiontext>
            </question>
          </questions>
        </question_versions>
      </question_version>
    </question_bank_entry>
  </question_category>
</question_categories>
    """.strip()

    quiz_xml = """
<?xml version="1.0" encoding="UTF-8"?>
<activity id="1" modulename="quiz">
  <quiz id="2">
    <name>My Quiz</name>
    <question_instances>
      <question_instance id="123">
        <slot>1</slot>
        <page>1</page>
        <question_reference>
          <questionbankentryid>123</questionbankentryid>
          <version>$@NULL@$</version>
        </question_reference>
      </question_instance>
    </question_instances>
  </quiz>
</activity>
    """.strip()

    with open(tmp_path / "questions.xml", "w") as qb:
        qb.write(question_bank_xml)
    (tmp_path / "activities").mkdir()
    with open(tmp_path / "activities" / "quiz.xml", "w") as qb:
        qb.write(quiz_xml)

    question_bank = MoodleQuestionBank(tmp_path)
    quiz = MoodleQuiz((tmp_path / "activities"), tmp_path, question_bank)

    results = quiz.used_qbank_entry_ids()
    assert len(results) == 3
    assert "123" in results
    assert "124" in results
    assert "125" in results
