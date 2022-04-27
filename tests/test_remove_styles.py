import pytest
import html
from mbtools import remove_styles
from lxml import etree
from mbtools.models import MoodleHtmlElement

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
    f'<img src="{IM_MEDIA_LINK}">'
    f'<img src="{ADDITIONAL_MEDIA}">'
    '</div>'
    '</div>'
)
LESSON1_CONTENT2 = (
    '<div>'
    f'<img src="{OSX_MEDIA_LINK}">'
    '</div>'
)
LESSON_ANSWER1 = (
    '<p dir="ltr" style="text-align: left; color=blue; font-size: 10px">'
    '(6, 0)'
    '<br>'
    '</p>'
)
LESSON_ANSWER2 = (
    '<p dir="ltr">'
    '<img alt="Answer Picture" height="71" role="image" '
    f'src="{LESSON_ANSW_ILLUSTRATION}" title="question" width="101">'
    '<br>'
    '</p>'
)
LESSON_ANSWER3 = (
    '<p dir="ltr" style="text-align: left; color= red;">'
    '(3, 2)'
    '<br>'
    '</p>'
)
PAGE2_CONTENT = (
    '<div>'
    '<video style="border: 5px" :controls="true">'
    f'<source src="{MOODLE_VIDEO_FILE}">'
    f'<track src="{MOODLE_TRACK_FILE}">'
    f'<track src="{ADDITIONAL_MEDIA2}">'
    'fallback content'
    '</video>'
    f'<a href="{ADDITIONAL_MEDIA3}">'
    '</a>'
    '<script>var variable=0'
    '</script>'
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
    '<p style="border: 5px">'
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
    '<script>var variable=0'
    '</script>'
    '<p style="border: 5px">'
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
    '<p style="border: 5px">'
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


def test_remove_styles_from_main(mbz_path, tmp_path, mocker):
    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}"]
    )
    remove_styles.main()
    with open(f"{tmp_path}/activities/lesson_1/lesson.xml", 'r') as f:
        file = f.read()
        assert ('style' not in file)
    with open(f"{tmp_path}/activities/page_2/page.xml", 'r') as f:
        file = f.read()
        assert ('style' not in file)


def test_styles_removed_from_html():
    location = "here"
    parent = etree.fromstring("<content></content>")
    parent.text = (
        '<p dir="ltr" style="color: blue">'
        '(6, 0)'
        '<br>'
        '</p>'
        '<p style="text-align: left">'
        'words'
        '</p>'
        '<p style="text-align: center">'
        'words'
        '</p>'
    )
    elem = MoodleHtmlElement(parent, location)
    elem.remove_attr("style")
    assert (elem.tostring() == (
            '<p dir="ltr">'
            '(6, 0)'
            '<br>'
            '</p>'
            '<p>'
            'words'
            '</p>'
            '<p>'
            'words'
            '</p>'))
    assert len(elem.etree_fragments) == 3
