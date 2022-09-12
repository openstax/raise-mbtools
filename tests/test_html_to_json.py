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
HTML_VARIANT1 = (
    '<h1>no video</h1>'
    '<p>Some text</p>'
)

HTML_VARIANT2 = (
    '<h1>no interactive</h1>'
    '<p>Some text</p>'
)


@pytest.fixture
def file_path(tmp_path):
    (tmp_path / 'html_directory').mkdir()
    (tmp_path / 'html_directory' / 'variantdir').mkdir()

    (tmp_path / 'json_directory').mkdir()
    (tmp_path / 'html_directory' / "fragment.html").write_text(HTML_FRAGMENT1)
    (tmp_path / 'html_directory' / "fragment2.html").write_text(HTML_FRAGMENT2)
    (tmp_path / 'html_directory' / 'variantdir' /
     'variant1.html').write_text(HTML_VARIANT1)
    (tmp_path / 'html_directory' / 'variantdir' /
     'variant2.html').write_text(HTML_VARIANT2)

    return tmp_path

@pytest.fixture
def correct_file_path(tmp_path):
    (tmp_path / 'html_directory').mkdir()
    (tmp_path / 'html_directory' / 'variantdir').mkdir()

    (tmp_path / 'json_directory').mkdir()
    (tmp_path / 'html_directory' / "fragment.html").write_text(HTML_FRAGMENT1)
    (tmp_path / 'html_directory' / "variant.html").write_text(HTML_FRAGMENT1)

    (tmp_path / 'html_directory' / "fragment2.html").write_text(HTML_FRAGMENT2)
    (tmp_path / 'html_directory' / 'variant' /
     'variant1.html').write_text(HTML_VARIANT1)
    (tmp_path / 'html_directory' / 'variant' /
     'variant2.html').write_text(HTML_VARIANT2)

    return tmp_path

def get_json_content(file_path):
    content_in_json = []
    for file in os.listdir(f"{file_path}"):
        if file.endswith(".json"):
            with open(f'{file_path}/{file}') as f:
                content_in_json.append(f.read())
    return content_in_json


def test_json_file_created(file_path):
    html_to_json(f'{file_path}/html_directory', f'{file_path}/json_directory')
    assert ("fragment.json" in os.listdir(f'{file_path}/json_directory'))
    assert ("fragment2.json" in os.listdir(f'{file_path}/json_directory'))
    assert ("variantdir.json" in os.listdir(f'{file_path}/json_directory'))


def test_html_in_json(file_path):
    html_to_json(f'{file_path}/html_directory', f'{file_path}/json_directory')
    content_in_json = get_json_content(f'{file_path}/json_directory')
    # json dumps to escape html content
    assert any(json.dumps(HTML_FRAGMENT1) in s for s in content_in_json)
    assert any(json.dumps(HTML_FRAGMENT2) in s for s in content_in_json)
    assert any(json.dumps(HTML_VARIANT1) in s for s in content_in_json)
    assert any(json.dumps(HTML_VARIANT2) in s for s in content_in_json)


def test_json_content_is_valid(file_path):
    html_to_json(f'{file_path}/html_directory', f'{file_path}/json_directory')
    content_in_json = get_json_content(f'{file_path}/json_directory')
    # json files are valid json
    for content in content_in_json:
        assert json.loads(content)


def test_main(file_path, mocker):
    # Test for main function called by the CLI.
    mocker.patch(
        "sys.argv",
        ["", f"{file_path}/html_directory", f"{file_path}/json_directory"]
    )
    main()
    json_files = []
    for file in os.listdir(f"{file_path}/json_directory"):
        if file.endswith(".json"):
            json_files.append(Path(file).stem)
    assert len(json_files) == 3
