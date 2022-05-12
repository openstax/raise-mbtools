from lxml import etree
from mbtools.models import MoodleHtmlElement


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
