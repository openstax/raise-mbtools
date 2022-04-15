import html
import pytest
from pathlib import Path
from mbtools.html_tag_insertion import TagReplacement
from hashlib import sha256
import os, glob
from bs4 import BeautifulSoup as bs

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

LESSON1_CONTENT2 = "<div>" f'<img src="{OSX_MEDIA_LINK}">' "</div>"
LESSON_ANSWER1 = '<p dir="ltr" style="text-align: left;">' "(6, 0)" "<br>" "</p>"
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
                <pages>
                    <page>
                        <contents>{html.escape(LESSON1_CONTENT1)}</contents>
                    </page>
                    <page>
                        <contents>{html.escape(LESSON1_CONTENT2)}</contents>
                        <answers>
                            <answer_text>{html.escape(LESSON_ANSWER1)}</answer_text>
                            <answer_text>{html.escape(LESSON_ANSWER2)}</answer_text>
                        </answers>
                    </page>
                </pages>
            </lesson>
        </activity>
    """
PAGE2_XML = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <activity id="2" modulename="page">
            <page id="2">
                <content>{html.escape(PAGE2_CONTENT)}</content>
            </page>
        </activity>
    """
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
def populate_tags(uuid_content1, uuid_content2, uuid_page  ):


    PAGE2_CONTENT_TAG = f'<div  class="os-raise-content" data-content-id="{uuid_page}">'
    LESSON1_CONTENT1_TAG = f'<div  class="os-raise-content" data-content-id="{uuid_content1}">'
    LESSON1_CONTENT2_TAG = f'<div  class="os-raise-content" data-content-id="{uuid_content2}">'

    LESSON1_CONTENT_TAGGED = f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <activity id="1" modulename="lesson">
                <lesson id="1">
                    <pages>
                        <page>
                            <contents>{html.escape(LESSON1_CONTENT1_TAG)}</contents>
                        </page>
                        <page>
                            <contents>{html.escape(LESSON1_CONTENT2_TAG)}</contents>
                            <answers>
                                <answer_text>{html.escape(LESSON_ANSWER1)}</answer_text>
                                <answer_text>{html.escape(LESSON_ANSWER2)}</answer_text>
                            </answers>
                        </page>
                    </pages>
                </lesson>
            </activity>
        """
    PAGE2_CONTENT_TAGGED = f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <activity id="2" modulename="page">
                <page id="2">
                    <content>{html.escape(PAGE2_CONTENT_TAG)}</content>
                </page>
            </activity>
        """
    return [LESSON1_CONTENT_TAGGED,PAGE2_CONTENT_TAGGED]
"""
def format_html_file(self, file_content):
        soup = bs(file_content)
        prettyHTML = soup.prettify()
        return prettyHTML"""
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




def test_content_replacement(mbz_path):
    tag_replacer = TagReplacement(mbz_path)

    tag_replacer.replace_tags()
    file_list = os.listdir(f"{mbz_path}/activities")
    content_list = []
    for file in glob.glob(f"{mbz_path}/*.html"):
        with open(file,"r") as f:
            content_list.append(f.read())
    content_set = set(content_list)

    # assert that all tagged content matches.
    answer_set = set([LESSON1_CONTENT1, LESSON1_CONTENT2, PAGE2_CONTENT])

    assert content_set == answer_set
def test_html_files_names(mbz_path):
    tag_replacer = TagReplacement(mbz_path)
    # check file name against files in mbz
    html_files_dict = tag_replacer.replace_tags()
    html_files_inmbz = []
    for file in os.listdir(f"{mbz_path}"):
        if file.endswith(".html"):
            html_files_inmbz.append(Path(file).stem)

    files_in_mbz_set = set(html_files_inmbz)
    files_from_tag_replacer_set = set(list(html_files_dict.keys()))
    print(files_from_tag_replacer_set)
    print(files_in_mbz_set)

    assert files_in_mbz_set == files_from_tag_replacer_set

def test_xml_content_changed(mbz_path):
    tag_replacer = TagReplacement(mbz_path)
    # check file content against files in mbz
    html_files_dict = tag_replacer.replace_tags()
    content_list_in_mbz = []
    files =  os.listdir(f"{mbz_path}/activities")

    print(f"Files in activities: {files}")
    for file in glob.glob(f"{mbz_path}/activities/*/*.xml"):
        with open(file,"r") as f:
            content_list_in_mbz.append(f.read())

    list_of_names = list(html_files_dict.keys())
    correct_content = populate_tags(list_of_names[0], list_of_names[1], list_of_names[2])
    content_list = set(correct_content)
    files_from_tag_replacer_set = set(html_files_dict.values())
    print("Content list ")
    print(content_list_in_mbz)
    print("Correct content ")

    print(correct_content)
    assert len(content_list) == len(content_list_in_mbz)
    assert content_list == content_list_in_mbz





"""
Q: Output into single directory? 
Q: Tabs with 4 spaces okay? 
Q: 
"""