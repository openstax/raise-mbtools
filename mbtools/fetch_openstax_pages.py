from pathlib import Path
from functools import lru_cache
import argparse
import csv
import requests
from lxml import etree


BOOKS_BY_SLUG = {
    "elementary-algebra-2e": {
        "uuid": "55931856-c627-418b-a56f-1dd0007683a8",
        "code_version": "20220228.174637",
        "book_version": "97c23b7"
    },
    "intermediate-algebra-2e": {
        "uuid": "4664c267-cd62-4a99-8b28-1cb9b3aee347",
        "code_version": "20220228.174637",
        "book_version": "97c23b7"
    }
}

CSV_PAGE_URL = "page_url"


def parse_book_slug(page_url):
    """Parse a book slug given a page URL"""

    return page_url.split("openstax.org/books/")[1].split("/")[0]


def parse_page_slug(page_url):
    """Parse a page slug given a page URL"""

    return page_url.split("/")[-1]


def get_base_url(code_version):
    """Generate the base URL for book content given a code version"""
    return f"https://openstax.org/apps/archive/{code_version}"


@lru_cache
def get_book_json(base_url, book_uuid, book_version):
    """Get the book JSON

    Note: This function memoizes to avoid fetching the same book JSON
    multiple times
    """

    book_url = f"{base_url}/contents/{book_uuid}@{book_version}.json"

    res = requests.get(book_url)
    res.raise_for_status()
    return res.json()


def get_page_json(base_url, book_uuid, book_version, page_uuid):
    """Get the page JSON"""
    page_url = \
        f"{base_url}/contents/{book_uuid}@{book_version}:{page_uuid}.json"

    print(f"Getting page {page_url}")
    res = requests.get(page_url)
    res.raise_for_status()
    return res.json()


def parse_tree_for_page_uuid(tree, page_slug):
    """Given a tree parse for the page UUID"""

    curr_slug = tree["slug"]
    if curr_slug == page_slug:
        # Return page UUID accounting for the fact that sometimes the value
        # has a trailing version "@"
        return tree["id"].split("@")[0]
    if "contents" in tree:
        for node in tree["contents"]:
            page_uuid = parse_tree_for_page_uuid(node, page_slug)
            if page_uuid:
                return page_uuid
    return None


def fix_page_resources(page_tree, resource_url_prefix):
    """Fixes page resource URLs and return a list of all references as the
    sha1 values
    """
    resources = set()

    for elem in page_tree.xpath("//*[contains(@src, '../resources')]"):
        # This bakes in the knowledge / assumption that we upload resource
        # files as the sha1 of the content for books
        resource_sha1 = elem.get("src").split("../resources/")[1]
        resources.add(resource_sha1)
        elem.attrib["src"] = f"{resource_url_prefix}/{resource_sha1}"

    return resources


def write_page_xhtml(page_tree, book_slug, page_slug, output_dir):
    """Save page XHTML file"""
    contents_dir = output_dir / "contents" / book_slug
    contents_dir.mkdir(parents=True, exist_ok=True)

    with (contents_dir / f"{page_slug}.xhtml").open("wb") as outfile:
        outfile.write(etree.tostring(page_tree, encoding="utf-8"))


def fetch_resource(base_url, resource_sha1, output_dir):
    """Download resource file"""
    resource_url = f"{base_url}/resources/{resource_sha1}"
    resources_dir = output_dir / "resources"
    resources_dir.mkdir(parents=True, exist_ok=True)
    resource_outfile = resources_dir / resource_sha1

    # Check if the file exists just in case an image is used across multiple
    # pages to avoid a fetch
    if resource_outfile.exists():
        return

    res = requests.get(resource_url)
    res.raise_for_status()

    with resource_outfile.open("wb") as outfile:
        outfile.write(res.content)


def process_page(page_url, output_dir, resource_url_prefix):
    """Fetch / fix a page and return resource sha1 list"""
    print(f"Processing page: {page_url}")
    book_slug = parse_book_slug(page_url)
    page_slug = parse_page_slug(page_url)

    try:
        book_data = BOOKS_BY_SLUG[book_slug]
    except KeyError:
        raise Exception(f"Unsupported book slug: {book_slug}")

    book_uuid = book_data["uuid"]
    book_version = book_data["book_version"]
    code_version = book_data["code_version"]

    base_url = get_base_url(code_version)
    book_json = get_book_json(base_url, book_uuid, book_version)

    page_uuid = parse_tree_for_page_uuid(book_json["tree"], page_slug)
    if page_uuid is None:
        raise Exception("Page slug not found in book JSON")

    page_json = get_page_json(base_url, book_uuid, book_version, page_uuid)
    page_tree = etree.fromstring(page_json['content'])
    resources = fix_page_resources(page_tree, resource_url_prefix)

    write_page_xhtml(page_tree, book_slug, page_slug, output_dir)

    print("Downloading resource files...")
    for resource in resources:
        fetch_resource(base_url, resource, output_dir)


def main():
    parser = argparse.ArgumentParser(description="Fetch OpenStax book pages")
    parser.add_argument(
        "input_csv",
        type=str,
        help="Input CSV with columns: page_url"
    )
    parser.add_argument(
        "output_dir",
        type=str,
        help="Output directory"
    )
    parser.add_argument(
        "resource_url_prefix",
        type=str,
        help="URL prefix to use when fixing resource links"
    )
    args = parser.parse_args()

    input_csv = Path(args.input_csv).resolve(strict=True)
    output_dir = Path(args.output_dir).resolve(strict=True)
    resource_url_prefix = args.resource_url_prefix

    with input_csv.open() as csv_file:
        pages = csv.DictReader(csv_file)

        for page in pages:
            process_page(page[CSV_PAGE_URL], output_dir, resource_url_prefix)


if __name__ == "__main__":
    main()
