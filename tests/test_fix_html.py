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
    '<br/>'
    '<br/>'
    '<br/><a>hello</a>'
    '<img alt="W3Schools.com" src="w3html.gif" width="100"/>'
    '<p><img alt="W3Schools.com" src="w3html.gif"/></p>'
)


@pytest.fixture
def file_path(tmp_path):

    (tmp_path / 'html_directory').mkdir()
    (tmp_path / 'html_directory' / "htmlfile.html").write_text(HTML)

    return tmp_path


def test_json_file_created(file_path):
    fix_html(f'{file_path}/html_directory')
    content = ''
    with open(f'{file_path}/html_directory/htmlfile.html') as f:
        content = f.read()

    assert (content == output_html)


def test_main(file_path, mocker):
    # Test for main function called by the CLI.
    mocker.patch(
        "sys.argv",
        ["", f"{file_path}/html_directory"]
    )
    main()
    with open(f"{file_path}/html_directory/htmlfile.html", 'r') as f:
        file = f.read()
        assert ('<h2></h2>' not in file)
