import csv
import os
from lxml import etree
from mbtools import validate_mbz_html
from mbtools.models import MoodleHtmlElement
from pathlib import Path
import pytest


@pytest.fixture
def test_data_path():
    return Path(__file__).parent / "data/validate_mbz_html"


@pytest.fixture
def question_xml(test_data_path):
    with open(test_data_path / "questions.xml", "r") as f:
        questions = f.read()
    return questions


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
    parent.text = '<a href="https://openstax.org/apps/archive" >html</a>'
    parent.text += '<a href="https://openstax.org/" target="_blank">html</a>'
    elem = MoodleHtmlElement(parent, location)
    style_violations = validate_mbz_html.find_tag_violations([elem])
    assert len(style_violations) == 2
    assert style_violations[0].issue == validate_mbz_html.HREF_VIOLATION
    assert style_violations[0].link == "https://openstax.org/apps/archive"
    assert style_violations[0].location == "here"
    assert style_violations[1].issue == validate_mbz_html.LINK_TARGET_VIOLATION
    assert style_violations[1].link == "https://openstax.org/apps/archive"
    assert style_violations[1].location == "here"


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
        ["", f"{tmp_path}/mbz", f"{tmp_path}/test_output.csv", "mbz"]
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
        ["", f"{tmp_path}/mbz", f"{tmp_path}/test_output.csv", "mbz"]
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
        ["", f"{tmp_path}/mbz", f"{tmp_path}/test_output.csv", "mbz"]
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
        ["", f"{tmp_path}/mbz", f"{tmp_path}/test_output.csv", "mbz"]
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
                        "html_content":
                            '<iframe src="http://foobaz"></iframe>',
                        "response": '<p style="left: align">response</p>'
                    }
                ]
            },
        ]
    )

    mbz_builder(tmp_path / "mbz", [page1, lesson2])

    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}/mbz", f"{tmp_path}/test_output.csv", "mbz"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(tmp_path / "test_output.csv"))
    errors = [row for row in reader]
    assert len(errors) == 5
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
        "location": "Lesson 2 (page: Lesson 2 Page 2): Answer Value",
        "link": "http://foobaz"
    }
    lesson_style_errors = {
        "issue": validate_mbz_html.STYLE_VIOLATION,
        "location": "Lesson 2 (page: Lesson 2 Page 2): Answer Value Response",
        "link": "left: align"
    }

    assert page_src_error in errors
    assert page_script_error in errors
    assert lesson_moodle_source_error in errors
    assert lesson_iframe_errors in errors
    assert lesson_style_errors in errors


def test_questionbank_validation_and_optout_flag_mbz(
    tmp_path, mbz_builder, quiz_builder, mocker
):
    quiz = quiz_builder(
        id=1,
        name="Quiz",
        questions=[
            {
                "id": 1,
                "slot": 1,
                "page": 1,
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
                "idnumber": 'f79cdda5-8411-4f8b-8648-47fb0e74ecb1',
                "html_content": '<img src="@@PLUGINFILE@@">',
                "answers": [
                    {
                        "id": 11,
                        "grade": 1,
                        "html_content": "<script></script>"
                    }
                ]
            },
            {
                "id": 2,
                "idnumber": 'f79cdda5-8911-4f8b-8648-47fb0e24ecb1',
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
        ["", f"{tmp_path}/mbz", f"{tmp_path}/test_output.csv", "mbz"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(tmp_path / "test_output.csv"))
    errors = [row for row in reader]
    assert len(errors) == 6
    q1_error1 = {
        "issue": validate_mbz_html.MOODLE_VIOLATION,
        "location": "Question bank ID questionid1 version 1",
        "link": "@@PLUGINFILE@@"
    }
    q1_error2 = {
        "issue": validate_mbz_html.SCRIPT_VIOLATION,
        "location": "Question bank ID questionid1 version 1",
        "link": ""
    }
    q2_error1 = {
        "issue": validate_mbz_html.IFRAME_VIOLATION,
        "location": "Question bank ID questionid2 version 1",
        "link": "http://foobaz"
    }
    q2_error2 = {
        "issue": validate_mbz_html.SOURCE_VIOLATION,
        "location": "Question bank ID questionid2 version 1",
        "link": "http://foobar"
    }
    quiz_errror1 = {
        "issue": validate_mbz_html.IFRAME_VIOLATION,
        "location": "Question bank ID questionid2 version 1",
        "link": "http://foobaz"
    }
    quiz_errror2 = {
        "issue": validate_mbz_html.SOURCE_VIOLATION,
        "location": "Question bank ID questionid2 version 1",
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
        ["", f"{tmp_path}/mbz", f"{tmp_path}/test_output_noqb.csv",
         "mbz", "--no-qb"]
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
        ["", f"{tmp_path}/mbz", f"{tmp_path}/test_output.csv", "mbz"]
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
        ["", f"{tmp_path}/mbz", f"{tmp_path}/test_output.csv",
         "mbz", "--no-style"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(tmp_path / "test_output.csv"))
    errors = [row for row in reader]
    assert len(errors) == 0


def test_single_html_file_unested_violation(tmp_path, mocker):
    html = 'Hi Hello<p>Content</p>'
    html_path = str(tmp_path) + "/html/"
    os.mkdir(html_path)
    file_path = html_path + "123.html"
    with open(file_path, 'w') as f:
        f.write(html)

    output_filepath = f"{tmp_path}/test_output.csv"
    mocker.patch(
        "sys.argv",
        ["", html_path, output_filepath, "html"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(output_filepath))
    errors = [row for row in reader]
    assert len(errors) == 1

    assert validate_mbz_html.UNNESTED_VIOLATION in errors[0]["issue"]
    assert '/html/123.html' in errors[0]["location"]


def test_multiple_html_file_unnested_violations(tmp_path, mocker):
    html_1 = 'Hi Hello<p>Content</p>'
    html_2 = 'Hi Hello 2<p>Content</p>'
    html_path = str(tmp_path) + "/html/"
    os.mkdir(html_path)
    file_path_1 = html_path + "123.html"
    file_path_2 = html_path + "456.html"
    with open(file_path_1, 'w') as f:
        f.write(html_1)
    with open(file_path_2, 'w') as f:
        f.write(html_2)

    output_filepath = f"{tmp_path}/test_output.csv"
    mocker.patch(
        "sys.argv",
        ["", html_path, output_filepath, "html"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(output_filepath))
    errors = [row for row in reader]
    issues = [row["issue"] for row in errors]
    locations = [row["location"] for row in errors]
    assert len(errors) == 2

    for issue in issues:
        assert validate_mbz_html.UNNESTED_VIOLATION in issue
    for location in locations:
        assert ('/html/123.html' in location or '/html/456.html' in location)


def test_single_html_file_each_violation(
    tmp_path, mocker
):
    html = '''<div>
  <p style="left: allign">Content</p>
  <img src="link"></img>
  <iframe src="link"></iframe>
  <script>javascript</script>
  <img src="@@PLUGINFILE@@"></img>
  <a href="link" target="_blank"></a>
</div>'''

    html_path = str(tmp_path) + "/html/"
    os.mkdir(html_path)
    file_path = html_path + "123.html"
    with open(file_path, 'w') as f:
        f.write(html)

    output_filepath = f"{tmp_path}/test_output.csv"
    mocker.patch(
        "sys.argv",
        ["", html_path, output_filepath, "html"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(output_filepath))
    errors = [row for row in reader]
    issues = [row["issue"] for row in errors]
    locations = [row["location"] for row in errors]
    assert len(errors) == 6

    assert validate_mbz_html.SOURCE_VIOLATION in issues
    assert validate_mbz_html.IFRAME_VIOLATION in issues
    assert validate_mbz_html.HREF_VIOLATION in issues
    assert validate_mbz_html.STYLE_VIOLATION in issues
    assert validate_mbz_html.SCRIPT_VIOLATION in issues
    assert validate_mbz_html.MOODLE_VIOLATION in issues

    for location in locations:
        assert '/html/123.html' in location


def test_multiple_html_files_style_violation_in_each(
    tmp_path, mocker
):
    html_1 = '<p style="align: left>Content</p>'
    html_2 = '<iframe src="link">Content</iframe>'
    html_path = str(tmp_path) + "/html/"
    os.mkdir(html_path)
    file_path_1 = html_path + "123.html"
    file_path_2 = html_path + "456.html"

    with open(file_path_1, 'w') as f:
        f.write(html_1)
    with open(file_path_2, 'w') as f:
        f.write(html_2)

    output_filepath = f"{tmp_path}/test_output.csv"
    mocker.patch(
        "sys.argv",
        ["", html_path, output_filepath, "html"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(output_filepath))
    errors = [row for row in reader]
    issues = [row["issue"] for row in errors]
    locations = [row["location"] for row in errors]
    assert len(errors) == 2

    assert validate_mbz_html.IFRAME_VIOLATION in issues
    assert validate_mbz_html.STYLE_VIOLATION in issues

    for location in locations:
        assert ('/html/123.html' in location or '/html/456.html' in location)


def test_multiple_html_files_style_violations_ignored(
    tmp_path, mocker
):
    html = '<p style="left: allign">Content</p>'

    html_path = str(tmp_path) + "/html/"
    os.mkdir(html_path)
    file_path = html_path + "123.html"
    with open(file_path, 'w') as f:
        f.write(html)

    output_filepath = f"{tmp_path}/test_output.csv"
    mocker.patch(
        "sys.argv",
        ["", html_path, output_filepath, "html", "--no-style"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(output_filepath))
    errors = [row for row in reader]
    assert len(errors) == 0


def test_nested_html_directory_violations(
    tmp_path, mocker
):
    html_1 = '<p style="align: left>Content</p>'
    html_2 = '<iframe src="link">Content</iframe>'
    html_3 = '<script>javascript</script>'
    html_path = str(tmp_path) + "/html/"
    os.mkdir(html_path)
    file_path_1 = html_path + "123.html"
    html_subdir = html_path + "/subdir/"
    os.mkdir(html_subdir)
    file_path_2 = html_subdir + "456.html"
    html_subsubdir = html_subdir + "/subsubdir/"
    os.mkdir(html_subsubdir)
    file_path_3 = html_subsubdir + "789.html"

    with open(file_path_1, 'w') as f:
        f.write(html_1)
    with open(file_path_2, 'w') as f:
        f.write(html_2)
    with open(file_path_3, 'w') as f:
        f.write(html_3)

    output_filepath = f"{tmp_path}/test_output.csv"
    mocker.patch(
        "sys.argv",
        ["", html_path, output_filepath, "html"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(output_filepath))
    errors = [row for row in reader]
    issues = [row["issue"] for row in errors]
    locations = [row["location"] for row in errors]
    assert len(errors) == 3

    assert validate_mbz_html.IFRAME_VIOLATION in issues
    assert validate_mbz_html.STYLE_VIOLATION in issues
    assert validate_mbz_html.SCRIPT_VIOLATION in issues

    for location in locations:
        assert ('/html/123.html' in location or
                '/html/subdir/456.html' in location or
                '/html/subdir/subsubdir/789.html' in location
                )


def test_questions_uuid_validation(tmp_path, mocker,
                                   question_xml, mbz_builder):

    mbz_builder(tmp_path / "mbz", [])
    mbz_dir = f"{tmp_path}/mbz"
    fp = Path(mbz_dir) / "questions.xml"
    fp.write_text(question_xml)

    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}/mbz", f"{tmp_path}/test_output.csv", "mbz"]
    )
    validate_mbz_html.main()

    reader = csv.DictReader(open(tmp_path / "test_output.csv"))
    errors = [row for row in reader]

    assert {
        "issue": validate_mbz_html.INVALID_QBANK_UUID_VIOLATION,
        "location": f'{mbz_dir}/questions.xml',
        "link": "question id: 2 uuid: f79cdda5-8911-4f8b-8648-"
    } in errors
    assert {
        "issue": validate_mbz_html.DUPLICATE_QBANK_UUID_VIOLATION,
        "location": f'{mbz_dir}/questions.xml',
        "link": "question id: 3 uuid: f79cdda5-8911-4f8b-8648-47fb0e74ecb1"
    } in errors
    assert {
        "issue": validate_mbz_html.INVALID_QBANK_UUID_VIOLATION,
        "location": f'{mbz_dir}/questions.xml',
        "link": "question id: 4 uuid: $@NULL@$"
    } in errors


def test_inject_ib_uuids_duplicates_diff_files(tmp_path, mocker):
    html_1 = """
<div class="os-raise-ib-input"
data-content-id="7080c78d-298b-40ba-a68d-55d6a93b00fb">
</div>
"""
    html_2 = """
<div class="os-raise-ib-input"
data-content-id="7080c78d-298b-40ba-a68d-55d6a93b00fb">
</div>
    """.strip()

    html_path = str(tmp_path) + "/html"
    os.mkdir(html_path)
    file_path_1 = html_path + "/123.html"
    html_subdir = html_path + "/variant/"
    os.mkdir(html_subdir)
    file_path_2 = html_subdir + "456.html"

    with open(file_path_1, 'w') as f:
        f.write(html_1)
    with open(file_path_2, 'w') as f:
        f.write(html_2)

    output_filepath = f"{tmp_path}/test_output.csv"
    mocker.patch(
        "sys.argv",
        ["", html_path, output_filepath, "html"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(output_filepath))
    errors = [row for row in reader]
    issues = [row["issue"] for row in errors]
    locations = [row["location"] for row in errors]
    assert len(errors) == 1
    assert len(locations) == 1

    assert validate_mbz_html.DUPLICATE_IB_UUID_VIOLATION in issues
    assert '/html/123.html' in locations[0]
    assert '/html/variant/456.html' in locations[0]


def test_inject_ib_uuids_duplicates_same_file(tmp_path, mocker):
    html_1 = """
<div class="os-raise-ib-input"
data-content-id="7080c78d-298b-40ba-a68d-55d6a93b00fb">
</div>
<div class="os-raise-ib-input"
data-content-id="7080c78d-298b-40ba-a68d-55d6a93b00fb">
</div>
    """.strip()

    html_path = str(tmp_path) + "/html"
    os.mkdir(html_path)
    file_path_1 = html_path + "/123.html"

    with open(file_path_1, 'w') as f:
        f.write(html_1)

    output_filepath = f"{tmp_path}/test_output.csv"
    mocker.patch(
        "sys.argv",
        ["", html_path, output_filepath, "html"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(output_filepath))
    errors = [row for row in reader]
    issues = [row["issue"] for row in errors]
    locations = [row["location"] for row in errors]
    assert len(errors) == 1
    assert len(locations) == 1

    assert validate_mbz_html.DUPLICATE_IB_UUID_VIOLATION in issues
    assert locations[0].count('/html/123.html') == 2


def test_inject_ib_uuids_untagged(tmp_path, mocker):
    html_1 = """
<div class="os-raise-ib-input">
</div>
<div class="os-raise-ib-pset">
</div>
<div class="os-raise-ib-pset-problem">
</div>
    """.strip()

    html_path = str(tmp_path) + "/html"
    os.mkdir(html_path)
    file_path_1 = html_path + "/123.html"
    with open(file_path_1, 'w') as f:
        f.write(html_1)

    output_filepath = f"{tmp_path}/test_output.csv"
    mocker.patch(
        "sys.argv",
        ["", html_path, output_filepath, "html", "--uuids-populated"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(output_filepath))
    errors = [row for row in reader]
    issues = [row["issue"] for row in errors]
    locations = [row["location"] for row in errors]
    assert len(errors) == 3
    assert len(locations) == 3

    for i in issues:
        assert i == validate_mbz_html.MISSING_IB_UUID_VIOLATION

    for i in locations:
        assert '/html/123.html' in i


def test_inject_ib_uuids_pass(tmp_path, mocker):
    html_1 = """
<div class="os-raise-ib-input"
data-content-id="7080c78d-298b-40ba-a68d-55d6a93b00fb">
</div>
<div class="os-raise-ib-pset"
data-content-id="4567c78d-298b-40ba-a68d-55d6a93b0066">
</div>
<div class="os-raise-ib-pset-problem"
data-content-id="9967c78d-298b-40ba-a68d-55d6a93b0055">
</div>
    """.strip()

    html_path = str(tmp_path) + "/html"
    os.mkdir(html_path)
    file_path_1 = html_path + "/123.html"
    with open(file_path_1, 'w') as f:
        f.write(html_1)

    output_filepath = f"{tmp_path}/test_output.csv"
    mocker.patch(
        "sys.argv",
        ["", html_path, output_filepath, "html"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(output_filepath))
    errors = [row for row in reader]
    assert len(errors) == 0


def test_inject_ib_uuids_diff_files_pass(tmp_path, mocker):
    html_1 = """
<div class="os-raise-ib-input"
data-content-id="7080c78d-298b-40ba-a68d-55d6a93b00fb">
</div>
    """
    html_2 = """
<div class="os-raise-ib-pset"
data-content-id="4567c78d-298b-40ba-a68d-55d6a93b0066">
</div>
    """
    html_3 = """
<div class="os-raise-ib-pset-problem"
data-content-id="9967c78d-298b-40ba-a68d-55d6a93b0055">
</div>
    """.strip()
    html_path = str(tmp_path) + "/html"
    os.mkdir(html_path)
    file_path_1 = html_path + "/123.html"
    html_subdir = html_path + "/variant/"
    os.mkdir(html_subdir)
    file_path_2 = html_subdir + "456.html"
    file_path_3 = html_subdir + "789.html"

    with open(file_path_1, 'w') as f:
        f.write(html_1)
    with open(file_path_2, 'w') as f:
        f.write(html_2)
    with open(file_path_3, 'w') as f:
        f.write(html_3)

    output_filepath = f"{tmp_path}/test_output.csv"
    mocker.patch(
        "sys.argv",
        ["", html_path, output_filepath, "html"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(output_filepath))
    errors = [row for row in reader]
    assert len(errors) == 0


def test_inject_ib_uuids_invalid(tmp_path, mocker):
    html = """
<div class="os-raise-ib-input"
data-content-id="7080c78d-298b-40ba-a68d-55d6a93b00fbextra">
</div>
    """.strip()

    html_path = str(tmp_path) + "/html"
    os.mkdir(html_path)
    file_path = html_path + "/123.html"
    with open(file_path, 'w') as f:
        f.write(html)

    output_filepath = f"{tmp_path}/test_output.csv"
    mocker.patch(
        "sys.argv",
        ["", html_path, output_filepath, "html"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(output_filepath))
    errors = [row for row in reader]
    assert len(errors) == 1

    assert errors[0]["issue"] == validate_mbz_html.INVALID_IB_UUID_VIOLATION

    assert errors[0]["location"] == file_path


def test_table_valid(tmp_path, mocker):
    html = """
<table class="os-raise-doubleheadertable">
  <thead>
    <tr>
      <th scope="col"></th>
      <th scope="col">\\({x}\\)</th>
      <th scope="col">\\(+7\\)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">\\({x}\\)</th>
      <td>\\({x^2}\\)</td>
      <td><p class="something"></p></td>
    </tr>
    <tr>
      <th scope="row">\\(+9\\)</th>
      <td>\\(9x\\)</td>
      <td>\\(63\\)</td>
    </tr>
  </tbody>
</table>
""".strip()

    html_path = str(tmp_path) + "/html"
    os.mkdir(html_path)
    file_path = html_path + "/123.html"
    with open(file_path, 'w') as f:
        f.write(html)

    output_filepath = f"{tmp_path}/test_output.csv"
    mocker.patch(
        "sys.argv",
        ["", html_path, output_filepath, "html"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(output_filepath))
    errors = [row for row in reader]
    assert len(errors) == 0


def test_table_invalid(tmp_path, mocker):
    html = """
<table invalid_attribute="Invalid">
    <caption>caption</caption>

    <tr>
      <th>Time (years)</th>
      <td>5</td>
      <td>1</td>
      <td>0</td>
      <td>-1</td>
      <td>-2</td>
    </tr>
    <tbody>
    <tr>
      <th scope="col">Volume of Coral (cubic centimeters)</th>
      <td>a.___</td>
      <td>b.___</td>
      <td>c.___</td>
      <td>d.___</td>
      <td>e.___</td>
    </tr>
    </tbody>
</table>  """.strip()

    html_path = str(tmp_path) + "/html"
    os.mkdir(html_path)
    file_path = html_path + "/123.html"
    with open(file_path, 'w') as f:
        f.write(html)

    output_filepath = f"{tmp_path}/test_output.csv"
    mocker.patch(
        "sys.argv",
        ["", html_path, output_filepath, "html"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(output_filepath))
    errors = [row for row in reader]
    assert len(errors) == 5
    assert errors[0]["issue"] == validate_mbz_html.TABLE_VIOLATION + \
        "table is missing a class attribute"

    assert errors[0]["location"] == file_path
    assert errors[1]["issue"] == validate_mbz_html.TABLE_VIOLATION + \
        "table has invalid attribute invalid_attribute"
    assert errors[1]["location"] == file_path
    assert errors[2]["issue"] == validate_mbz_html.TABLE_VIOLATION + \
        "thead missing in table"
    assert errors[2]["location"] == file_path
    assert errors[3]["issue"] == validate_mbz_html.TABLE_VIOLATION + \
        "tr is not allowed as direct child of table"
    assert errors[3]["location"] == file_path


def test_table_invalid_doubleheadertable(tmp_path, mocker):
    html = """
        <table class="os-raise-doubleheadertable">
        <thead>
            <tr>
            <th ></th>
            <th scope="col">\\(x\\)</th>
            <th scope="col">\\(+7\\)</th>
            </tr>
        </thead>
        <tbody>
            <invalid_tr></invalid_tr>
            <tr>
            <td>\\(x^2\\)</td>
            <td>\\(7x\\)</td>
            </tr>
            <tr>
            <td>\\(9x\\)</td>
            <td>\\(63\\)</td>
            </tr>
        </tbody>
        </table>
       """.strip()

    html_path = str(tmp_path) + "/html"
    os.mkdir(html_path)
    file_path = html_path + "/123.html"
    with open(file_path, 'w') as f:
        f.write(html)

    output_filepath = f"{tmp_path}/test_output.csv"
    mocker.patch(
        "sys.argv",
        ["", html_path, output_filepath, "html"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(output_filepath))
    errors = [row for row in reader]
    assert len(errors) == 3
    assert errors[0]["issue"] == validate_mbz_html.TABLE_VIOLATION + \
        "doubleheadertable requires th in both thead and tbody"
    assert errors[0]["location"] == file_path
    assert errors[1]["issue"] == validate_mbz_html.TABLE_VIOLATION + \
        "must include scope attribute in thead th with value col"
    assert errors[1]["location"] == file_path
    assert errors[2]["issue"] == validate_mbz_html.TABLE_VIOLATION + \
        "invalid_tr is not allowed as child of tbody"
    assert errors[2]["location"] == file_path


def test_table_invalid_elements(tmp_path, mocker):
    html = """
<table class="os-raise-textheavytable">
  <thead>
  <invalid_thead></invalid_thead>
    <tr>
      <invalid_th></invalid_th>

    </tr>
  </thead>
  <invalid_tr></invalid_tr>
    <tr>
      <invalid_td></invalid_td>
      <th scope="row">\\(x\\)</th>
      <td>\\(x^2\\)</td>
      <td>\\(7x\\)</td>
    </tr>
    <tr>
      <th scope="row">\\(+9\\)</th>
      <td>\\(9x\\)</td>
      <td>\\(63\\)</td>
    </tr>
</table>
    """.strip()

    html_path = str(tmp_path) + "/html"
    os.mkdir(html_path)
    file_path = html_path + "/123.html"
    with open(file_path, 'w') as f:
        f.write(html)

    output_filepath = f"{tmp_path}/test_output.csv"
    mocker.patch(
        "sys.argv",
        ["", html_path, output_filepath, "html"]
    )

    validate_mbz_html.main()

    reader = csv.DictReader(open(output_filepath))
    errors = [row for row in reader]
    assert len(errors) == 7

    assert errors[0]["issue"] == validate_mbz_html.TABLE_VIOLATION + \
        "tbody missing in table"
    assert errors[0]["location"] == file_path
    assert errors[1]["issue"] == validate_mbz_html.TABLE_VIOLATION + \
        "invalid_tr is not allowed as direct child of table"
    assert errors[1]["location"] == file_path
    assert errors[2]["issue"] == validate_mbz_html.TABLE_VIOLATION + \
        "tr is not allowed as direct child of table"
    assert errors[2]["location"] == file_path
    assert errors[3]["issue"] == validate_mbz_html.TABLE_VIOLATION + \
        "tr is not allowed as direct child of table"
    assert errors[3]["location"] == file_path
    assert errors[4]["issue"] == validate_mbz_html.TABLE_VIOLATION + \
        "th is required in either thead or tbody"
    assert errors[4]["location"] == file_path
    assert errors[5]["issue"] == validate_mbz_html.TABLE_VIOLATION + \
        "invalid_thead is not allowed as child of thead"
    assert errors[5]["location"] == file_path
    assert errors[6]["issue"] == validate_mbz_html.TABLE_VIOLATION + \
        "invalid_th is not allowed as child of tr"
    assert errors[6]["location"] == file_path


def test_duplicate_content_uuids(
    tmp_path, page_builder, lesson_builder, mbz_builder
):
    html_content_with_id = """
    <div
      class="os-raise-content"
      data-content-id="26d5d10b-1ce2-4dcc-960f-43c424c93629">
    </div>
    """

    lesson1 = lesson_builder(
        id=1,
        name="Lesson 1",
        pages=[
            {
                "id": 11,
                "title": "Lesson 1 Page 1",
                "html_content": html_content_with_id
            },
            {
                "id": 12,
                "title": "Lesson 1 Page 2",
                "html_content": "<p>Some unextracted content</p>",
                "answers": [
                    {
                        "id": 111,
                        "html_content": "<p>Foobar</p>",
                        "response": "<p>Foobar</p>"
                    },
                    {
                        "id": 112,
                        "html_content": "<p>Foobar</p>",
                        "response": "<p>Foobar</p>"
                    }
                ]
            }
        ]
    )
    page2 = page_builder(
        id=2, name="Page 2", html_content=html_content_with_id
    )
    mbz_path = tmp_path / "mbz"
    html_path = tmp_path / "html"
    html_path.mkdir()

    mbz_builder(mbz_path, activities=[lesson1, page2])

    violations = validate_mbz_html.validate_mbz(mbz_path)

    assert len(violations) == 1
    violation = violations[0]
    assert violation.issue == \
        validate_mbz_html.DUPLICATE_CONTENT_UUID_VIOLATION
    assert violation.location == "Page 2"
    assert violation.link == "26d5d10b-1ce2-4dcc-960f-43c424c93629"


def test_extracted_corruption(
    tmp_path, page_builder, mbz_builder
):
    multiple_fragments = """
    <div
      class="os-raise-content"
      data-content-id="26d5d10b-1ce2-4dcc-960f-43c424c93629">
    </div>
    <p>I shouldn't be here</p>
    """

    inner_text = """
    <div
      class="os-raise-content"
      data-content-id="26d5d10b-1ce2-4dcc-960f-43c424c93628">
      I shouldn't be here
    </div>
    """

    inner_element = """
    <div
      class="os-raise-content"
      data-content-id="26d5d10b-1ce2-4dcc-960f-43c424c93627">
      <p>I shouldn't be here</p>
    </div>
    """

    valid_extracted = """
    <div
      class="os-raise-content"
      data-content-id="26d5d10b-1ce2-4dcc-960f-43c424c93626"></div>
    """

    page1 = page_builder(
        id=1, name="Page 1", html_content=multiple_fragments
    )
    page2 = page_builder(
        id=2, name="Page 2", html_content=inner_text
    )
    page3 = page_builder(
        id=3, name="Page 3", html_content=inner_element
    )
    page4 = page_builder(
        id=4, name="Page 4", html_content=valid_extracted
    )
    mbz_path = tmp_path / "mbz"
    html_path = tmp_path / "html"
    html_path.mkdir()

    mbz_builder(mbz_path, activities=[page1, page2, page3, page4])

    violations = validate_mbz_html.validate_mbz(mbz_path)

    assert len(violations) == 3
    for violation in violations:
        assert violation.issue == \
            validate_mbz_html.EXTRACTED_HTML_CORRUPTION_VIOLATION
    assert violations[0].location == "Page 1"
    assert violations[0].link == "26d5d10b-1ce2-4dcc-960f-43c424c93629"
    assert violations[1].location == "Page 2"
    assert violations[1].link == "26d5d10b-1ce2-4dcc-960f-43c424c93628"
    assert violations[2].location == "Page 3"
    assert violations[2].link == "26d5d10b-1ce2-4dcc-960f-43c424c93627"
