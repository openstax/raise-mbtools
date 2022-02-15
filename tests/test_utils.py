import pytest
import html
from mbtools import utils


LESSON1_CONTENT1 = "<p>Lesson 1 content 1</p>"
LESSON1_CONTENT2 = "<p>Lesson 1 content 2</p>"
PAGE2_CONTENT = "<p>Page 2 content</p>"


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
            <quiz id="31">
            </quiz>
        </activity>
    """.strip()
    quiz3_dir = tmp_path / "activities/quiz_3"
    quiz3_dir.mkdir(parents=True)
    (quiz3_dir / "quiz.xml").write_text(quiz3_content)

    return tmp_path


def test_parse_backup_activities(mbz_path):
    activities = utils.parse_backup_activities(mbz_path)

    assert len(activities) == 3


def test_parse_activity_html_contents(mbz_path):
    activities = utils.parse_backup_activities(mbz_path)

    parsed_html_content_strings = []
    for act in activities:
        for html_elem in act.html_elements():
            parsed_html_content_strings.append(html_elem.tostring())

    assert set([LESSON1_CONTENT1, LESSON1_CONTENT2, PAGE2_CONTENT]) == \
        set(parsed_html_content_strings)
