import json
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
    (tmp_path / 'html_directory' / 'variant').mkdir()

    (tmp_path / 'json_directory').mkdir()
    (tmp_path / 'html_directory' / "fragment.html").write_text(HTML_FRAGMENT1)
    (tmp_path / 'html_directory' / "variant.html").write_text(HTML_FRAGMENT1)

    (tmp_path / 'html_directory' / "fragment2.html").write_text(HTML_FRAGMENT2)
    (tmp_path / 'html_directory' / 'variant' /
     'variant1.html').write_text(HTML_VARIANT1)
    (tmp_path / 'html_directory' / 'variant' /
     'variant2.html').write_text(HTML_VARIANT2)

    return tmp_path


@pytest.fixture
def incorrect_file_path(tmp_path):
    # File path without variant main file in root html directory.
    (tmp_path / 'html_directory').mkdir()
    (tmp_path / 'html_directory' / 'variant').mkdir()

    (tmp_path / 'json_directory').mkdir()
    (tmp_path / 'html_directory' / "fragment.html").write_text(HTML_FRAGMENT1)

    (tmp_path / 'html_directory' / "fragment2.html").write_text(HTML_FRAGMENT2)
    (tmp_path / 'html_directory' / 'variant' /
     'variant1.html').write_text(HTML_VARIANT1)
    (tmp_path / 'html_directory' / 'variant' /
     'variant2.html').write_text(HTML_VARIANT2)

    return tmp_path


def get_json_content(file_path, content_id, variant):
    json_dir = file_path / 'json_directory'
    content = json.load(open(str(json_dir / f'{content_id}.json')))['content']
    for entry in content:
        if entry['variant'] == variant:
            return entry['html']


def test_json_file_created(file_path):
    html_to_json(f'{file_path}/html_directory', f'{file_path}/json_directory')
    assert (Path(f'{file_path}/json_directory/fragment.json').exists())
    assert (Path(f'{file_path}/json_directory/fragment2.json').exists())
    assert (Path(f'{file_path}/json_directory/variant.json').exists())


def test_json_file_created_incorrect_path(incorrect_file_path):
    html_to_json(f'{incorrect_file_path}/html_directory',
                 f'{incorrect_file_path}/json_directory')

    assert (Path(f'{incorrect_file_path}/json_directory/fragment.json')
            .exists())
    assert (Path(f'{incorrect_file_path}/json_directory/fragment2.json')
            .exists())
    assert (not Path(f'{incorrect_file_path}/json_directory/variant.json')
            .exists())


def test_html_in_json(file_path):
    html_to_json(f'{file_path}/html_directory', f'{file_path}/json_directory')
    # content_in_json = get_json_content(f'{file_path}/json_directory')
    # json dumps to escape html content
    assert get_json_content(file_path, 'fragment', 'main') == HTML_FRAGMENT1
    assert get_json_content(file_path, 'fragment2', 'main') == HTML_FRAGMENT2
    assert get_json_content(file_path, 'variant', 'variant1') == HTML_VARIANT1
    assert get_json_content(file_path, 'variant', 'variant2') == HTML_VARIANT2


def test_main(file_path, mocker):
    # Test for main function called by the CLI.
    mocker.patch(
        "sys.argv",
        ["", f"{file_path}/html_directory", f"{file_path}/json_directory"]
    )
    main()
    json_files = []
    for file in Path(f"{file_path}/json_directory").iterdir():
        if file.name.endswith(".json"):
            json_files.append(Path(file.name).stem)
    assert len(json_files) == 3
