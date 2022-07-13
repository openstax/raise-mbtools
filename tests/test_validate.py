import csv
from lxml import etree
from mbtools import validate_mbz_html
from mbtools.models import MoodleHtmlElement


def test_validate_mbz_fail_early_for_unnested_violations(
    tmp_path, page_builder, mbz_builder
):
    page1 = page_builder(
        id=1,
        name="Page 1",
        html_content="Page 1 unnested content"
    )

    page2 = page_builder(
        id=2,
        name="Page 2",
        html_content="<div><script>javascript</script></div>"
    )

    mbz_path = tmp_path / "mbz"
    mbz_builder(mbz_path, activities=[page1, page2])
    violations = validate_mbz_html.validate_mbz(mbz_path)

    assert len(violations) == 1
    violation = violations[0]
    assert violation.issue == validate_mbz_html.UNNESTED_VIOLATION
    assert violation.location == "Page 1"
    assert violation.link == "Page 1 unnested content"


def test_unnested_front():
    location = "here"
    parent = etree.fromstring("<content></content>")
    parent.text = 'Hi hello<p>actual_html</p>'
    elem = MoodleHtmlElement(parent, location)
    violations = validate_mbz_html.find_unnested_violations([elem])
    assert len(violations) == 1


def test_unnested_back():
    location = "here"
    parent = etree.fromstring("<content></content>")
    parent.text = '<p>actual_html</p>Hi Hello'
    elem = MoodleHtmlElement(parent, location)
    violations = validate_mbz_html.find_unnested_violations([elem])
    assert len(violations) == 1
    assert violations[0].issue == validate_mbz_html.UNNESTED_VIOLATION


def test_unnested_middle():
    location = "here"
    parent = etree.fromstring("<content></content>")
    parent.text = '<p>actual_html</p>Hi Hello<p>actual_html_also</p>'
    elem = MoodleHtmlElement(parent, location)
    violations = validate_mbz_html.find_unnested_violations([elem])
    assert len(violations) == 1
    assert violations[0].issue == validate_mbz_html.UNNESTED_VIOLATION


def test_unnested_multiple():
    location = "here"
    parent = etree.fromstring("<content></content>")
    parent.text = 'Front<p>actual_html</p>Middle<p>actual_html_also</p>Back'
    elem = MoodleHtmlElement(parent, location)
    violations = validate_mbz_html.find_unnested_violations([elem])
    assert len(violations) == 3
    for v in violations:
        assert v.issue == validate_mbz_html.UNNESTED_VIOLATION


def test_unnested_different_line():
    location = "here"
    parent = etree.fromstring("<content></content>")
    parent.text = '<p>actual_html</p>\nHi Hello'
    elem = MoodleHtmlElement(parent, location)
    violations = validate_mbz_html.find_unnested_violations([elem])
    assert len(violations) == 1
    assert violations[0].issue == validate_mbz_html.UNNESTED_VIOLATION


def test_unnested_ignore_comments():
    parent = etree.fromstring("<content></content>")
    parent.text = '''
    <!-- External comment -->
    <p>Real content</p>
    <div>
      <!-- Internal comment -->
    </div>
    '''
    elem = MoodleHtmlElement(parent, "")
    violations = validate_mbz_html.find_unnested_violations([elem])
    assert len(violations) == 0


def test_unnested_text_with_comments():
    parent = etree.fromstring("<content></content>")
    parent.text = '''
    <!-- External comment -->some text
    <p>Real content</p>
    <div>
      <!-- Internal comment -->
    </div>
    '''
    elem = MoodleHtmlElement(parent, "")
    violations = validate_mbz_html.find_unnested_violations([elem])
    assert len(violations) == 1
    assert violations[0].issue == validate_mbz_html.UNNESTED_VIOLATION


def test_ignore_space_tail():
    location = "here"
    parent = etree.fromstring("<content></content>")
    parent.text = '<p>actual_html_also</p>    '
    elem = MoodleHtmlElement(parent, location)
    violations = validate_mbz_html.find_unnested_violations([elem])
    assert len(violations) == 0


def test_style_violation():
    location = "here"
    parent = etree.fromstring("<content></content>")
    parent.text = '<p style="left: allign">html</p>'
    elem = MoodleHtmlElement(parent, location)
    style_violations = validate_mbz_html.find_style_violations([elem])
    assert len(style_violations) == 1
    assert style_violations[0].issue == validate_mbz_html.STYLE_VIOLATION
    assert style_violations[0].link == "left: allign"
    assert style_violations[0].location == "here"


def test_href_violation():
    location = "here"
    parent = etree.fromstring("<content></content>")
    parent.text = '<a href="something">html</a>'
    elem = MoodleHtmlElement(parent, location)
    style_violations = validate_mbz_html.find_tag_violations([elem])
    assert len(style_violations) == 1
    assert style_violations[0].issue == validate_mbz_html.HREF_VIOLATION
    assert style_violations[0].link == "something"
    assert style_violations[0].location == "here"


def test_script_violation():
    location = "here"
    parent = etree.fromstring("<content></content>")
    parent.text = '<script>javascript</script>'
    elem = MoodleHtmlElement(parent, location)
    style_violations = validate_mbz_html.find_tag_violations([elem])
    assert len(style_violations) == 1
    assert style_violations[0].issue == validate_mbz_html.SCRIPT_VIOLATION
    assert style_violations[0].link is None
    assert style_violations[0].location == "here"


def test_iframe_violation():
    location = "here"
    parent = etree.fromstring("<content></content>")
    parent.text = '<iframe src="link">something</iframe>'
    elem = MoodleHtmlElement(parent, location)
    style_violations = validate_mbz_html.find_tag_violations([elem])
    assert len(style_violations) == 1
    assert style_violations[0].issue == validate_mbz_html.IFRAME_VIOLATION
    assert style_violations[0].link == "link"
    assert style_violations[0].location == "here"


def test_source_violation():
    location = "here"
    parent = etree.fromstring("<content></content>")
    parent.text = '<img src="link">'
    elem = MoodleHtmlElement(parent, location)
    style_violations = validate_mbz_html.find_source_violations([elem])
    assert len(style_violations) == 1
    assert style_violations[0].issue == validate_mbz_html.SOURCE_VIOLATION
    assert style_violations[0].link == "link"
    assert style_violations[0].location == "here"


def test_moodle_source_violation():
    location = "here"
    parent = etree.fromstring("<content></content>")
    parent.text = '<img src="@@PLUGINFILE@@">'
    elem = MoodleHtmlElement(parent, location)
    style_violations = validate_mbz_html.find_source_violations([elem])
    assert len(style_violations) == 1
    assert style_violations[0].issue == validate_mbz_html.MOODLE_VIOLATION
    assert style_violations[0].link == "@@PLUGINFILE@@"
    assert style_violations[0].location == "here"


def test_valid_source_no_violation():
    location = "here"
    parent = etree.fromstring("<content></content>")
    parent.text = f'<img src="{validate_mbz_html.VALID_PREFIXES[0]}">'
    elem = MoodleHtmlElement(parent, location)
    style_violations = validate_mbz_html.find_source_violations([elem])
    assert len(style_violations) == 0


def test_find_nested_ib_violations():
    valid_content = """
<div class="os-raise-ib-sometype">
  <div class="os-raise-ib-sometype-somedata"></div>
  <div class="os-raise-ib-sometype-otherdata"></div>
</div>
<div class="os-raise-ib-anothertype">
<p><span class="os-raise-ib-tooltip styleclass">vocab word</span></p>
</div>
    """
    bad_content = """
<div>
  <div class="os-raise-ib-nestedtype"></div>
</div>
<div class="os-raise-ib-anothertype"></div>
<div class="os-raise-ib-sometype">
  <div class="os-raise-ib-sometype-somedata"></div>
  <div class="os-raise-ib-sometype-otherdata"></div>
</div>
    """
    html1 = etree.fromstring("<content></content>")
    html1.text = valid_content
    elem1 = MoodleHtmlElement(html1, "loc1")
    html2 = etree.fromstring("<content></content>")
    html2.text = bad_content
    elem2 = MoodleHtmlElement(html2, "loc2")
    violations = validate_mbz_html.find_nested_ib_violations([elem1, elem2])
    assert len(violations) == 1
    assert violations[0].issue == validate_mbz_html.NESTED_IB_VIOLATION
    assert violations[0].location == "loc2"
    assert violations[0].link == "os-raise-ib-nestedtype"


def test_find_nested_ib_violations_mbz(
    tmp_path, mbz_builder, page_builder, mocker
):
    bad_content = '<div><div class="os-raise-ib-nestedtype"></div></div>'
    page1 = page_builder(1, "Page", bad_content)
    mbz_builder(tmp_path / "mbz", [page1])

    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}/mbz", f"{tmp_path}/test_output.csv"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(tmp_path / "test_output.csv"))
    errors = [row for row in reader]
    assert len(errors) == 1
    assert errors[0]["issue"] == validate_mbz_html.NESTED_IB_VIOLATION
    assert errors[0]["location"] == "Page"
    assert errors[0]["link"] == "os-raise-ib-nestedtype"


def test_find_tag_violations_mbz(
    tmp_path, mbz_builder, page_builder, mocker
):
    bad_content = '<div><script></script></div>'
    page1 = page_builder(1, "Page", bad_content)
    mbz_builder(tmp_path / "mbz", [page1])

    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}/mbz", f"{tmp_path}/test_output.csv"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(tmp_path / "test_output.csv"))
    errors = [row for row in reader]
    assert len(errors) == 1
    assert errors[0]["issue"] == validate_mbz_html.SCRIPT_VIOLATION
    assert errors[0]["location"] == "Page"
    assert errors[0]["link"] == ""


def test_find_style_violations_mbz(
    tmp_path, mbz_builder, page_builder, mocker
):
    bad_content = '<p style="color: blue"></p>'
    page1 = page_builder(1, "Page", bad_content)
    mbz_builder(tmp_path / "mbz", [page1])

    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}/mbz", f"{tmp_path}/test_output.csv"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(tmp_path / "test_output.csv"))
    errors = [row for row in reader]
    assert len(errors) == 1
    assert errors[0]["issue"] == validate_mbz_html.STYLE_VIOLATION
    assert errors[0]["location"] == "Page"
    assert errors[0]["link"] == "color: blue"


def test_find_source_violations_mbz(
    tmp_path, mbz_builder, page_builder, mocker
):
    bad_content = '<img src="http://foobar">'
    page1 = page_builder(1, "Page", bad_content)
    mbz_builder(tmp_path / "mbz", [page1])

    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}/mbz", f"{tmp_path}/test_output.csv"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(tmp_path / "test_output.csv"))
    errors = [row for row in reader]
    assert len(errors) == 1
    assert errors[0]["issue"] == validate_mbz_html.SOURCE_VIOLATION
    assert errors[0]["location"] == "Page"
    assert errors[0]["link"] == "http://foobar"


def test_find_multiple_activity_violations_mbz(
    tmp_path, mbz_builder, page_builder, lesson_builder, mocker
):
    bad_content = '<img src="http://foobar"><script></script>'
    page1 = page_builder(1, "Page", bad_content)
    lesson2 = lesson_builder(
        id=2,
        name="Lesson 2",
        pages=[
            {
                "id": 21,
                "title": "Lesson 2 Page 1",
                "html_content": '<img src="@@PLUGINFILE@@">'
            },
            {
                "id": 21,
                "title": "Lesson 2 Page 2",
                "html_content": "<p></p>",
                "answers": [
                    {
                        "id": 111,
                        "html_content": '<iframe src="http://foobaz"></iframe>'
                    }
                ]
            },
        ]
    )

    mbz_builder(tmp_path / "mbz", [page1, lesson2])

    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}/mbz", f"{tmp_path}/test_output.csv"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(tmp_path / "test_output.csv"))
    errors = [row for row in reader]
    assert len(errors) == 4
    page_src_error = {
        "issue": validate_mbz_html.SOURCE_VIOLATION,
        "location": "Page",
        "link": "http://foobar"
    }
    page_script_error = {
        "issue": validate_mbz_html.SCRIPT_VIOLATION,
        "location": "Page",
        "link": ""
    }
    lesson_moodle_source_error = {
        "issue": validate_mbz_html.MOODLE_VIOLATION,
        "location": "Lesson 2 (page: Lesson 2 Page 1)",
        "link": "@@PLUGINFILE@@"
    }
    lesson_iframe_errors = {
        "issue": validate_mbz_html.IFRAME_VIOLATION,
        "location": "Lesson 2 (page: Lesson 2 Page 2) (answer id: 111)",
        "link": "http://foobaz"
    }
    assert page_src_error in errors
    assert page_script_error in errors
    assert lesson_moodle_source_error in errors
    assert lesson_iframe_errors in errors


def test_questionbank_validation_and_optout_flag_mbz(
    tmp_path, mbz_builder, quiz_builder, mocker
):
    quiz = quiz_builder(
        id=1,
        name="Quiz",
        questions=[
            {
                "id": 1,
                "questionid": 2
            }
        ]
    )
    mbz_builder(
        tmp_path / "mbz",
        activities=[quiz],
        questionbank_questions=[
            {
                "id": 1,
                "html_content": '<img src="@@PLUGINFILE@@">',
                "answers": [
                    {
                        "id": 11,
                        "html_content": "<script></script>"
                    }
                ]
            },
            {
                "id": 2,
                "html_content": '<iframe src="http://foobaz"></iframe>',
                "matches": [
                    {
                        "id": 2,
                        "answer_content": "Some non-HTML content",
                        "question_html_content": '<img src="http://foobar">'
                    }
                ]
            }
        ]
    )

    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}/mbz", f"{tmp_path}/test_output.csv"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(tmp_path / "test_output.csv"))
    errors = [row for row in reader]
    assert len(errors) == 6
    q1_error1 = {
        "issue": validate_mbz_html.MOODLE_VIOLATION,
        "location": "Question Bank, Question: 1",
        "link": "@@PLUGINFILE@@"
    }
    q1_error2 = {
        "issue": validate_mbz_html.SCRIPT_VIOLATION,
        "location": "Question Bank, Question: 1",
        "link": ""
    }
    q2_error1 = {
        "issue": validate_mbz_html.IFRAME_VIOLATION,
        "location": "Question Bank, Question: 2",
        "link": "http://foobaz"
    }
    q2_error2 = {
        "issue": validate_mbz_html.SOURCE_VIOLATION,
        "location": "Question Bank, Question: 2",
        "link": "http://foobar"
    }
    quiz_errror1 = {
        "issue": validate_mbz_html.IFRAME_VIOLATION,
        "location": "Quiz Question: 2",
        "link": "http://foobaz"
    }
    quiz_errror2 = {
        "issue": validate_mbz_html.SOURCE_VIOLATION,
        "location": "Quiz Question: 2",
        "link": "http://foobar"
    }
    assert q1_error1 in errors
    assert q1_error2 in errors
    assert q2_error1 in errors
    assert q2_error2 in errors
    assert quiz_errror1 in errors
    assert quiz_errror2 in errors

    # Run with question bank validation off
    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}/mbz", f"{tmp_path}/test_output_noqb.csv", "--no-qb"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(tmp_path / "test_output_noqb.csv"))
    errors = [row for row in reader]
    assert len(errors) == 2
    assert quiz_errror1 in errors
    assert quiz_errror2 in errors


def test_multiple_violations_on_content_with_fragments(
    tmp_path, page_builder, mbz_builder, mocker
):
    bad_content = '<img src="@@PLUGINFILE@@"><p style="color: blue;"></p>'
    page1 = page_builder(1, "Page", bad_content)
    mbz_builder(tmp_path / "mbz", [page1])

    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}/mbz", f"{tmp_path}/test_output.csv"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(tmp_path / "test_output.csv"))
    errors = [row for row in reader]
    assert len(errors) == 2

    page_style_error = {
        "issue": validate_mbz_html.STYLE_VIOLATION,
        "location": "Page",
        "link": "color: blue;"
    }
    page_moodle_error = {
        "issue": validate_mbz_html.MOODLE_VIOLATION,
        "location": "Page",
        "link": "@@PLUGINFILE@@"
    }

    assert page_style_error in errors
    assert page_moodle_error in errors


def test_style_exclusion_from_validation_flag_mbz(
    tmp_path, mbz_builder, page_builder, mocker
):
    bad_content = '<p style="color: blue"></p>'
    page1 = page_builder(1, "Page", bad_content)
    mbz_builder(tmp_path / "mbz", [page1])

    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}/mbz", f"{tmp_path}/test_output.csv", "--no-style"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(tmp_path / "test_output.csv"))
    errors = [row for row in reader]
    assert len(errors) == 0
