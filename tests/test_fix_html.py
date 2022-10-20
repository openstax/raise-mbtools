from mbtools.fix_html import fix_html, main
import pytest

HTML = (
    '<h1>Header tag</h1>'
    '<h2></h2>'
    '<p></p>'
    '<p><span></span></p>'
    '<p><span lang="EN"></span></p>'
    '<p><span lang="EN">&nbsp;</span></p>'
    '<br>'
    '<br>'
    '<br><a>hello</a></br>'
    '<img src="w3html.gif" alt="W3Schools.com" width="100" />'
    '<p><img src="w3html.gif" alt="W3Schools.com" /></p>'

)

output_html = (
    '<h1>Header tag</h1>'
    '<br>'
    '<br>'
    '<br><a>hello</a>'
    '<img alt="W3Schools.com" src="w3html.gif" width="100">'
    '<p><img alt="W3Schools.com" src="w3html.gif"></p>'

)


@pytest.fixture
def file_path(tmp_path):

    html_directory = tmp_path / 'html_directory'

    html_directory.mkdir()
    (html_directory / "htmlfile.html").write_text(HTML)

    return html_directory


def test_remove_empty_elems(file_path):
    fix_html(str(file_path))
    content = ''
    with open(f'{file_path}/htmlfile.html') as f:
        content = f.read()

    assert (content == output_html)


def test_main(file_path, mocker):
    # Test for main function called by the CLI.
    mocker.patch(
        "sys.argv",
        ["", str(file_path)]
    )
    main()
    with open(f"{file_path}/htmlfile.html", 'r') as f:
        file = f.read()
        assert ('<h2></h2>' not in file)


def test_directories(file_path):
    (file_path / 'htmldir').mkdir()
    (file_path / 'htmldir' / 'content.html').write_text(HTML)
    fix_html(str(file_path))

    with open(f'{file_path}/htmlfile.html') as f:
        content = f.read()

    assert (content == output_html)

    with open(f'{file_path}/htmldir/content.html') as f:
        content = f.read()

    assert (content == output_html)
