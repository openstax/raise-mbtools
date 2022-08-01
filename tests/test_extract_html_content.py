from pathlib import Path
from mbtools.extract_html_content import replace_content_tags, main
import os
from lxml import etree


def test_html_files_creation(
    tmp_path, page_builder, lesson_builder, mbz_builder
):
    lesson1_page1_content = "<div><p>Lesson 1 Page 1</p></div>"
    lesson1_page2_content = "<div><p>Lesson 1 Page 2</p></div>"
    page2_content = "<div><p>Page 2</p></div>"

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
                "html_content": lesson1_page2_content
            }
        ]
    )
    page2 = page_builder(id=2, name="Page 2", html_content=page2_content)
    mbz_path = tmp_path / "mbz"
    html_path = tmp_path / "html"
    html_path.mkdir()

    mbz_builder(mbz_path, activities=[lesson1, page2])

    # Compare file name with files in mbz.
    html_files_list = replace_content_tags(mbz_path, html_path)
    html_file_names_expected = []
    for file in os.listdir(f"{html_path}"):
        if file.endswith(".html"):
            html_file_names_expected.append(Path(file).stem)

    file_names = []
    for file in html_files_list:
        file_names.append(file["uuid"])
    assert set(html_file_names_expected) == set(file_names)


def test_html_files_content(
    tmp_path, page_builder, lesson_builder, mbz_builder
):
    lesson1_page1_content = "<div><p>Lesson 1 Page 1</p></div>"
    lesson1_page2_content = "<div><p>Lesson 1 Page 2</p></div>"
    lesson1_page2_answer1_content = "<p>L1 P2 A1</p>"
    lesson1_page2_answer2_content = "<p>L1 P2 A2</p>"
    lesson1_page2_answer1_response = "<p>L1 P2 A1 R</p>"
    lesson1_page2_answer2_response = "<p>L1 P2 A2 R</p>"
    page2_content = "<div><p>Page 2</p></div>"

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
    mbz_path = tmp_path / "mbz"
    html_path = tmp_path / "html"
    html_path.mkdir()

    mbz_builder(mbz_path, activities=[lesson1, page2])

    # compare expected html file content with files in mbz
    html_files_list = replace_content_tags(mbz_path, html_path)
    content_expected_in_files = [lesson1_page1_content,
                                 lesson1_page2_content,
                                 page2_content]

    file_contents = []
    for file in html_files_list:
        file_contents.append(file["content"])

    assert set(content_expected_in_files) == set(file_contents)


def test_xml_content_changed(
    tmp_path, page_builder, lesson_builder, mbz_builder
):
    lesson1_page1_content = "<div><p>Lesson 1 Page 1</p></div>"
    lesson1_page2_content = "<div><p>Lesson 1 Page 2</p></div>"
    page2_content = "<div><p>Page 2</p></div>"

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
                "html_content": lesson1_page2_content
            }
        ]
    )
    page2 = page_builder(id=2, name="Page 2", html_content=page2_content)
    mbz_path = tmp_path / "mbz"
    html_path = tmp_path / "html"
    html_path.mkdir()

    mbz_builder(mbz_path, activities=[lesson1, page2])

    # Compare file content with files in mbz
    html_files_list = replace_content_tags(mbz_path, html_path)

    file_names = []
    for file in html_files_list:
        file_names.append(file["uuid"])

    tags = []
    for name in file_names:
        tags.append(
            f'<div class="os-raise-content" data-content-id="{name}"></div>'
        )

    updated_lesson_etree = etree.parse(
        f"{mbz_path}/activities/lesson_1/lesson.xml"
    )

    updated_lesson1_page1_content = updated_lesson_etree.xpath(
        "//page[@id=11]/contents"
    )[0].text

    assert updated_lesson1_page1_content in tags

    updated_lesson1_page2_content = updated_lesson_etree.xpath(
        "//page[@id=12]/contents"
    )[0].text

    assert updated_lesson1_page2_content in tags

    updated_page_etree = etree.parse(f"{mbz_path}/activities/page_2/page.xml")

    updated_page2_content = updated_page_etree.xpath("//page/content")[0].text

    assert updated_page2_content in tags


def test_ignore_extracted_content(tmp_path, page_builder, mbz_builder):
    pages = []
    for indx in range(3):
        pages.append(page_builder(
            id=indx,
            name="Page",
            html_content="<div><p>Page</p></div>"
        ))
    mbz_path = tmp_path / "mbz"
    html_path = tmp_path / "html"
    html_path.mkdir()

    mbz_builder(mbz_path, activities=pages)

    # Extracted tags should not be extracted again.
    html_files_list_first_run = replace_content_tags(mbz_path, html_path)
    html_files_inmbz_first_run = []

    for file in os.listdir(f"{mbz_path}"):
        if file.endswith(".html"):
            html_files_inmbz_first_run.append(Path(file).stem)

    html_files_list_second_run = replace_content_tags(mbz_path, html_path)
    html_files_inmbz_second_run = []

    for file in os.listdir(f"{mbz_path}"):
        if file.endswith(".html"):
            html_files_inmbz_second_run.append(Path(file).stem)

    # Number of html files should remain the same after second run.
    assert len(html_files_inmbz_first_run) == len(html_files_inmbz_second_run)

    # First run of extract content should return 3 files
    assert (len(html_files_list_first_run) == 3)
    # Second run of the extract content should not return files.
    assert (len(html_files_list_second_run) == 0)


def test_main_no_filter(
    tmp_path, page_builder, lesson_builder, mbz_builder, mocker
):
    # Test for main function called by the CLI.
    # No filter args should default to extract page and lesson content.
    activities = []
    for indx in range(1):
        activities.append(page_builder(
            id=indx,
            name="Page",
            html_content="<div><p>Page</p></div>"
        ))

    for indx in range(2):
        activities.append(lesson_builder(
            id=indx,
            name="Lesson",
            pages=[
                {
                    "id": indx,
                    "title": "Lesson Page",
                    "html_content": "<div><p>Lesson page</p></div>"
                }
            ]
        ))

    mbz_path = tmp_path / "mbz"
    html_path = tmp_path / "html"
    html_path.mkdir()

    mbz_builder(mbz_path, activities=activities)
    mocker.patch(
        "sys.argv",
        ["", f"{mbz_path}", f"{html_path}"]
    )
    main()
    html_files_in_mbz = []
    for file in os.listdir(f"{html_path}"):
        if file.endswith(".html"):
            html_files_in_mbz.append(Path(file).stem)
    assert len(html_files_in_mbz) == 3


def test_main_lesson_filter(
    tmp_path, page_builder, lesson_builder, mbz_builder, mocker
):
    # Test for main function called by the CLI with lesson filter.
    activities = []
    for indx in range(1):
        activities.append(page_builder(
            id=indx,
            name="Page",
            html_content="<div><p>Page</p></div>"
        ))

    for indx in range(2):
        activities.append(lesson_builder(
            id=indx,
            name="Lesson",
            pages=[
                {
                    "id": indx,
                    "title": "Lesson Page",
                    "html_content": "<div><p>Lesson page</p></div>"
                }
            ]
        ))

    mbz_path = tmp_path / "mbz"
    html_path = tmp_path / "html"
    html_path.mkdir()

    mbz_builder(mbz_path, activities=activities)

    mocker.patch(
        "sys.argv",
        ["", f"{mbz_path}", f"{html_path}", "-filter", "lesson"]
    )
    main()
    html_files_in_mbz = []
    for file in os.listdir(f"{html_path}"):
        if file.endswith(".html"):
            html_files_in_mbz.append(Path(file).stem)
    assert len(html_files_in_mbz) == 2


def test_main_page_filter(
    tmp_path, page_builder, lesson_builder, mbz_builder, mocker
):
    # Test for main function called by the CLI with page filter.
    activities = []
    for indx in range(1):
        activities.append(page_builder(
            id=indx,
            name="Page",
            html_content="<div><p>Page</p></div>"
        ))

    for indx in range(2):
        activities.append(lesson_builder(
            id=indx,
            name="Lesson",
            pages=[
                {
                    "id": indx,
                    "title": "Lesson Page",
                    "html_content": "<div><p>Lesson page</p></div>"
                }
            ]
        ))

    mbz_path = tmp_path / "mbz"
    html_path = tmp_path / "html"
    html_path.mkdir()

    mbz_builder(mbz_path, activities=activities)
    mocker.patch(
        "sys.argv",
        ["", f"{mbz_path}", f"{html_path}", "-filter", "page"]
    )
    main()
    html_files_in_mbz = []
    for file in os.listdir(f"{html_path}"):
        if file.endswith(".html"):
            html_files_in_mbz.append(Path(file).stem)
    assert len(html_files_in_mbz) == 1
