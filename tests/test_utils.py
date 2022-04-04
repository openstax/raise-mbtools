from xml.dom import NotFoundErr
import pytest
import html
from mbtools import utils


IM_MEDIA_LINK = "https://s3.amazonaws.com/im-ims-export/imagename"
OSX_MEDIA_LINK = "https://osx-int-alg.s3.us-east-1.amazonaws.com/l1/imagename"
MOODLE_VIDEO_FILE = "@@PLUGINFILE@@/video.mp4"
MOODLE_TRACK_FILE = "@@PLUGINFILE@@/video.vtt"
LESSON_ANSW_ILLUSTRATION = "https://osx-int-alg.s3.us-east-1.amazonaws.com/la1"
QUESTION1_ILLUSTRATION = "https://osx-int-alg.s3.us-east-1.amazonaws.com/q1"
QUESTION2_ILLUSTRATION = "https://osx-int-alg.s3.us-east-1.amazonaws.com/q2"
QUESTION3_ILLUSTRATION = "https://osx-int-alg.s3.us-east-1.amazonaws.com/q3"
ANSWER1_ILLUSTRATION = "https://osx-int-alg.s3.us-east-1.amazonaws.com/answer1"
ANSWER2_ILLUSTRATION = "https://osx-int-alg.s3.us-east-1.amazonaws.com/answer2"

LESSON1_CONTENT1 = (
    '<div>'
    f'<img src="{IM_MEDIA_LINK}">'
    '<img src="https://validsite/imagename">'
    '</div>'
)
LESSON1_CONTENT2 = (
    '<div>'
    f'<img src="{OSX_MEDIA_LINK}">'
    '</div>'
)
LESSON_ANSWER1 = (
    '<p dir="ltr" style="text-align: left;">'
    '(6, 0)'
    '<br>'
    '</p>'
)
LESSON_ANSWER2 = (
    '<p dir="ltr" style="text-align: left;">'
    '<img alt="Answer Picture" height="71" role="image" '
    f'src="{LESSON_ANSW_ILLUSTRATION}" title="question" width="101">'
    '<br>'
    '</p>'
)
PAGE2_CONTENT = (
    '<div>'
    '<video controls="true">'
    f'<source src="{MOODLE_VIDEO_FILE}">'
    f'<track src="{MOODLE_TRACK_FILE}">'
    '<track src="https://validsite/video.vtt">'
    'fallback content'
    '</video>'
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
                            <answer_text>{html.escape(LESSON_ANSWER1)}</answer_text>
                            <answer_text>{html.escape(LESSON_ANSWER2)}</answer_text>
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
                <name>Some Moodle Hosted Content</name>
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


def test_parse_backup_activities(mbz_path):
    activities = utils.parse_backup_activities(mbz_path)
    assert len(activities) == 3


def test_parse_activity_html_contents(mbz_path):
    activities = utils.parse_backup_activities(mbz_path)

    parsed_html_content_strings = []
    for act in activities:
        for html_elem in act.html_elements():
            parsed_html_content_strings.append(
                html_elem.tostring()
            )
    assert set([LESSON1_CONTENT1,
                LESSON1_CONTENT2,
                LESSON_ANSWER1,
                LESSON_ANSWER2,
                PAGE2_CONTENT,
                QUESTION1_CONTENT,
                QUESTION2_CONTENT,
                QUESTION3_CONTENT,
                ANSWER1_CONTENT,
                ANSWER2_CONTENT]) == set(parsed_html_content_strings)


def test_find_external_media_references(mbz_path):
    activities = utils.parse_backup_activities(mbz_path)
    media_references = []

    for act in activities:
        media_references += utils.find_external_media_references(act)

    assert set([IM_MEDIA_LINK,
                OSX_MEDIA_LINK,
                LESSON_ANSW_ILLUSTRATION,
                QUESTION1_ILLUSTRATION,
                QUESTION2_ILLUSTRATION,
                QUESTION3_ILLUSTRATION,
                ANSWER1_ILLUSTRATION,
                ANSWER2_ILLUSTRATION]) == set(media_references)


def test_find_moodle_media_references(mbz_path):
    activities = utils.parse_backup_activities(mbz_path)
    media_references = []

    for act in activities:
        media_references += utils.find_moodle_media_references(act)

    assert set([MOODLE_VIDEO_FILE, MOODLE_TRACK_FILE]) == \
        set(media_references)


def test_find_question_html(mbz_path):
    html_elements = utils.parse_question_bank_for_html(mbz_path)
    html = []
    for elem in html_elements:
        html.append(elem.tostring())
    assert len(html) == 5
    assert set([QUESTION1_CONTENT,
                QUESTION2_CONTENT,
                QUESTION3_CONTENT,
                ANSWER1_CONTENT,
                ANSWER2_CONTENT]) == set(html)


def test_find_questions_by_id(mbz_path):
    ids = ["1"]
    html_elements = utils.parse_question_bank_for_html(mbz_path, ids)
    html = []
    for elem in html_elements:
        html.append(elem.tostring())
    assert len(html) == 3
    assert set([QUESTION1_CONTENT,
                ANSWER1_CONTENT,
                ANSWER2_CONTENT]) == set(html)

    with pytest.raises(NotFoundErr):
        ids = ["9"]
        html = utils.parse_question_bank_for_html(mbz_path, ids)
