import os
from mbtools import replace_im_links
from mbtools.fetch_im_resources import IM_PREFIX
from mbtools.utils import collect_resources_from_mbz
from lxml import html
import json


def test_replace_im_links_regular(
    tmp_path, mbz_builder, page_builder, lesson_builder,
    quiz_builder, mocker
):
    media_json = [
        {
            'mime_type': 'application/json',
            'sha1': 'dc330ae2bc1d0b2edac442ed3f8245647cf5c0c0',
            'original_filename': 'abcd.json',
            's3_key': 'resources/dc330ae2bc1d0b2edac442ed3f8245647cf5c0c0'
        },
        {
            'mime_type': 'application/json',
            'sha1': 'a31e7f061d762f1e5099ecebfe6877310e5be420',
            'original_filename': 'efgh.json',
            's3_key': 'resources/a31e7f061d762f1e5099ecebfe6877310e5be420'
        },
        {
            'mime_type': 'application/json',
            'sha1': 'e606bc6acc83666e1d40722e9c743a01e12e65ab',
            'original_filename': 'ijkl.json',
            's3_key': 'resources/e606bc6acc83666e1d40722e9c743a01e12e65ab'
        }
    ]
    json_object = json.dumps(media_json, indent=4)
    media_path = tmp_path / "media.json"
    with open(media_path, "w") as outfile:
        outfile.write(json_object)

    filename1 = "abcd.json"
    filename2 = "efgh.json"
    filename3 = "ijkl.json"
    im_resource1 = f"https://s3.amazonaws.com/im-ims-export/{filename1}"
    im_resource2 = f"https://s3.amazonaws.com/im-ims-export/{filename2}"
    im_resource3 = f"https://s3.amazonaws.com/im-ims-export/{filename3}"

    lesson1_page1_content = "<div><p>Lesson 1 Page 1</p></div>"
    lesson1_page2_content = "<div><p>Lesson 1 Page 2</p></div>"
    lesson1_page2_answer1_content = "<p>L1 P2 A1</p>"
    lesson1_page2_answer2_content = f'<img src="{im_resource2}"></img>'
    page2_content = f'<div><img src="{im_resource1}">Page 2</p></div>'
    qb_question1_content = "<p>Question 1</p>"
    qb_question1_answer1_content = "<p>answer 1</p>"
    qb_question1_answer2_content = f'<img src="{im_resource3}"></img>'
    qb_question2_content = "<p>Question 2 </p>"
    qb_question3_content = "<p>Question 3</p>"

    lesson1 = lesson_builder(
        id=1,
        name="Lesson 1",
        pages=[
            {
                "id": 11,
                "title": "Lesson 1 Page 1",
                "html_content": lesson1_page1_content
            },
            {
                "id": 12,
                "title": "Lesson 1 Page 2",
                "html_content": lesson1_page2_content,
                "answers": [
                    {
                        "id": 111,
                        "html_content": lesson1_page2_answer1_content
                    },
                    {
                        "id": 112,
                        "html_content": lesson1_page2_answer2_content
                    }
                ]
            }
        ]
    )
    page2 = page_builder(id=2, name="Page 2", html_content=page2_content)
    quiz3 = quiz_builder(
        id=3,
        name="Quiz 3",
        questions=[
            {
                "id": 31,
                "questionid": 1
            },
            {
                "id": 32,
                "questionid": 2
            }
        ]
    )
    mbz_builder(
        tmp_path,
        activities=[lesson1, page2, quiz3],
        questionbank_questions=[
            {
                "id": 1,
                "html_content": qb_question1_content,
                "answers": [
                    {
                        "id": 11,
                        "html_content": qb_question1_answer1_content
                    },
                    {
                        "id": 12,
                        "html_content": qb_question1_answer2_content
                    }
                ]
            },
            {
                "id": 2,
                "html_content": qb_question2_content
            },
            {
                "id": 3,
                "html_content": qb_question3_content
            }
        ]
    )

    replacing_prefix = "k12"
    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}", f"{media_path}", f"{replacing_prefix}", "mbz"]
    )

    replace_im_links.main()

    resources = collect_resources_from_mbz(tmp_path, IM_PREFIX)
    assert len(resources) == 0
    resources = collect_resources_from_mbz(tmp_path, replacing_prefix)
    assert len(resources) == 3


def test_replace_im_links_regular_no_matches(
    tmp_path, mbz_builder, lesson_builder, mocker
):
    media_json = [
        {
            'mime_type': 'application/json',
            'sha1': 'dc330ae2bc1d0b2edac442ed3f8245647cf5c0c0',
            'original_filename': 'abcd.json',
            's3_key': 'resources/dc330ae2bc1d0b2edac442ed3f8245647cf5c0c0'
        },
        {
            'mime_type': 'application/json',
            'sha1': 'a31e7f061d762f1e5099ecebfe6877310e5be420',
            'original_filename': 'efgh.json',
            's3_key': 'resources/a31e7f061d762f1e5099ecebfe6877310e5be420'
        },
        {
            'mime_type': 'application/json',
            'sha1': 'e606bc6acc83666e1d40722e9c743a01e12e65ab',
            'original_filename': 'ijkl.json',
            's3_key': 'resources/e606bc6acc83666e1d40722e9c743a01e12e65ab'
        }
    ]
    json_object = json.dumps(media_json, indent=4)
    media_path = tmp_path / "media.json"
    with open(media_path, "w") as outfile:
        outfile.write(json_object)

    filename1 = "abcd.json"
    im_resource1 = f"https://otherprefix.com/{filename1}"
    lesson1_page1_content = "<div><p>Lesson 1 Page 1</p></div>"
    lesson1_page2_content = "<div><p>Lesson 1 Page 2</p></div>"
    lesson1_page2_answer1_content = "<p>L1 P2 A1</p>"
    lesson1_page2_answer2_content = f'<img src="{im_resource1}"></img>'

    lesson1 = lesson_builder(
        id=1,
        name="Lesson 1",
        pages=[
            {
                "id": 11,
                "title": "Lesson 1 Page 1",
                "html_content": lesson1_page1_content
            },
            {
                "id": 12,
                "title": "Lesson 1 Page 2",
                "html_content": lesson1_page2_content,
                "answers": [
                    {
                        "id": 111,
                        "html_content": lesson1_page2_answer1_content
                    },
                    {
                        "id": 112,
                        "html_content": lesson1_page2_answer2_content
                    }
                ]
            }
        ]
    )
    mbz_builder(
        tmp_path,
        activities=[lesson1]
    )

    replacing_prefix = "k12"
    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}", f"{media_path}", f"{replacing_prefix}", "mbz"]
    )

    replace_im_links.main()

    resources = collect_resources_from_mbz(tmp_path)
    assert len(resources) == 1
    resources = collect_resources_from_mbz(tmp_path, replacing_prefix)
    assert len(resources) == 0


def test_fetch_im_resource_extracted(
    tmp_path, mocker
):
    media_json = [
        {
            'mime_type': 'application/json',
            'sha1': 'dc330ae2bc1d0b2edac442ed3f8245647cf5c0c0',
            'original_filename': 'abcd.json',
            's3_key': 'resources/dc330ae2bc1d0b2edac442ed3f8245647cf5c0c0'
        },
        {
            'mime_type': 'application/json',
            'sha1': 'a31e7f061d762f1e5099ecebfe6877310e5be420',
            'original_filename': 'efgh.json',
            's3_key': 'resources/a31e7f061d762f1e5099ecebfe6877310e5be420'
        }
    ]
    json_object = json.dumps(media_json, indent=4)
    media_path = tmp_path / "media.json"
    with open(media_path, "w") as outfile:
        outfile.write(json_object)

    filename = "abcd.json"
    filename2 = "efgh.json"
    im_resource = f"https://s3.amazonaws.com/im-ims-export/{filename}"
    im_resource2 = f"https://s3.amazonaws.com/im-ims-export/{filename2}"

    lesson1_page1_content = f'''
    <div><p>Lesson 1 Page 1</p>
    <img src="{im_resource}"></img></div>'''
    lesson1_page2_content = f'''
    <div><p>Lesson 1 Page 1</p>
    <img src="{im_resource2}"></img></div>'''

    extracted_path = tmp_path / "extracted"
    extracted_path.mkdir(parents=True, exist_ok=True)
    extracted_filename = extracted_path / "lesson1page1.html"
    extracted_filename.write_text(lesson1_page1_content)
    extracted_filename2 = extracted_path / "lesson1page2.html"
    extracted_filename2.write_text(lesson1_page2_content)

    new_prefix = "k12"
    mocker.patch(
        "sys.argv",
        ["", f"{extracted_path}", f"{media_path}", f"{new_prefix}", "html"]
    )
    replace_im_links.main()

    assert (len(os.listdir(extracted_path)) == 2)
    resources = []
    for filename in os.listdir(extracted_path):
        f = os.path.join(extracted_path, filename)
        with open(f, 'r') as file:
            data = file.read()
            for attr in ['src', 'href']:
                for elem in html.fragments_fromstring(
                            data)[0].xpath(f'//*[@{attr}]'):
                    resources.append(elem.attrib[attr])
    assert len(resources) == 2
    for r in resources:
        assert new_prefix in r


def test_fetch_im_resource_extracted_no_matches(
    tmp_path, mocker
):
    media_json = [
        {
            'mime_type': 'application/json',
            'sha1': 'dc330ae2bc1d0b2edac442ed3f8245647cf5c0c0',
            'original_filename': 'abcd.json',
            's3_key': 'resources/dc330ae2bc1d0b2edac442ed3f8245647cf5c0c0'
        },
        {
            'mime_type': 'application/json',
            'sha1': 'a31e7f061d762f1e5099ecebfe6877310e5be420',
            'original_filename': 'efgh.json',
            's3_key': 'resources/a31e7f061d762f1e5099ecebfe6877310e5be420'
        }
    ]
    json_object = json.dumps(media_json, indent=4)
    media_path = tmp_path / "media.json"
    with open(media_path, "w") as outfile:
        outfile.write(json_object)

    filename = "abcd.json"
    filename2 = "efgh.json"
    im_resource = f"{filename}"
    im_resource2 = f"{filename2}"

    lesson1_page1_content = f'''
    <div><p>Lesson 1 Page 1</p>
    <img src="{im_resource}"></img></div>'''
    lesson1_page2_content = f'''
    <div><p>Lesson 1 Page 1</p>
    <img src="{im_resource2}"></img></div>'''

    extracted_path = tmp_path / "extracted"
    extracted_path.mkdir(parents=True, exist_ok=True)
    extracted_filename = extracted_path / "lesson1page1.html"
    extracted_filename.write_text(lesson1_page1_content)
    extracted_filename2 = extracted_path / "lesson1page2.html"
    extracted_filename2.write_text(lesson1_page2_content)

    new_prefix = "k12"
    mocker.patch(
        "sys.argv",
        ["", f"{extracted_path}", f"{media_path}", f"{new_prefix}", "html"]
    )
    replace_im_links.main()

    assert (len(os.listdir(extracted_path)) == 2)
    resources = []
    for filename in os.listdir(extracted_path):
        f = os.path.join(extracted_path, filename)
        with open(f, 'r') as file:
            data = file.read()
            for attr in ['src', 'href']:
                for elem in html.fragments_fromstring(
                            data)[0].xpath(f'//*[@{attr}]'):
                    resources.append(elem.attrib[attr])
    assert len(resources) == 2
    for r in resources:
        assert new_prefix not in r
