import os
import mbtools.extract_html_content
from mbtools.generate_mbz_toc import main
import csv
from mbtools.utils import validate_uuid4


def test_toc_creation_single_page(
    mocker, tmp_path, mbz_builder, page_builder
):

    page_html = "<p>Content</p>"
    page_name = "Only Page"
    page = page_builder(
            id=1,
            name=page_name,
            html_content=page_html
        )

    mbz_path = tmp_path / "mbz"
    html_path = tmp_path / "html"
    html_path.mkdir()
    mbz_builder(mbz_path, activities=[page])
    mbtools.extract_html_content.replace_content_tags(mbz_path, html_path)
    md_filepath = tmp_path
    mocker.patch(
        "sys.argv",
        ["", f"{mbz_path}", str(md_filepath)]
    )
    main()

    html_filename = ""
    for path, dirs, files in os.walk(html_path):
        assert len(files) == 1
        html_filename = files[0]
        with open((html_path / html_filename), 'r') as f:
            assert f.read() == page_html

    with open(f'{md_filepath}/toc.md', 'r') as f:
        lines = [line.rstrip() for line in f]
        assert len(lines) == 3
        assert lines[0] == "# Table of Contents"
        assert lines[1] == "* Default Section"
        assert lines[2] == f"    * [{page_name}](./html/{html_filename})"


def test_toc_creation_single_lesson(
    mocker, tmp_path, mbz_builder, lesson_builder
):

    lesson_html = "<p>Content</p>"
    lesson_name = "Only Lesson"
    lesson_page_name = "Lesson Page"
    lesson = lesson_builder(
            id=1,
            name=lesson_name,
            pages=[
                {
                    "id": 1,
                    "title": lesson_page_name,
                    "html_content": lesson_html
                }]
    )

    mbz_path = tmp_path / "mbz"
    html_path = tmp_path / "html"
    html_path.mkdir()
    mbz_builder(mbz_path, activities=[lesson])
    mbtools.extract_html_content.replace_content_tags(mbz_path, html_path)
    md_filepath = tmp_path
    mocker.patch(
        "sys.argv",
        ["", f"{mbz_path}", str(md_filepath)]
    )
    main()

    html_filename = ""
    for path, dirs, files in os.walk(html_path):
        assert len(files) == 1
        html_filename = files[0]
        with open((html_path / html_filename), 'r') as f:
            assert f.read() == lesson_html

    with open(f'{md_filepath}/toc.md') as f:
        lines = [line.rstrip() for line in f]
        assert len(lines) == 4
        assert lines[0] == "# Table of Contents"
        assert lines[1] == "* Default Section"
        assert lines[2] == f"    * {lesson_name}"
        assert lines[3] == \
            f"        * [{lesson_page_name}](./html/{html_filename})"


def test_toc_creation_lesson_pages_in_order(
    mocker, tmp_path, mbz_builder, lesson_builder
):
    lesson_name = "Only Lesson"
    lesson_html_1 = "<p>Content 1</p>"
    lesson_html_2 = "<p>Content 2</p>"
    lesson_html_3 = "<p>Content 3</p>"
    lesson_page_name_1 = "Lesson Page 1"
    lesson_page_name_2 = "Lesson Page 2"
    lesson_page_name_3 = "Lesson Page 3"
    lesson = lesson_builder(
            id=1,
            name=lesson_name,
            pages=[
                {
                    "id": "3",
                    "title": lesson_page_name_3,
                    "html_content": lesson_html_3
                },
                {
                    "id": "2",
                    "title": lesson_page_name_2,
                    "html_content": lesson_html_2
                },
                {
                    "id": "1",
                    "title": lesson_page_name_1,
                    "html_content": lesson_html_1
                }
                ]
    )

    mbz_path = tmp_path / "mbz"
    html_path = tmp_path / "html"
    html_path.mkdir()
    mbz_builder(mbz_path, activities=[lesson])
    mbtools.extract_html_content.replace_content_tags(mbz_path, html_path)
    md_filepath = tmp_path
    mocker.patch(
        "sys.argv",
        ["", f"{mbz_path}", str(md_filepath)]
    )
    main()

    html_filenames = {}
    for path, dirs, files in os.walk(html_path):
        assert len(files) == 3
        for html_filename in files:
            with open((html_path / html_filename), 'r') as f:
                content = f.read()
                if content == lesson_html_1:
                    html_filenames[1] = html_filename
                elif content == lesson_html_2:
                    html_filenames[2] = html_filename
                elif content == lesson_html_3:
                    html_filenames[3] = html_filename

    with open(f'{md_filepath}/toc.md') as f:
        lines = [line.rstrip() for line in f]
        assert len(lines) == 6
        assert lines[0] == "# Table of Contents"
        assert lines[1] == "* Default Section"
        assert lines[2] == f"    * {lesson_name}"
        assert lines[3] == \
            f"        * [{lesson_page_name_3}](./html/{html_filenames[3]})"
        assert lines[4] == \
            f"        * [{lesson_page_name_2}](./html/{html_filenames[2]})"
        assert lines[5] == \
            f"        * [{lesson_page_name_1}](./html/{html_filenames[1]})"


def test_toc_creation_multiple_sections(
    mocker, tmp_path, mbz_builder, page_builder
):

    page_html_1 = "<p>Content 1</p>"
    page_html_2 = "<p>Content 2"
    page_name_1 = "Page 1"
    page_name_2 = "Page 2"
    page_1 = page_builder(
            section_id=1,
            id=1,
            name=page_name_1,
            html_content=page_html_1
        )
    page_2 = page_builder(
            section_id=2,
            id=2,
            name=page_name_2,
            html_content=page_html_2
        )

    section_name_1 = "First Section"
    section_name_2 = "Second Section"
    sections = [
        {
            "id": 1,
            "title": section_name_1
        },
        {
            "id": 2,
            "title": section_name_2
        }]

    mbz_path = tmp_path / "mbz"
    html_path = tmp_path / "html"
    html_path.mkdir()
    mbz_builder(mbz_path, activities=[page_1, page_2], sections=sections)
    mbtools.extract_html_content.replace_content_tags(mbz_path, html_path)
    md_filepath = tmp_path
    mocker.patch(
        "sys.argv",
        ["", f"{mbz_path}", str(md_filepath)]
    )
    main()

    html_filenames = {}
    for path, dirs, files in os.walk(html_path):
        assert len(files) == 2
        for html_filename in files:
            with open((html_path / html_filename), 'r') as f:
                content = f.read()
                if content == page_html_1:
                    html_filenames[1] = html_filename
                elif content == page_html_2:
                    html_filenames[2] = html_filename

    with open(f'{md_filepath}/toc.md') as f:
        lines = [line.rstrip() for line in f]
        assert len(lines) == 5
        assert lines[0] == "# Table of Contents"
        assert lines[1] == f"* {section_name_1}"
        assert lines[2] == f"    * [{page_name_1}](./html/{html_filenames[1]})"
        assert lines[3] == f"* {section_name_2}"
        assert lines[4] == f"    * [{page_name_2}](./html/{html_filenames[2]})"


def test_toc_creation_page_and_lesson_together(
    mocker, tmp_path, mbz_builder, lesson_builder, page_builder
):
    lesson_html = "<p>Lesson Content</p>"
    lesson_name = "Only Lesson"
    lesson_page_name = "Lesson Page 1"
    lesson = lesson_builder(
            id=1,
            name=lesson_name,
            pages=[
                {
                    "id": "1",
                    "title": lesson_page_name,
                    "html_content": lesson_html
                }
            ]
    )
    page_html = "<p>Page Content</p>"
    page_name = "Only Page"
    page = page_builder(
            id=1,
            name=page_name,
            html_content=page_html
        )

    mbz_path = tmp_path / "mbz"
    html_path = tmp_path / "html"
    html_path.mkdir()
    mbz_builder(mbz_path, activities=[lesson, page])
    mbtools.extract_html_content.replace_content_tags(mbz_path, html_path)
    md_filepath = tmp_path
    mocker.patch(
        "sys.argv",
        ["", f"{mbz_path}", str(md_filepath)]
    )
    main()

    html_filenames = {}
    for path, dirs, files in os.walk(html_path):
        assert len(files) == 2
        for html_filename in files:
            with open((html_path / html_filename), 'r') as f:
                content = f.read()
                if content == lesson_html:
                    html_filenames["L"] = html_filename
                elif content == page_html:
                    html_filenames["P"] = html_filename

    with open(f'{md_filepath}/toc.md') as f:
        lines = [line.rstrip() for line in f]
        assert len(lines) == 5
        assert lines[0] == "# Table of Contents"
        assert lines[1] == "* Default Section"
        assert lines[2] == f"    * {lesson_name}"
        assert lines[3] == \
            f'        * [{lesson_page_name}](./html/{html_filenames["L"]})'
        assert lines[4] == f'    * [{page_name}](./html/{html_filenames["P"]})'


def test_toc_creation_page_and_lesson_together_csv(
    mocker, tmp_path, mbz_builder, lesson_builder, page_builder
):
    lesson_html = "<p>Lesson Content</p>"
    lesson_name = "Only Lesson"
    lesson_page_name = "Lesson Page 1"
    lesson = lesson_builder(
            id=1,
            name=lesson_name,
            pages=[
                {
                    "id": "1",
                    "title": lesson_page_name,
                    "html_content": lesson_html
                }
            ]
    )
    page_html = "<p>Page Content</p>"
    page_name = "Only Page"
    page = page_builder(
            id=1,
            name=page_name,
            html_content=page_html
        )

    mbz_path = tmp_path / "mbz"
    html_path = tmp_path / "html"
    html_path.mkdir()
    mbz_builder(mbz_path, activities=[lesson, page])
    mbtools.extract_html_content.replace_content_tags(mbz_path, html_path)
    md_filepath = tmp_path

    mocker.patch(
        "sys.argv",
        ["", f"{mbz_path}", str(md_filepath), '--csv']
    )
    main()

    html_filenames = {}
    for path, dirs, files in os.walk(html_path):
        assert len(files) == 2
        for html_filename in files:
            with open((html_path / html_filename), 'r') as f:
                content = f.read()
                if content == lesson_html:
                    html_filenames["L"] = html_filename
                elif content == page_html:
                    html_filenames["P"] = html_filename

    toc_csv = csv.DictReader(open(f'{md_filepath}/toc.csv'))
    toc_csv_rows = list(toc_csv)

    assert 'Only Lesson' == toc_csv_rows[0]['activity_name']
    assert validate_uuid4(toc_csv_rows[0]['content_id'])
    assert 'Lesson Page 1' == toc_csv_rows[0]['lesson_page']
    assert 'Default Section' == toc_csv_rows[0]['section']

    assert 'Only Page' == toc_csv_rows[1]['activity_name']
    assert validate_uuid4(toc_csv_rows[1]['content_id'])
    assert '' == toc_csv_rows[1]['lesson_page']
    assert 'Default Section' == toc_csv_rows[1]['section']
