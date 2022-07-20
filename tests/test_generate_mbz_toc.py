import mbtools.extract_html_content
from mbtools.generate_mbz_toc import main


def test_generate_toc_from_mbz(
    mocker, tmp_path, page_builder, lesson_builder, mbz_builder
):
    activities = []
    sections = []
    page_html = "<div><p>Page</p></div>"
    lesson_html = "<div><p>Lesson page</p></div>"
    for indx in range(1):
        activities.append(page_builder(
            section_id=1,
            id=indx,
            name="Page",
            html_content=page_html
        ))

    for indx in range(2):
        activities.append(lesson_builder(
            section_id=1,
            id=indx,
            name="Lesson",
            pages=[
                {
                    "id": 1,
                    "title": "2 Lesson Page",
                    "html_content": lesson_html,
                    "prevpageid": 0,
                    "nextpageid": 2
                },
                {
                    "id": 2,
                    "title": "3 Lesson Page",
                    "html_content": lesson_html,
                    "prevpageid": 1,
                    "nextpageid": 3,
                },
                {
                    "id": 3,
                    "title": "1 Lesson Page",
                    "html_content": lesson_html,
                    "prevpageid": 2,
                    "nextpageid": 0,
                }
            ]
        ))

    sections.append({
        "id": 1,
        "title": "First Section"
        })

    mbz_path = tmp_path / "mbz"
    html_path = tmp_path / "html"
    html_path.mkdir()

    mbz_builder(mbz_path, activities=activities)
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
    entries = {}
    for line in lines:
        if (len(line.split("](")) > 1):
            name = line.split("](")[0].strip('[')
            link = line.split("](")[1].split(')')[0]
            entries[name] = link

    for name in entries.keys():
        path = str(tmp_path) + entries[name].strip('.')
        with open(path, 'r') as f:
            if ('Lesson' in name):
                content = f.read()
                assert lesson_html in content
            else:
                content = f.read()
                assert page_html in content
