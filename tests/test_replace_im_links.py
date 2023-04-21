import os
from mbtools import replace_im_links
from mbtools.fetch_im_resources import IM_PREFIX
from mbtools import utils
from lxml import html
import json


def collect_resources_from_mbz(mbz_path, prefix=None):
    """
    Given a path to an opened mbz file, this function will return all of the
    references to external sources referenced by the HTML within that mbz. If a
    prefix is provided, it will return the references that contain that
    prefix
    """
    elems = []
    elems.extend(utils.parse_backup_elements(mbz_path))
    resource_elems = []
    for elem in elems:
        if prefix is None:
            resource_elems.extend(elem.etree_fragments[0].xpath('//*[@src]'))
        else:
            resource_elems.extend(elem.etree_fragments[0].xpath(
                f'//*[contains(@src, "{prefix}")]')
                )
    return [el.get("src") for el in resource_elems]


def test_replace_im_links_mbz(
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
        },
        {
            'mime_type': 'application/json',
            'sha1': 'aabcds6acc83666e1d40722e9c743a01e12e65ab',
            'original_filename': 'mnop.json',
            's3_key': 'resources/aabcds6acc83666e1d40722e9c743a01e12e65ab'
        }
    ]
    json_object = json.dumps(media_json, indent=4)
    media_path = tmp_path / "media.json"
    with open(media_path, "w") as outfile:
        outfile.write(json_object)

    filename1 = "abcd.json"
    filename2 = "efgh.json"
    filename3 = "ijkl.json"
    filename4 = "mnop.json"
    im_resource1 = f"https://s3.amazonaws.com/im-ims-export/{filename1}"
    im_resource2 = f"https://s3.amazonaws.com/im-ims-export/{filename2}"
    im_resource3 = f"https://s3.amazonaws.com/im-ims-export/{filename3}"
    im_resource4 = f"https://s3.amazonaws.com/im-ims-export/{filename4}"

    lesson1_page1_content = "<div><p>Lesson 1 Page 1</p></div>"
    lesson1_page2_content = "<div><p>Lesson 1 Page 2</p></div>"
    lesson1_page2_answer1_content = "<p>L1 P2 A1</p>"
    lesson1_page2_answer2_content = f'<img src="{im_resource2}"></img>'
    lesson1_page2_answer1_response = ""
    lesson1_page2_answer2_response = f'<img src="{im_resource4}"></img>'
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
                        "html_content": lesson1_page2_answer1_content,
                        "response": lesson1_page2_answer1_response
                    },
                    {
                        "id": 112,
                        "html_content": lesson1_page2_answer2_content,
                        "response": lesson1_page2_answer2_response
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
                "slot": 1,
                "page": 1,
                "questionid": 1
            },
            {
                "id": 32,
                "slot": 1,
                "page": 2,
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
                "idnumber": 1234,
                "html_content": qb_question1_content,
                "answers": [
                    {
                        "id": 11,
                        "grade": 1,
                        "html_content": qb_question1_answer1_content
                    },
                    {
                        "id": 12,
                        "grade": 0,
                        "html_content": qb_question1_answer2_content
                    }
                ]
            },
            {
                "id": 2,
                "idnumber": 1235,
                "html_content": qb_question2_content
            },
            {
                "id": 3,
                "idnumber": 1236,
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
    assert len(resources) == 4


def test_replace_im_links_mbz_no_matches(
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
                        "html_content": lesson1_page2_answer1_content,
                        "response": ""
                    },
                    {
                        "id": 112,
                        "html_content": lesson1_page2_answer2_content,
                        "response": ""
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


def test_replace_im_resource_extracted(
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
    im_resource = f"{IM_PREFIX}{filename}"
    im_resource2 = f"{IM_PREFIX}{filename2}"

    lesson1_page1_content = f'''
    <div><p>Lesson 1 Page 1</p>
    <img src="{im_resource}"></img></div>'''
    lesson1_page2_content = f'''
    <div><p>Lesson 1 Page 1</p>
    <img src="{im_resource2}"></img></div>'''
    lesson1_page2_variant_content = f'''
    <div><p>Lesson 1 Page 1 Variant</p>
    <img src="{im_resource2}"></img></div>'''

    extracted_path = tmp_path / "extracted"
    extracted_path.mkdir(parents=True, exist_ok=True)
    extracted_filename = extracted_path / "lesson1page1.html"
    extracted_filename.write_text(lesson1_page1_content)
    extracted_filename2 = extracted_path / "lesson1page2.html"
    extracted_filename2.write_text(lesson1_page2_content)
    extracted_filename2_variant_dir = extracted_path / "lesson1page2"
    extracted_filename2_variant_dir.mkdir()
    extracted_filename2_variant = extracted_filename2_variant_dir / "foo.html"
    extracted_filename2_variant.write_text(lesson1_page2_variant_content)

    new_prefix = "k12"
    mocker.patch(
        "sys.argv",
        ["", f"{extracted_path}", f"{media_path}", f"{new_prefix}", "html"]
    )
    replace_im_links.main()

    assert (len(list(extracted_path.rglob("*.html"))) == 3)
    resources = []
    for filename in extracted_path.rglob("*.html"):
        with open(filename, 'r') as file:
            data = file.read()
            for elem in html.fragments_fromstring(
                        data)[0].xpath('//*[@src]'):
                resources.append(elem.attrib['src'])
    assert len(resources) == 3
    for r in resources:
        assert new_prefix in r


def test_replace_im_resource_extracted_no_matches(
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
            for elem in html.fragments_fromstring(
                        data)[0].xpath('//*[@src]'):
                resources.append(elem.attrib['src'])
    assert len(resources) == 2
    for r in resources:
        assert new_prefix not in r


def test_replace_im_resources_html_overlapping_filenames(
    tmp_path, mocker, requests_mock
):
    media_json = [
        {
            'mime_type': 'application/json',
            'sha1': 'c527d2ba1d2dbcefb509822abb0bf2ab04457a2c',
            'original_filename': 'abcd.json',
            's3_key': 'resources/c527d2ba1d2dbcefb509822abb0bf2ab04457a2c'
        }
    ]
    json_object = json.dumps(media_json, indent=4)
    media_path = tmp_path / "media.json"
    with open(media_path, "w") as outfile:
        outfile.write(json_object)

    filename = "abcd.json"
    filename2 = "efgh.json"
    im_resource = f"{IM_PREFIX}{filename}"
    im_resource2 = f"{IM_PREFIX}{filename2}"

    resource_content = b"123456789abcdef"
    requests_mock.get(
        im_resource2,
        content=resource_content
    )

    lesson1_page1_content = f'''
    <div><p>Lesson 1 Page 1</p>
    <img src="{im_resource}"></img></div>
    <img src="{im_resource2}"></img></div>'''

    extracted_path = tmp_path / "extracted"
    extracted_path.mkdir(parents=True, exist_ok=True)
    extracted_filename = extracted_path / "lesson1page1.html"
    extracted_filename.write_text(lesson1_page1_content)

    new_prefix = "k12"
    mocker.patch(
        "sys.argv",
        ["", f"{extracted_path}", f"{media_path}", f"{new_prefix}", "html"]
    )
    replace_im_links.main()

    resources = []
    for filename in os.listdir(extracted_path):
        f = os.path.join(extracted_path, filename)
        with open(f, 'r') as file:
            data = file.read()
            for elem in html.fragments_fromstring(
                        data)[0].xpath('//*[@src]'):
                resources.append(elem.attrib['src'])
    assert len(resources) == 2
    for r in resources:
        assert new_prefix in r
