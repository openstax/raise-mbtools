import json
import os
from pathlib import Path

from mbtools.html_to_json import html_to_json, main
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
def file_path(tmp_path):
    html_dir = tmp_path
    (html_dir / "fragment.html").write_text(HTML_FRAGMENT1)
    (html_dir / "fragment2.html").write_text(HTML_FRAGMENT2)

    return tmp_path


def get_json_content(file_path):
    content_in_json = []
    for file in os.listdir(f"{file_path}"):
        if file.endswith(".json"):
            with open(f'{file_path}/{file}') as f:
                content_in_json.append(f.read())
    return content_in_json


def test_json_file_created(file_path):
    html_to_json(f'{file_path}', f'{file_path}')
    assert("fragment.json" in os.listdir(f'{file_path}'))
    assert("fragment2.json" in os.listdir(f'{file_path}'))


def test_html_in_json(file_path):
    html_to_json(f'{file_path}', f'{file_path}')
    content_in_json = get_json_content(file_path)

    # json dumps to escape html content
    assert any(json.dumps(HTML_FRAGMENT1) in s for s in content_in_json)
    assert any(json.dumps(HTML_FRAGMENT2) in s for s in content_in_json)


def test_json_content_is_valid(file_path):
    html_to_json(f'{file_path}', f'{file_path}')
    content_in_json = get_json_content(file_path)
    # json files are valid json
    for content in content_in_json:
        assert json.loads(content)


def test_main(file_path, mocker):
    # Test for main function called by the CLI.
    mocker.patch(
        "sys.argv",
        ["", f"{file_path}", f"{file_path}"]
    )
    main()
    json_files = []
    for file in os.listdir(f"{file_path}"):
        if file.endswith(".json"):
            json_files.append(Path(file).stem)
    assert len(json_files) == 2
