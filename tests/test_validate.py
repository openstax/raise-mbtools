import csv
import pytest
import html
from lxml import etree
from mbtools import validate_mbz_html
from mbtools.models import MoodleHtmlElement
from collections import defaultdict

IM_MEDIA_LINK = "https://s3.amazonaws.com/im-ims-export/imagename"
OSX_MEDIA_LINK = "https://s3.amazonaws.com/im-ims-export/l1/imagename"
MOODLE_VIDEO_FILE = "@@PLUGINFILE@@/video.mp4"
MOODLE_TRACK_FILE = "@@PLUGINFILE@@/video.vtt"
LESSON_ANSW_ILLUSTRATION = "https://s3.amazonaws.com/im-ims-export/la1"
QUESTION1_ILLUSTRATION = "https://s3.amazonaws.com/im-ims-export/q1"
QUESTION2_ILLUSTRATION = "https://s3.amazonaws.com/im-ims-export/q2"
QUESTION3_ILLUSTRATION = "https://s3.amazonaws.com/im-ims-export/q3"
ANSWER1_ILLUSTRATION = "https://s3.amazonaws.com/im-ims-export/answer1"
ANSWER2_ILLUSTRATION = "https://s3.amazonaws.com/im-ims-export/answer2"
ADDITIONAL_MEDIA = "https://wikipedia.com/brazil/image1"
ADDITIONAL_MEDIA2 = "https://wikipedia.com/brazil/image2"
ADDITIONAL_MEDIA3 = "https://wikipedia.com/brazil/image3"
ADDITIONAL_MEDIA4 = "https://wikipedia.com/brazil/image4"

VIOLATION_HASHMAP = {validate_mbz_html.STYLE_VIOLATION: 7,
                     validate_mbz_html.SOURCE_VIOLATION: 2,
                     validate_mbz_html.SCRIPT_VIOLATION: 3,
                     validate_mbz_html.IFRAME_VIOLATION: 1,
                     validate_mbz_html.MOODLE_VIOLATION: 2,
                     validate_mbz_html.HREF_VIOLATION: 1}

VIOLATION_LINK_HASHMAP = {None: 3,
                          MOODLE_VIDEO_FILE: 1,
                          MOODLE_TRACK_FILE: 1,
                          ADDITIONAL_MEDIA: 1,
                          ADDITIONAL_MEDIA2: 1,
                          ADDITIONAL_MEDIA3: 1,
                          ADDITIONAL_MEDIA4: 1,
                          "color: blue": 1,
                          "text-align: left; color: red;": 1,
                          "text-align: left": 1,
                          "color: green": 1,
                          "color: grey": 1,
                          "color: orange": 1,
                          "text-align: center": 1}

LESSON1_CONTENT1 = (
    '<div>'
    '<div>'
    # Style Violation 1
    f'<img style="color: orange" src="{IM_MEDIA_LINK}">'
    # Source Violation 1
    f'<img src="{ADDITIONAL_MEDIA}">'
    '</div>'
    '</div>'
)
LESSON1_CONTENT2 = (
    '<div>'
    f'<img src="{OSX_MEDIA_LINK}">'
    '</div>'
    # Script Violation 1
    '<script>'
    'var something = 0'
    '</script>'
)
LESSON_ANSWER1 = (
    # Style Violation 2
    '<p dir="ltr" style="color: blue">'
    '(6, 0)'
    '<br>'
    '</p>'
    # Style Violation 3
    '<p style="text-align: left">'
    'words'
    '</p>'
    # Style Violation 4
    '<p style="text-align: center">'
    'words'
    '</p>'
)
LESSON_ANSWER2 = (
    '<p dir="ltr">'
    # Style Violation 5
    '<img alt="Answer Picture" height="71" role="image" '
    f'src="{LESSON_ANSW_ILLUSTRATION}" title="question" style="color: grey"'
    ' width="101">'
    '<br>'
    '</p>'
)
LESSON_ANSWER3 = (
    # Style Violation 6
    '<p dir="ltr" style="text-align: left; color: red;">'
    '(3, 2)'
    '<br>'
    '</p>'
)
PAGE2_CONTENT = (
    '<div>'
    '<video controls="true">'
    # Moodle Violation 1
    f'<source src="{MOODLE_VIDEO_FILE}">'
    # Moodle Violation 2
    f'<track src="{MOODLE_TRACK_FILE}">'
    f'<track src="{ADDITIONAL_MEDIA2}">'
    'fallback content'
    '</video>'
    # Source Violation 2
    f'<a href="{ADDITIONAL_MEDIA3}">'
    '</a>'
    # Script Violation 2
    '<script>var variable=0'
    '</script>'
    '</div>'
    # Style Violaiton 7
    '<div style="color: green">'
    'some text'
    '</div>'
)
PAGE2_INVALID_CONTENT = (
    'Invalid Content Before'
    '<p>Valid content</p>'
    'Invalid Content Between'
    '<p style="color: green">some text</p>'
    'Invalid Content After'
)
QUESTION1_CONTENT = (
    '<div>'
    '<p>'
    'What is the capital of Brazil'
    '</p>'
    '<div>'
    '<img alt="A picture of a map of Brazil" height="71" role="image" '
    f'src="{QUESTION1_ILLUSTRATION}" title="question" width="202">'
    '</div>'
    '<p>'
    'Select <strong>all</strong> statements that must be true.'
    '</p>'
    '</div>'
)
QUESTION2_CONTENT = (
    '<div>'
    '<p>'
    'Write 10 pages on the colonization of Brazil'
    '</p>'
    '<div>'
    '<img alt="A picture of a map of Brazil" height="71" role="image" '
    f'src="{QUESTION2_ILLUSTRATION}" title="question" width="202">'
    '</div>'
    '<p>'
    'Select <strong>all</strong> statements that must be true.'
    '</p>'
    '</div>'
)
QUESTION3_CONTENT = (
    '<div>'
    '<p>'
    'Draw and submit a picture of Brazil'
    '</p>'
    '<div>'
    '<img alt="A picture of a map of Brazil" height="71" role="image" '
    f'src="{QUESTION3_ILLUSTRATION}" title="question" width="202">'
    '</div>'
    # Script Violation 3
    '<script>'
    'var variable=0'
    '</script>'
    '<p>'
    'Select <strong>all</strong> statements that must be true.'
    '</p>'
    '</div>'
)
ANSWER1_CONTENT = (
    '<div>'
    '<p>'
    'Brasilia'
    '</p>'
    '<img alt="A Picture of Brasilia" height="71" role="image" '
    f'src="{ANSWER1_ILLUSTRATION}" title="answer1" width="101">'
    f'<iframe src="{ADDITIONAL_MEDIA4}">A SINGLE IFRAME'
    '</iframe>'
    '</div>'
)
ANSWER2_CONTENT = (
    '<div>'
    '<p>'
    'Rio de Janiero'
    '</p>'
    '<img alt="A picture of Rio De Janiero" height="71" role="image" '
    f'src="{ANSWER2_ILLUSTRATION}" title="answer2" width="101">'
    '</div>'
)

BACK_XML_CONTENT = """
    <?xml version="1.0" encoding="UTF-8"?>
    <moodle_backup>
        <contents>
        <activities>
            <activity>
                <modulename>lesson</modulename>
                <title>First Lesson: 1.1</title>
                <directory>activities/lesson_1</directory>
            </activity>
            <activity>
                <modulename>page</modulename>
                <title>Second Lesson: 2.1</title>
                <directory>activities/page_2</directory>
            </activity>
            <activity>
                <modulename>quiz</modulename>
                <title>Third Lesson: 3.1</title>
                <directory>activities/quiz_3</directory>
            </activity>
        </activities>
        </contents>
    </moodle_backup>
""".strip()

LESSON1_CONTENT = f"""
    <?xml version="1.0" encoding="UTF-8"?>
    <activity id="1" modulename="lesson">
        <lesson id="1">
            <name>First Lesson: 1.1</name>
            <pages>
                <page id="3">
                    <title>First Lession: 1.1 - lesson.xml</title>
                    <contents>{html.escape(LESSON1_CONTENT1)}</contents>
                    <answers>
                        <answer_text>{html.escape(LESSON_ANSWER1)}</answer_text>
                        <answer_text>{html.escape(LESSON_ANSWER2)}</answer_text>
                    </answers>
                </page>
                <page id="4">
                    <title>Second Lession: 2.1 - lesson.xml</title>
                    <contents>{html.escape(LESSON1_CONTENT2)}</contents>
                    <answers>
                        <answer_text>{html.escape(LESSON_ANSWER3)}</answer_text>
                    </answers>
                </page>
            </pages>
        </lesson>
    </activity>
""".strip()

PAGE2_CONTENT = f"""
<?xml version="1.0" encoding="UTF-8"?>
<activity id="2" modulename="page">
    <page id="2">
        <name>Page 2 - A Special Activity</name>
        <content>{html.escape(PAGE2_CONTENT)}</content>
    </page>
</activity>
""".strip()

PAGE2_INVALID_CONTENT = f"""
<?xml version="1.0" encoding="UTF-8"?>
<activity id="2" modulename="page">
    <page id="2">
        <name>Page 2 - A Special Activity</name>
        <content>{html.escape(PAGE2_INVALID_CONTENT)}</content>
    </page>
</activity>
""".strip()

QUIZ3_CONTENT = """
    <?xml version="1.0" encoding="UTF-8"?>
    <activity id="3" modulename="quiz">
        <quiz id="1">
            <name>Fist Example Quiz</name>
            <question_instances>
                <question_instance id="1">
                    <questionid>1</questionid>
                </question_instance>
                <question_instance id ="2">
                    <questionid>2</questionid>
                </question_instance>
            </question_instances>
        </quiz>
        <quiz id="2">
            <name>Second Example Quiz</name>
            <question_instances>
                <question_instance id="3">
                    <questionid>3</questionid>
                </question_instance>
            </question_instances>
        </quiz>
    </activity>
""".strip()

QUESTION_CONTENT = f"""
<?xml version="1.0" encoding="UTF-8"?>
<question_categories>
    <question_category id="1">
        <name>Quiz Bank 'Algebra1.1 Check Your Readiness'</name>
        <questions>
            <question id="1">
            <questiontext>{html.escape(QUESTION1_CONTENT)}</questiontext>
            <answers>
                <answer id="1">
                <answertext>{html.escape(ANSWER1_CONTENT)}</answertext>
                </answer>
                <answer id="2">
                <answertext>{html.escape(ANSWER2_CONTENT)}</answertext>
                </answer>
            </answers>
            </question>
            <question id="2">
            <questiontext>{html.escape(QUESTION2_CONTENT)}</questiontext>
            </question>
            <question id="3">
            <questiontext>{html.escape(QUESTION3_CONTENT)}</questiontext>
            </question>
        </questions>
    </question_category>
</question_categories>
""".strip()


@pytest.fixture
def mbz_path(tmp_path):
    (tmp_path / "moodle_backup.xml").write_text(BACK_XML_CONTENT)

    lesson1_dir = tmp_path / "activities/lesson_1"
    lesson1_dir.mkdir(parents=True)
    (lesson1_dir / "lesson.xml").write_text(LESSON1_CONTENT)

    page2_dir = tmp_path / "activities/page_2"
    page2_dir.mkdir(parents=True)
    (page2_dir / "page.xml").write_text(PAGE2_CONTENT)

    quiz3_dir = tmp_path / "activities/quiz_3"
    quiz3_dir.mkdir(parents=True)
    (quiz3_dir / "quiz.xml").write_text(QUIZ3_CONTENT)

    (tmp_path / "questions.xml").write_text(QUESTION_CONTENT)
    return tmp_path


@pytest.fixture
def mbz_invalid_html(tmp_path):
    (tmp_path / "moodle_backup.xml").write_text(BACK_XML_CONTENT)

    lesson1_dir = tmp_path / "activities/lesson_1"
    lesson1_dir.mkdir(parents=True)
    (lesson1_dir / "lesson.xml").write_text(LESSON1_CONTENT)

    page2_dir = tmp_path / "activities/page_2"
    page2_dir.mkdir(parents=True)
    (page2_dir / "page.xml").write_text(PAGE2_INVALID_CONTENT)

    quiz3_dir = tmp_path / "activities/quiz_3"
    quiz3_dir.mkdir(parents=True)
    (quiz3_dir / "quiz.xml").write_text(QUIZ3_CONTENT)

    (tmp_path / "questions.xml").write_text(QUESTION_CONTENT)
    return tmp_path


def test_validate_all(mbz_path):
    violations = validate_mbz_html.validate_mbz(mbz_path)
    violations_map = defaultdict(lambda: 0)
    violations_link_map = defaultdict(lambda: 0)
    for v in violations:
        violations_map[v.issue] += 1
        violations_link_map[v.link] += 1
    assert VIOLATION_HASHMAP == violations_map
    assert VIOLATION_LINK_HASHMAP == violations_link_map


def test_validate_output_file(mbz_path, mocker, tmp_path):
    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}", f"{tmp_path}/test_output.csv"]
    )
    validate_mbz_html.main()
    with open(f"{tmp_path}/test_output.csv", 'r') as f:
        violations = csv.reader(f, delimiter=",")
        next(violations)
        violation_map = defaultdict(lambda: 0)
        violation_descriptions = defaultdict(lambda: 0)
        for row in violations:
            violation_map[row[0]] += 1
            link = (None if row[2] == '' else row[2])
            violation_descriptions[link] += 1
        assert VIOLATION_HASHMAP == violation_map
        assert VIOLATION_LINK_HASHMAP == violation_descriptions


def test_erroneous_output_file(mbz_invalid_html, mocker, tmp_path):
    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}", f"{tmp_path}/test_output.csv"]
    )
    validate_mbz_html.main()
    with open(f"{tmp_path}/test_output.csv", 'r') as f:
        violations = csv.reader(f, delimiter=",")
        next(violations)
        violation_map = defaultdict(lambda: 0)
        violation_descriptions = defaultdict(lambda: 0)
        for row in violations:
            violation_map[row[0]] += 1
            link = (None if row[2] == '' else row[2])
            violation_descriptions[link] += 1
        assert {validate_mbz_html.UNNESTED_VIOLATION: 3} == violation_map
        assert {'Invalid Content Before': 1,
                'Invalid Content Between': 1,
                'Invalid Content After': 1} == violation_descriptions


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
    assert style_violations[0].html == '<p style="left: allign">html</p>'
    assert style_violations[0].location == "here"


def test_href_violaiton():
    location = "here"
    parent = etree.fromstring("<content></content>")
    parent.text = '<a href="something">html</a>'
    elem = MoodleHtmlElement(parent, location)
    style_violations = validate_mbz_html.find_tag_violations([elem])
    assert len(style_violations) == 1
    assert style_violations[0].issue == validate_mbz_html.HREF_VIOLATION
    assert style_violations[0].link == "something"
    assert style_violations[0].html == '<a href="something">html</a>'
    assert style_violations[0].location == "here"


def test_script_violaiton():
    location = "here"
    parent = etree.fromstring("<content></content>")
    parent.text = '<script>javascript</script>'
    elem = MoodleHtmlElement(parent, location)
    style_violations = validate_mbz_html.find_tag_violations([elem])
    assert len(style_violations) == 1
    assert style_violations[0].issue == validate_mbz_html.SCRIPT_VIOLATION
    assert style_violations[0].link is None
    assert style_violations[0].html == '<script>javascript</script>'
    assert style_violations[0].location == "here"


def test_iframe_violaiton():
    location = "here"
    parent = etree.fromstring("<content></content>")
    parent.text = '<iframe src="link">something</iframe>'
    elem = MoodleHtmlElement(parent, location)
    style_violations = validate_mbz_html.find_tag_violations([elem])
    assert len(style_violations) == 1
    assert style_violations[0].issue == validate_mbz_html.IFRAME_VIOLATION
    assert style_violations[0].link == "link"
    assert style_violations[0].html == '<iframe src="link">something</iframe>'
    assert style_violations[0].location == "here"


def test_source_violaiton():
    location = "here"
    parent = etree.fromstring("<content></content>")
    parent.text = '<img src="link">'
    elem = MoodleHtmlElement(parent, location)
    style_violations = validate_mbz_html.find_source_violations([elem])
    assert len(style_violations) == 1
    assert style_violations[0].issue == validate_mbz_html.SOURCE_VIOLATION
    assert style_violations[0].link == "link"
    assert style_violations[0].html == '<img src="link">'
    assert style_violations[0].location == "here"
