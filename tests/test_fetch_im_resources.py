from mbtools import fetch_im_resources 
import os


def test_fetch_im_resources_main(
    tmp_path, mbz_builder, page_builder, lesson_builder,
    quiz_builder, mocker, requests_mock
):
    filename1 = "abcd.img"
    filename2 = "efgh.img"
    filename3 = "ijkl.mp4"
    im_resource1 = f"https://s3.amazonaws.com/im-ims-export/{filename1}"
    im_resource2 = f"https://s3.amazonaws.com/im-ims-export/{filename2}"
    im_resource3 = f"https://s3.amazonaws.com/im-ims-export/{filename3}"
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

    lesson1_page1_content = "<div><p>Lesson 1 Page 1</p></div>"
    lesson1_page2_content = "<div><p>Lesson 1 Page 2</p></div>"
    lesson1_page2_answer1_content = "<p>L1 P2 A1</p>"
    lesson1_page2_answer2_content = "<p>L1 P2 A2</p>"
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

    output_path = tmp_path / "im_resources"

    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}", f"{output_path}"]
    )

    fetch_im_resources.main()

    assert(len(os.listdir(output_path)) == 3)
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
        ["", f"{tmp_path}", f"{output_path}"]
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
        ["", f"{tmp_path}", f"{output_path}"]
    )

    fetch_im_resources.main()

    assert (len(os.listdir(output_path)) == 1)
    for filename in os.listdir(output_path):
        f = os.path.join(output_path, filename)
        with open(f, 'r') as file:
            assert file.read() == resource_content.decode()
