from mbtools import remove_styles
from lxml import etree
from mbtools.models import MoodleHtmlElement


def test_remove_styles_from_main(
    tmp_path, mbz_builder, page_builder, lesson_builder, mocker
):
    content_with_styles = \
        '<p style="text-align: left; color=blue; font-size: 10px">Text</p>'
    page1 = page_builder(2, "Page", content_with_styles)
    lesson2 = lesson_builder(
        id=1,
        name="Lesson",
        pages=[
            {
                "id": 21,
                "title": "Lesson 1 Page 1",
                "html_content": content_with_styles
            },
            {
                "id": 22,
                "title": "Lesson 1 Page 2",
                "html_content": content_with_styles,
                "answers": [
                    {
                        "id": 221,
                        "html_content": content_with_styles,
                        "response": content_with_styles
                    },
                    {
                        "id": 222,
                        "html_content": content_with_styles,
                        "response": content_with_styles
                    }
                ]
            }
        ]
    )
    mbz_builder(tmp_path, [page1, lesson2])

    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}"]
    )
    remove_styles.main()
    with open(f"{tmp_path}/activities/lesson_1/lesson.xml", 'r') as f:
        file = f.read()
        assert ('style' not in file)
    with open(f"{tmp_path}/activities/page_2/page.xml", 'r') as f:
        file = f.read()
        assert ('style' not in file)


def test_styles_removed_from_html():
    location = "here"
    parent = etree.fromstring("<content></content>")
    parent.text = (
        '<p dir="ltr" style="color: blue">'
        '(6, 0)'
        '<br>'
        '</p>'
        '<p style="text-align: left">'
        'words'
        '</p>'
        '<p style="text-align: center">'
        'words'
        '</p>'
    )
    elem = MoodleHtmlElement(parent, location)
    elem.remove_attr("style")
    assert (elem.tostring() == (
            '<p dir="ltr">'
            '(6, 0)'
            '<br>'
            '</p>'
            '<p>'
            'words'
            '</p>'
            '<p>'
            'words'
            '</p>'))
    assert len(elem.etree_fragments) == 3
