from xml.dom import NotFoundErr
import pytest
import html
from mbtools import utils


IM_MEDIA_LINK = "https://s3.amazonaws.com/im-ims-export/imagename"
OSX_MEDIA_LINK = "https://osx-int-alg.s3.us-east-1.amazonaws.com/l1/imagename"
MOODLE_VIDEO_FILE = "@@PLUGINFILE@@/video.mp4"
MOODLE_TRACK_FILE = "@@PLUGINFILE@@/video.vtt"
QUESTION1_ILLUSTRATION = "https://osx-int-alg.s3.us-east-1.amazonaws.com/q1"
QUESTION2_ILLUSTRATION = "https://osx-int-alg.s3.us-east-1.amazonaws.com/q2"
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
    '<img alt="A picture of a map of Brazil" height="71" role="image"'
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
    '<img alt="A picture of a map of Brazil" height="71" role="image"'
    f'src="{QUESTION2_ILLUSTRATION}" title="question" width="202">'
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
    '<img alt="A Picture of Brasilia" height="71" role="image"'
    f'src="{ANSWER1_ILLUSTRATION}" title="answer1" width="101">'
    '</div>'
)
ANSWER2_CONTENT = (
    '<div>'
    '<p>'
    'Rio de Janiero'
    '</p>'
    '<img alt="A picture of Rio De Janiero" height="71" role="image"'
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
                    <directory>activities/lesson_1</directory>
                </activity>
                <activity>
                    <modulename>page</modulename>
                    <directory>activities/page_2</directory>
                </activity>
                <activity>
                    <modulename>quiz</modulename>
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
                <pages>
                    <page>
                        <contents>{html.escape(LESSON1_CONTENT1)}</contents>
                    </page>
                    <page>
                        <contents>{html.escape(LESSON1_CONTENT2)}</contents>
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
                <question_instances>
                    <question_instance id="1">
                        <questionid>1</questionid>
                    </question_instance>
                    <question_instance id ="2">
                        <questionid>2</questionid>
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
            </questions>
        </question_category>
    </question_categories>
    """.strip()
    (tmp_path / "questions.xml").write_text(question_content)

    return tmp_path


def squish_list(html_list):
    """ This helper function removes spaces and newlines from lists"""
    new_list = []
    for item in html_list:
        new_list.append(item.replace('\n', '').replace(' ', ''))

    return new_list


def test_parse_backup_activities(mbz_path):
    activities = utils.parse_backup_activities(mbz_path)

    assert len(activities) == 3


def test_parse_activity_html_contents(mbz_path):
    activities = utils.parse_backup_activities(mbz_path)

    parsed_html_content_strings = []
    for act in activities:
        for html_elem in act.html_elements():
            parsed_html_content_strings.append(
                html_elem.tostring().decode("utf-8")
            )
    comparable_html = squish_list(parsed_html_content_strings)
    assert set(squish_list([LESSON1_CONTENT1,
                           LESSON1_CONTENT2,
                           PAGE2_CONTENT,
                           QUESTION1_CONTENT,
                           QUESTION2_CONTENT,
                           ANSWER1_CONTENT,
                           ANSWER2_CONTENT])) == \
        set(comparable_html)


def test_find_external_media_references(mbz_path):
    activities = utils.parse_backup_activities(mbz_path)
    media_references = []

    for act in activities:
        media_references += utils.find_external_media_references(act)

    assert set([IM_MEDIA_LINK,
                OSX_MEDIA_LINK,
                QUESTION1_ILLUSTRATION,
                QUESTION2_ILLUSTRATION,
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
    html = utils.parse_question_bank_for_html(mbz_path)
    html_squish = squish_list(html)
    assert len(html) == 4
    assert set(squish_list([QUESTION1_CONTENT,
                            QUESTION2_CONTENT,
                            ANSWER1_CONTENT,
                            ANSWER2_CONTENT])) == \
        set(html_squish)


def test_find_questions_by_id(mbz_path):
    ids = ["1"]
    html = utils.parse_question_bank_for_ids(mbz_path, ids)
    html_squish = squish_list(html)
    assert len(html) == 3
    assert set(squish_list([QUESTION1_CONTENT,
                            ANSWER1_CONTENT,
                            ANSWER2_CONTENT])) == \
        set(html_squish)

    with pytest.raises(NotFoundErr):
        ids = ["9"]
        html = utils.parse_question_bank_for_ids(mbz_path, ids)
