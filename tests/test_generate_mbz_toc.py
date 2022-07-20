import mbtools.extract_html_content
from mbtools.generate_mbz_toc import main


def test_toc_activity_order_and_content(
    mocker, tmp_path, page_builder, lesson_builder, mbz_builder
):
    activities = []
    sections = []
    page_html = "<div><p>Page</p></div>"
    for indx in range(1):
        activities.append(page_builder(
            section_id=2,
            id=indx,
            name="4 Page",
            html_content=page_html
        ))

    lesson_1_name = "1 Lesson Page"
    lesson_2_name = "2 Lesson Page"
    lesson_3_name = "3 Lesson Page"
    lesson_1_html = f"<div><p>{lesson_1_name} content</p></div>"
    lesson_2_html = f"<div><p>{lesson_2_name} content</p></div>"
    lesson_3_html = f"<div><p>{lesson_3_name} content</p></div>"
    for indx in range(2):
        activities.append(lesson_builder(
            section_id=indx,
            id=indx,
            name="Lesson",
            pages=[
                {
                    "id": 1,
                    "title": lesson_1_name,
                    "html_content": lesson_1_html,
                    "prevpageid": 0,
                    "nextpageid": 2
                },
                {
                    "id": 2,
                    "title": lesson_2_name,
                    "html_content": lesson_2_html,
                    "prevpageid": 1,
                    "nextpageid": 3,
                },
                {
                    "id": 3,
                    "title": lesson_3_name,
                    "html_content": lesson_3_html,
                    "prevpageid": 2,
                    "nextpageid": 0,
                }
            ]
        ))

    sections.extend([{
            "id": 1,
            "title": "First Section"
        },
        {
            "id": 2,
            "title": "Second Section"
        }])

    mbz_path = tmp_path / "mbz"
    html_path = tmp_path / "html"
    html_path.mkdir()

    mbz_builder(mbz_path, activities=activities, sections=sections)
    mbtools.extract_html_content.replace_content_tags(mbz_path, html_path)

    md_file = "toc.md"
    mocker.patch(
        "sys.argv",
        ["", f"{mbz_path}", str(tmp_path / md_file)]
    )
    main()
    lines = []
    with open((tmp_path / md_file), 'r') as fp:
        lines = [line.rstrip() for line in fp]

    ordering_list = []
    entries = {}
    for line in lines:
        if (len(line.split("](")) > 1):
            name = line.split("](")[0].strip('* [')
            link = line.split("](")[1].split(')')[0]
            entries[name] = link
            ordering_list.append(name)

    pre_list = ordering_list
    ordering_list.sort()
    assert pre_list == ordering_list

    for name in entries.keys():
        path = str(tmp_path) + entries[name].strip('.')
        with open(path, 'r') as f:
            if ('Lesson' in name):
                content = f.read()
                assert name in content
            else:
                content = f.read()
                assert page_html in content


def test_sections_in_right_order(
    mocker, tmp_path, page_builder, lesson_builder, mbz_builder
):
    activities = []
    sections = []
    page_html = "<div><p>Page</p></div>"
    lesson_html = "<div><p>Lesson page</p></div>"
    section_1_title = "Section One"
    section_2_title = "Section Two"
    section_3_title = "Section Three"

    activities.append(page_builder(
        section_id=1,
        id=1,
        name="Page 1",
        html_content=page_html
    ))

    activities.extend([
        lesson_builder(
            section_id=2,
            id=2,
            name="Lesson",
            pages=[
                {
                    "id": 1,
                    "title": "Lesson Page 2",
                    "html_content": lesson_html,
                    "prevpageid": 0,
                    "nextpageid": 0
                }
            ]
        ),
        lesson_builder(
            section_id=3,
            id=3,
            name="Lesson",
            pages=[
                {
                    "id": 3,
                    "title": "Lesson Page 3",
                    "html_content": lesson_html,
                    "prevpageid": 0,
                    "nextpageid": 0
                }
            ]
        )]
    )

    sections.extend([{
            "id": 1,
            "title": section_1_title
        },
        {
            "id": 2,
            "title": section_2_title
        },
        {
            "id": 3,
            "title": section_3_title
        }]
    )
    mbz_path = tmp_path / "mbz"
    html_path = tmp_path / "html"
    html_path.mkdir()

    mbz_builder(mbz_path, activities=activities, sections=sections)
    mbtools.extract_html_content.replace_content_tags(mbz_path, html_path)

    md_file = "toc.md"
    mocker.patch(
        "sys.argv",
        ["", f"{mbz_path}", str(tmp_path / md_file)]
    )
    main()

    lines = []
    with open((tmp_path / md_file), 'r') as fp:
        lines = [line.rstrip() for line in fp]
    found_first_section = False
    found_second_section = False
    found_third_section = False
    for line in lines:
        if section_1_title in line:
            assert found_first_section is False
            assert found_second_section is False
            assert found_third_section is False
            found_first_section = True
        if section_2_title in line:
            assert found_first_section is True
            assert found_second_section is False
            assert found_third_section is False
            found_second_section = True
        if section_3_title in line:
            assert found_first_section is True
            assert found_second_section is True
            assert found_third_section is False
            found_third_section = True
