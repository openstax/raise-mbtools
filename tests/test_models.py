from lxml import etree
from mbtools.models import MoodleHtmlElement, MoodleQuestionBank


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
  </question_category>
</question_categories>
    """.strip()

    with open(tmp_path / "questions.xml", "w") as qb:
        qb.write(question_bank_xml)

    question_bank = MoodleQuestionBank(tmp_path)
    question_bank_html = []
    for question in question_bank.questions():
        question_bank_html.extend(question.html_elements())

    assert len(question_bank_html) == 0
