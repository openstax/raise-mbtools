from mbtools import fetch_im_resources
import os


def test_fetch_im_resources_main(
    tmp_path, mbz_builder, page_builder, lesson_builder,
    quiz_builder, mocker, requests_mock
):
    filename1 = "abcd.img"
    filename2 = "efgh.img"
    filename3 = "ijkl.mp4"
    filename4 = "mnop.txt"
    im_resource1 = f"https://s3.amazonaws.com/im-ims-export/{filename1}"
    im_resource2 = f"https://s3.amazonaws.com/im-ims-export/{filename2}"
    im_resource3 = f"https://s3.amazonaws.com/im-ims-export/{filename3}"
    im_resource4 = f"https://s3.amazonaws.com/im-ims-export/{filename4}"
    resource_content = b"123456789abcdef"
    requests_mock.get(
        f"https://s3.amazonaws.com/im-ims-export/{filename1}",
        content=resource_content
    )
    requests_mock.get(
        f"https://s3.amazonaws.com/im-ims-export/{filename2}",
        content=resource_content
    )
    requests_mock.get(
        f"https://s3.amazonaws.com/im-ims-export/{filename3}",
        content=resource_content
    )
    requests_mock.get(
        f"https://s3.amazonaws.com/im-ims-export/{filename4}",
        content=resource_content
    )

    lesson1_page1_content = "<div><p>Lesson 1 Page 1</p></div>"
    lesson1_page2_content = "<div><p>Lesson 1 Page 2</p></div>"
    lesson1_page2_answer1_content = "<p>L1 P2 A1</p>"
    lesson1_page2_answer2_content = "<p>L1 P2 A2</p>"
    lesson1_page2_answer1_response = f'<img src="{im_resource4}"></img>'
    lesson1_page2_answer2_response = '<p>response</p>'
    page2_content = f'<div><img src="{im_resource1}">Page 2</p></div>'
    qb_question1_content = "<p>Question 1</p>"
    qb_question1_answer1_content = "<p>answer 1</p>"
    qb_question1_answer2_content = f'<img src="{im_resource2}"></img>'
    qb_question2_content = f'<img src="{im_resource3}"></img>'
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

    output_path = tmp_path / "im_resources"

    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}", f"{output_path}", "mbz"]
    )

    fetch_im_resources.main()

    assert (len(os.listdir(output_path)) == 4)
    for filename in os.listdir(output_path):
        f = os.path.join(output_path, filename)
        with open(f, 'r') as file:
            assert file.read() == resource_content.decode()


def test_fetch_im_resource_none(
    tmp_path, mbz_builder, lesson_builder, mocker
):

    lesson1_page1_content = "<div><p>Lesson 1 Page 1</p></div>"
    lesson1 = lesson_builder(
        id=1,
        name="Lesson 1",
        pages=[
            {
                "id": 11,
                "title": "Lesson 1 Page 1",
                "html_content": lesson1_page1_content
            }
        ]
    )
    mbz_builder(
        tmp_path,
        activities=[lesson1]
        )

    output_path = tmp_path / "im_resources"

    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}", f"{output_path}", "mbz"]
    )

    fetch_im_resources.main()

    assert (len(os.listdir(output_path)) == 0)


def test_fetch_im_resource_repeats(
    tmp_path, mbz_builder, lesson_builder, mocker, requests_mock
):
    filename = "abcd.mp4"
    im_resource = f"https://s3.amazonaws.com/im-ims-export/{filename}"
    lesson1_page1_content = f'''
        <div><p>Lesson 1 Page 1</p>
        <img src="{im_resource}"></img>
        <img src="{im_resource}"></img>
        <img src="{im_resource}"></img></div>'''
    resource_content = b"123456789abcdef"
    lesson1 = lesson_builder(
        id=1,
        name="Lesson 1",
        pages=[
            {
                "id": 11,
                "title": "Lesson 1 Page 1",
                "html_content": lesson1_page1_content
            }
        ]
    )
    mbz_builder(
        tmp_path,
        activities=[lesson1]
        )
    requests_mock.get(
        f"https://s3.amazonaws.com/im-ims-export/{filename}",
        content=resource_content
    )

    output_path = tmp_path / "im_resources"
    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}", f"{output_path}", "mbz"]
    )

    fetch_im_resources.main()

    assert (requests_mock.call_count == 1)
    for filename in os.listdir(output_path):
        f = os.path.join(output_path, filename)
        with open(f, 'r') as file:
            assert file.read() == resource_content.decode()


def test_fetch_im_resource_extracted(
    tmp_path, mocker, requests_mock
):
    filename = "abcd.mp4"
    filename2 = "efgh.mp4"
    im_resource = f"https://s3.amazonaws.com/im-ims-export/{filename}"
    im_resource2 = f"https://s3.amazonaws.com/im-ims-export/{filename2}"
    resource_content = b"123456789abcdef"
    requests_mock.get(
        f"https://s3.amazonaws.com/im-ims-export/{filename}",
        content=resource_content
    )
    requests_mock.get(
        f"https://s3.amazonaws.com/im-ims-export/{filename2}",
        content=resource_content
    )

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

    output_path = tmp_path / "im_resources"
    mocker.patch(
        "sys.argv",
        ["", f"{extracted_path}", f"{output_path}", "html"]
    )
    fetch_im_resources.main()
    assert (len(os.listdir(output_path)) == 2)
    for filename in os.listdir(output_path):
        f = os.path.join(output_path, filename)
        with open(f, 'r') as file:
            assert file.read() == resource_content.decode()


def test_fetch_im_resource_extracted_empty(
    tmp_path, mocker
):

    extracted_path = tmp_path / "extracted"
    extracted_path.mkdir(parents=True, exist_ok=True)

    output_path = tmp_path / "im_resources"
    mocker.patch(
        "sys.argv",
        ["", f"{extracted_path}", f"{output_path}", "html"]
    )
    fetch_im_resources.main()
    assert (len(os.listdir(output_path)) == 0)
