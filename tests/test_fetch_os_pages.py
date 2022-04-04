import csv
import pytest
from mbtools import fetch_openstax_pages
from lxml import etree


def test_parsing_slugs():
    page_url = "https://openstax.org/books/book-slug/pages/page-slug"
    page_slug = fetch_openstax_pages.parse_page_slug(page_url)
    book_slug = fetch_openstax_pages.parse_book_slug(page_url)

    assert page_slug == "page-slug"
    assert book_slug == "book-slug"


def test_get_base_url():
    url = fetch_openstax_pages.get_base_url("some-code-version")
    assert url == "https://openstax.org/apps/archive/some-code-version"


def test_tree_parsing():
    book_tree = {
        "tree": {
            "id": "",
            "slug": "",
            "contents": [
                {
                    "id": "8887d5ce-d27c-4456-b39a-60131517af46@",
                    "slug": "slug0"
                },
                {
                    "id": "d83e3095-1633-43b8-aefe-c7d14729c02e",
                    "slug": "slug1"
                }
            ]
        }
    }

    page_id = fetch_openstax_pages.parse_tree_for_page_uuid(
        book_tree["tree"],
        "slug0"
    )
    assert page_id == "8887d5ce-d27c-4456-b39a-60131517af46"

    page_id = fetch_openstax_pages.parse_tree_for_page_uuid(
        book_tree["tree"],
        "slug1"
    )
    assert page_id == "d83e3095-1633-43b8-aefe-c7d14729c02e"


def test_get_book_json_memoization(requests_mock):
    base_url = "https://openstax.mock"
    book_uuid = "bookuuid"
    book_version = "bookversion"

    requests_mock.get(
        f"{base_url}/contents/{book_uuid}@{book_version}.json",
        json={}
    )

    fetch_openstax_pages.get_book_json(base_url, book_uuid, book_version)

    assert requests_mock.call_count == 1

    # Make the same request and confirm the mock is not invoked again
    fetch_openstax_pages.get_book_json(base_url, book_uuid, book_version)

    assert requests_mock.call_count == 1


def test_fix_page_resources():
    page_content = '''
    <html>
      <body>
        <div>
          <p>Some content</p>
          <img src="../resources/resource_sha1"
          id="test_img1"
          data-media-type="image/jpeg"
          alt="No Alt Text"/>
        </div>
      </body>
    </html>
    '''

    page_tree = etree.fromstring(page_content)
    resources = fetch_openstax_pages.fix_page_resources(
        page_tree,
        "https://urlprefix"
    )

    assert resources == set(["resource_sha1"])
    assert page_tree.xpath("//img[@id='test_img1']")[0].attrib["src"] == \
        "https://urlprefix/resource_sha1"


def test_fetch_resource(requests_mock, tmp_path):
    base_url = "https://openstax.mock"
    resource_sha1 = "resource_sha1"
    output_dir = tmp_path / "fetched_content"
    resource_content = b"123456789abcdef"

    requests_mock.get(
        f"{base_url}/resources/{resource_sha1}",
        content=resource_content
    )

    fetch_openstax_pages.fetch_resource(base_url, resource_sha1, output_dir)
    assert requests_mock.call_count == 1
    resource_data =  \
        (tmp_path / "fetched_content/resources/resource_sha1").read_bytes()
    assert resource_data == resource_content

    # Confirm that requesting the same resource doesn't result in another
    # network request
    fetch_openstax_pages.fetch_resource(base_url, resource_sha1, output_dir)
    assert requests_mock.call_count == 1


def test_fetch_os_pages(requests_mock, tmp_path, mocker):
    input_csv_path = tmp_path / "input.csv"
    output_path = tmp_path / "output"
    resource_url_prefix = "https://openstax.mock/contents/raise/resources"
    elem_alg_2e_prefix = "https://openstax.org/books/elementary-algebra-2e"
    intermediate_alg_2e_prefix = \
        "https://openstax.org/books/intermediate-algebra-2e"
    elem_alg_2e_book = \
        fetch_openstax_pages.BOOKS_BY_SLUG['elementary-algebra-2e']
    intermediate_alg_2e_book = \
        fetch_openstax_pages.BOOKS_BY_SLUG['intermediate-algebra-2e']
    elem_alg_2e_json = {
        "tree": {
            "id": "",
            "slug": "",
            "contents": [
                {
                    "id": "58723c65-289c-4279-8e74-6065b2544a00@",
                    "slug": "slug1"
                }
            ]
        }
    }

    intermediate_alg_2e_json = {
        "tree": {
            "id": "",
            "slug": "",
            "contents": [
                {
                    "id": "d4bec0b6-08ba-42d2-9049-b5ce4db05e04@",
                    "slug": "slug1"
                }
            ]
        }
    }

    page_content = '''
    <html>
      <body>
        <div>
          <p>Some content</p>
          <img src="../resources/resource_sha1"
          id="test_img1"
          data-media-type="image/jpeg"
          alt="No Alt Text"/>
        </div>
      </body>
    </html>
    '''
    resource_content = b"123456789abcdef"

    output_path.mkdir()
    with input_csv_path.open("w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["page_url"])
        writer.writeheader()
        writer.writerows([
            {"page_url": f"{elem_alg_2e_prefix}/pages/slug1"},
            {"page_url": f"{intermediate_alg_2e_prefix}/pages/slug1"}
        ])

    # Mocks for book JSON files
    requests_mock.get(
        f"https://openstax.org/apps/archive/{elem_alg_2e_book['code_version']}"
        f"/contents/{elem_alg_2e_book['uuid']}"
        f"@{elem_alg_2e_book['book_version']}.json",
        json=elem_alg_2e_json
    )

    requests_mock.get(
        "https://openstax.org/apps/archive/"
        f"{intermediate_alg_2e_book['code_version']}"
        f"/contents/{intermediate_alg_2e_book['uuid']}"
        f"@{intermediate_alg_2e_book['book_version']}.json",
        json=intermediate_alg_2e_json
    )

    # Mocks for page JSON files
    requests_mock.get(
        f"https://openstax.org/apps/archive/{elem_alg_2e_book['code_version']}"
        f"/contents/{elem_alg_2e_book['uuid']}"
        f"@{elem_alg_2e_book['book_version']}:"
        "58723c65-289c-4279-8e74-6065b2544a00.json",
        json={"content": page_content}
    )

    requests_mock.get(
        "https://openstax.org/apps/archive/"
        f"{intermediate_alg_2e_book['code_version']}"
        f"/contents/{intermediate_alg_2e_book['uuid']}"
        f"@{intermediate_alg_2e_book['book_version']}:"
        "d4bec0b6-08ba-42d2-9049-b5ce4db05e04.json",
        json={"content": page_content}
    )

    # Mocks for resource data
    requests_mock.get(
        "https://openstax.org/apps/archive/"
        f"{elem_alg_2e_book['code_version']}"
        f"/resources/resource_sha1",
        content=resource_content
    )

    requests_mock.get(
        "https://openstax.org/apps/archive/"
        f"{intermediate_alg_2e_book['code_version']}"
        f"/resources/resource_sha1",
        content=resource_content
    )

    mocker.patch(
        "sys.argv",
        ["", str(input_csv_path), str(output_path), resource_url_prefix]
    )

    fetch_openstax_pages.main()

    # Check XHTML file outputs
    elem_alg_2e_slug1_xhtml = \
        (output_path / "contents/elementary-algebra-2e/slug1.xhtml")
    intermediate_alg_2e_slug1_xhtml = \
        (output_path / "contents/intermediate-algebra-2e/slug1.xhtml")
    assert elem_alg_2e_slug1_xhtml.exists()
    assert intermediate_alg_2e_slug1_xhtml.exists()

    for xhtml_filepath in [
        elem_alg_2e_slug1_xhtml,
        intermediate_alg_2e_slug1_xhtml
    ]:
        with xhtml_filepath.open() as xhtml_file:
            xhtml_tree = etree.parse(xhtml_file)
            img_elem = xhtml_tree.xpath("//img[@id='test_img1']")[0]
            assert img_elem.attrib["src"] == \
                f"{resource_url_prefix}/resource_sha1"

    # Check resource file output
    resource_output = (output_path / "resources/resource_sha1")
    assert resource_output.exists()

    resource_data = resource_output.read_bytes()
    assert resource_data == resource_content


def test_process_page_bad_book_slug(tmp_path):
    output_path = tmp_path / "output"
    bad_book_slug_prefix = "https://openstax.org/books/unknownbook"

    with pytest.raises(Exception, match="Unsupported book slug"):
        fetch_openstax_pages.process_page(
            f"{bad_book_slug_prefix}/pages/slug1",
            output_path,
            "https://mock"
        )


def test_process_page_bad_page_slug(tmp_path, requests_mock):
    output_path = tmp_path / "output"
    elem_alg_2e_prefix = "https://openstax.org/books/elementary-algebra-2e"
    elem_alg_2e_book = \
        fetch_openstax_pages.BOOKS_BY_SLUG['elementary-algebra-2e']
    elem_alg_2e_json = {
        "tree": {
            "id": "",
            "slug": "",
            "contents": [
                {
                    "id": "58723c65-289c-4279-8e74-6065b2544a00@",
                    "slug": "slug0"
                }
            ]
        }
    }

    # Force clearing the memoized cache on function to be sure the mock data
    # is returned
    fetch_openstax_pages.get_book_json.cache_clear()

    requests_mock.get(
        f"https://openstax.org/apps/archive/{elem_alg_2e_book['code_version']}"
        f"/contents/{elem_alg_2e_book['uuid']}"
        f"@{elem_alg_2e_book['book_version']}.json",
        json=elem_alg_2e_json
    )

    with pytest.raises(Exception, match="Page slug not found in book JSON"):
        fetch_openstax_pages.process_page(
            f"{elem_alg_2e_prefix}/pages/slug1",
            output_path,
            "https://mock"
        )

    assert requests_mock.call_count == 1
