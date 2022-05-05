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
    # Unnested Violation 1
    'Bad Content'
)
LESSON_ANSWER2 = (
    '<p dir="ltr">'
    '<img alt="Answer Picture" height="71" role="image" '
    f'src="{LESSON_ANSW_ILLUSTRATION}" title="question" style="color: grey"'
    ' width="101">'
    '<br>'
    '</p>'
)
LESSON_ANSWER3 = (
    # Style Violation 5
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
    # Style Violaiton 6
    '<div style="color: green">'
    'some text'
    '</div>'
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


@pytest.fixture
def mbz_path(tmp_path):
    back_xml_content = """
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
    (tmp_path / "moodle_backup.xml").write_text(back_xml_content)

    lesson1_content = f"""
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
    lesson1_dir = tmp_path / "activities/lesson_1"
    lesson1_dir.mkdir(parents=True)
    (lesson1_dir / "lesson.xml").write_text(lesson1_content)

    page2_content = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <activity id="2" modulename="page">
            <page id="2">
                <name>Page 2 - A Special Activity</name>
                <content>{html.escape(PAGE2_CONTENT)}</content>
            </page>
        </activity>
    """.strip()
    page2_dir = tmp_path / "activities/page_2"
    page2_dir.mkdir(parents=True)
    (page2_dir / "page.xml").write_text(page2_content)

    quiz3_content = """
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
    quiz3_dir = tmp_path / "activities/quiz_3"
    quiz3_dir.mkdir(parents=True)
    (quiz3_dir / "quiz.xml").write_text(quiz3_content)

    question_content = f"""
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
    (tmp_path / "questions.xml").write_text(question_content)

    return tmp_path


def test_validate_all(mbz_path):
    violations = validate_mbz_html.validate_mbz(mbz_path)
    violation_names = [x.issue for x in violations]
    assert set([validate_mbz_html.STYLE_VIOLATION,
                validate_mbz_html.STYLE_VIOLATION,
                validate_mbz_html.SOURCE_VIOLATION,
                validate_mbz_html.SOURCE_VIOLATION,
                validate_mbz_html.SCRIPT_VIOLATION,
                validate_mbz_html.SCRIPT_VIOLATION,
                validate_mbz_html.IFRAME_VIOLATION,
                validate_mbz_html.MOODLE_VIOLATION,
                validate_mbz_html.MOODLE_VIOLATION,
                validate_mbz_html.HREF_VIOLATION]) == set(violation_names)


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
            violation_descriptions[row[2]] += 1

        hash_map = {validate_mbz_html.UNNESTED_VIOLATION: 1,
                    validate_mbz_html.STYLE_VIOLATION: 6,
                    validate_mbz_html.SOURCE_VIOLATION: 2,
                    validate_mbz_html.SCRIPT_VIOLATION: 3,
                    validate_mbz_html.IFRAME_VIOLATION: 1,
                    validate_mbz_html.MOODLE_VIOLATION: 2,
                    validate_mbz_html.HREF_VIOLATION: 1}
        assert hash_map == violation_map

        description_map = {'': 3,
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
                           "text-align: center": 1,
                           "Bad Content": 1}
        assert description_map == violation_descriptions


def test_string_without_html():
    location = "here"
    parent = etree.fromstring("<content></content>")
    parent.text = "Hi hello<p>actual_html</p>"
    elem = MoodleHtmlElement(parent, location)
    assert (elem.tostring() == "<p>Hi hello</p><p>actual_html</p>")
    assert len(elem.etree_fragments) == 2


def test_unnested_content():
    location = "here"
    parent = etree.fromstring("<content></content>")
    parent.text = "Hi hello<p>actual_html</p>"
    elem = MoodleHtmlElement(parent, location)
    violations = validate_mbz_html.find_unnested_violations([elem])
    assert len(violations) == 1
