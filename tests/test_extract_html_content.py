import html
import pytest
from pathlib import Path
from mbtools.extract_html_content import replace_content_tags, main
import os

IM_MEDIA_LINK = "https://s3.amazonaws.com/im-ims-export/imagename"
OSX_MEDIA_LINK = "https://osx-int-alg.s3.us-east-1.amazonaws.com/l1/imagename"
MOODLE_VIDEO_FILE = "@@PLUGINFILE@@/video.mp4"
MOODLE_TRACK_FILE = "@@PLUGINFILE@@/video.vtt"
LESSON_ANSW_ILLUSTRATION = "https://osx-int-alg.s3.us-east-1.amazonaws.com/la1"
QUESTION1_ILLUSTRATION = "https://osx-int-alg.s3.us-east-1.amazonaws.com/q1"
QUESTION2_ILLUSTRATION = "https://osx-int-alg.s3.us-east-1.amazonaws.com/q2"
ANSWER1_ILLUSTRATION = "https://osx-int-alg.s3.us-east-1.amazonaws.com/answer1"
ANSWER2_ILLUSTRATION = "https://osx-int-alg.s3.us-east-1.amazonaws.com/answer2"


LESSON1_CONTENT1 = (
    "<div>"
    f'<img src="{IM_MEDIA_LINK}">'
    '<img src="https://validsite/imagename">'
    "</div>"
)

LESSON1_CONTENT2 = (
    "<div>" f'<img src="{OSX_MEDIA_LINK}">' "</div>"
    "<div><p>More content</p></div>"
)
LESSON_ANSWER1 = '<p dir="ltr" style="text-align:' \
                 ' left;">' "(6, 0)" "<br>" "</p>"
LESSON_ANSWER2 = (
    '<p dir="ltr" style="text-align: left;">'
    '<img alt="Answer Picture" height="71" role="image" '
    f'src="{LESSON_ANSW_ILLUSTRATION}" title="question" width="101">'
    "<br>"
    "</p>"
)
PAGE2_CONTENT = (
    "<div>"
    '<video controls="true">'
    f'<source src="{MOODLE_VIDEO_FILE}">'
    f'<track src="{MOODLE_TRACK_FILE}">'
    '<track src="https://validsite/video.vtt">'
    "fallback content"
    "</video>"
    "</div>"
)

LESSON1_XML = f"""
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
PAGE2_XML = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <activity id="2" modulename="page">
            <page id="2">
                <name>Some Moodle Hosted Content</name>
                <content>{html.escape(PAGE2_CONTENT)}</content>
            </page>
        </activity>
    """.strip()
QUESTIONS_XML = """
        <?xml version="1.0" encoding="UTF-8"?>
        <a></a>
        """
BACKUP_XML = """
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

            </activities>
            </contents>
        </moodle_backup>
    """
"""
                <activity>
                    <modulename>quiz</modulename>
                    <directory>activities/quiz_3</directory>
                </activity>
                """


def populate_tags(uuid_content1, uuid_content2, uuid_page):
    PAGE2_CONTENT_TAG = f'<div class="os-raise-content"' \
                        f' data-content-id="{uuid_page}"></div>'
    LESSON1_CONTENT1_TAG = f'<div class="os-raise-content"' \
                           f' data-content-id="{uuid_content1}"></div>'
    LESSON1_CONTENT2_TAG = f'<div class="os-raise-content"' \
                           f' data-content-id="{uuid_content2}"></div>'

    LESSON1_CONTENT_TAGGED = f"""
        <?xml version="1.0" encoding="UTF-8"?>
<activity id="1" modulename="lesson">
            <lesson id="1">
                <name>First Lesson: 1.1</name>
                <pages>
                    <page id="3">
                        <title>First Lession: 1.1 - lesson.xml</title>
                        <contents>{(html.escape(LESSON1_CONTENT1_TAG,
                                                quote=False))}</contents>
                        <answers>
                            <answer_text>{(html.escape(LESSON_ANSWER1,
                                                       quote=False))}</answer_text>
                            <answer_text>{(html.escape(LESSON_ANSWER2,
                                                       quote=False))}</answer_text>
                        </answers>
                    </page>
                    <page id="4">
                        <title>Second Lession: 2.1 - lesson.xml</title>
                        <contents>{(html.escape(LESSON1_CONTENT2_TAG,
                                                quote=False))}</contents>
                        <answers>
                            <answer_text>{(html.escape(LESSON_ANSWER1,
                                                       quote=False))}</answer_text>
                            <answer_text>{(html.escape(LESSON_ANSWER2,
                                                       quote=False))}</answer_text>
                        </answers>
                    </page>
                </pages>
            </lesson>
        </activity>""".strip()
    PAGE2_CONTENT_TAGGED = f"""
        <?xml version="1.0" encoding="UTF-8"?>
<activity id="2" modulename="page">
            <page id="2">
                <name>Some Moodle Hosted Content</name>
                <content>{(html.escape(PAGE2_CONTENT_TAG,
                                       quote=False))}</content>
            </page>
        </activity>
    """.strip()
    return [LESSON1_CONTENT_TAGGED, PAGE2_CONTENT_TAGGED]


@pytest.fixture
def mbz_path(tmp_path):
    lesson1_content = LESSON1_XML.strip()
    lesson1_dir = tmp_path / "activities/lesson_1"
    lesson1_dir.mkdir(parents=True)
    (lesson1_dir / "lesson.xml").write_text(lesson1_content)

    page2_content = PAGE2_XML.strip()
    page2_dir = tmp_path / "activities/page_2"
    page2_dir.mkdir(parents=True)
    (page2_dir / "page.xml").write_text(page2_content)

    back_xml_content = BACKUP_XML.strip()
    (tmp_path / "moodle_backup.xml").write_text(back_xml_content)

    questions_xml_content = QUESTIONS_XML.strip()
    (tmp_path / "questions.xml").write_text(questions_xml_content)

    return tmp_path


def test_html_files_creation(mbz_path):

    # Compare file name with files in mbz.
    html_files_list = replace_content_tags(mbz_path, mbz_path)
    html_file_names_expected = []
    for file in os.listdir(f"{mbz_path}"):
        if file.endswith(".html"):
            html_file_names_expected.append(Path(file).stem)

    file_names = []
    for file in html_files_list:
        file_names.append(file["uuid"])
    assert set(html_file_names_expected) == set(file_names)


def test_html_files_content(mbz_path):
    # compare expected html file content with files in mbz
    html_files_list = replace_content_tags(mbz_path, mbz_path)
    content_expected_in_files = [LESSON1_CONTENT1,
                                 LESSON1_CONTENT2,
                                 PAGE2_CONTENT]

    file_contents = []
    for file in html_files_list:
        file_contents.append(file["content"])

    assert set(content_expected_in_files) == set(file_contents)


def test_xml_content_changed(mbz_path):
    # Compare file content with files in mbz
    html_files_list = replace_content_tags(mbz_path, mbz_path)

    file_names = []
    for file in html_files_list:
        file_names.append(file["uuid"])

    tags = []
    for name in file_names:
        tags.append(html.escape(f'<div class="os-raise-content" '
                                f'data-content-id="{name}"></div>',
                                quote=False))

    correct_content = populate_tags(file_names[0],
                                    file_names[1], file_names[2])
    correct_content = "".join(correct_content)
    for tag in tags:
        assert tag in correct_content


def test_ignore_extracted_content(mbz_path):

    # Extracted tags should not be extracted again.
    html_files_list_first_run = replace_content_tags(mbz_path, mbz_path)
    html_files_inmbz_first_run = []

    for file in os.listdir(f"{mbz_path}"):
        if file.endswith(".html"):
            html_files_inmbz_first_run.append(Path(file).stem)

    html_files_list_second_run = replace_content_tags(mbz_path, mbz_path)
    html_files_inmbz_second_run = []

    for file in os.listdir(f"{mbz_path}"):
        if file.endswith(".html"):
            html_files_inmbz_second_run.append(Path(file).stem)

    # Number of html files should remain the same after second run.
    assert len(html_files_inmbz_first_run) == len(html_files_inmbz_second_run)

    # First run of extract content should return 3 files
    assert(len(html_files_list_first_run) == 3)
    # Second run of the extract content should not return files.
    assert(len(html_files_list_second_run) == 0)


def test_main_no_filter(mbz_path, mocker):
    # Test for main function called by the CLI.
    # No filter args should default to extract page and lesson content.
    mocker.patch(
        "sys.argv",
        ["", f"{mbz_path}", f"{mbz_path}"]
    )
    main()
    html_files_in_mbz = []
    for file in os.listdir(f"{mbz_path}"):
        if file.endswith(".html"):
            html_files_in_mbz.append(Path(file).stem)
    assert len(html_files_in_mbz) == 3


def test_main_lesson_filter(mbz_path, mocker):
    # Test for main function called by the CLI with lesson filter.
    mocker.patch(
        "sys.argv",
        ["", f"{mbz_path}", f"{mbz_path}", "-filter", "lesson"]
    )
    main()
    html_files_in_mbz = []
    for file in os.listdir(f"{mbz_path}"):
        if file.endswith(".html"):
            html_files_in_mbz.append(Path(file).stem)
    assert len(html_files_in_mbz) == 2


def test_main_page_filter(mbz_path, mocker):
    # Test for main function called by the CLI with page filter.
    mocker.patch(
        "sys.argv",
        ["", f"{mbz_path}", f"{mbz_path}", "-filter", "page"]
    )
    main()
    html_files_in_mbz = []
    for file in os.listdir(f"{mbz_path}"):
        if file.endswith(".html"):
            html_files_in_mbz.append(Path(file).stem)
    assert len(html_files_in_mbz) == 1
