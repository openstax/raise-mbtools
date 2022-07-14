import pytest
from lxml import etree
from mbtools.models import MoodleHtmlElement, MoodleQuestionBank, MoodleQuiz


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
  <question_category>
    <question_versions>
      <version>1</version>
      <questions>
        <question id="1">
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
</question_categories>
    """.strip()

    with open(tmp_path / "questions.xml", "w") as qb:
        qb.write(question_bank_xml)

    question_bank = MoodleQuestionBank(tmp_path)
    question_bank_html = []
    for question in question_bank.questions:
        question_bank_html.extend(question.html_elements())

    assert len(question_bank_html) == 0


def test_quiz_used_qbank_entry_ids(tmp_path, mbz_builder, quiz_builder):
    quiz = quiz_builder(
        id=1,
        name="Quiz 1",
        questions=[
            {
                "id": "31",
                "questionid": "11"
            },
            {
                "id": "32",
                "questionid": "22"
            }
        ]
    )

    mbz_builder(tmp_path, activities=[quiz])
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
      <question_bank_entry id="3">
        <question_version>
          <question_versions>
            <version>1</version>
            <questions>
              <question id="question3">
              </question>
            </questions>
          </question_versions>
        </question_version>
     </question_bank_entry>
      <question_bank_entry id="4">
        <question_version>
          <question_versions>
            <version>1</version>
            <questions>
              <question id="question4">
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
        <question_version>
          <question_versions>
            <version>1</version>
            <questions>
              <question id="question1">
              </question>
            </questions>
          </question_versions>
          <question_versions>
            <version>2</version>
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
