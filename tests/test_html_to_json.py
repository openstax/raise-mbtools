import os
from mbtools.html_to_json import html_to_json
import pytest

HTML_FRAGMENT1 = (
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
HTML_FRAGMENT2 = (
    '<h1>Some Header</h1>'
    '<p>Some text</p>'
)


@pytest.fixture
def html_path(tmp_path):
    html_dir = tmp_path
    (html_dir / "fragment.html").write_text(HTML_FRAGMENT1)
    (html_dir / "fragment2.html").write_text(HTML_FRAGMENT2)

    return tmp_path

def test_json_file_created(html_path):
    for file in os.listdir(f"{html_path}"):
        if file.endswith(".html"):
            print(file)
    html_to_json(f'{html_path}', f'{html_path}')
    assert("fragment.json" in os.listdir(f'{html_path}'))
    assert("fragment2.json" in os.listdir(f'{html_path}'))


def test_json_file_content(html_path):
    content_in_html = []
    html_to_json(f'{html_path}', f'{html_path}')

    for file in os.listdir(f"{html_path}"):
        if file.endswith(".html"):
            with open(f'{html_path}/{file.split(".")[0]}.json') as f:
                content_in_html.append(f.read())

    assert ""