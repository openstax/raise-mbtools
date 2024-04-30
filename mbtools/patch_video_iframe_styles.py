import argparse
from pathlib import Path
from mbtools import utils
from bs4 import BeautifulSoup


def wrap_elements_in_div(html_file):
    with open(html_file, "r") as f:
        should_write = False
        soup = BeautifulSoup(f.read(), "html.parser")
        for tag in ["iframe", "video"]:
            elements = soup.find_all(tag)

            for element in elements:

                if not element.find_parent(class_='os-raise-video-container'):
                    div_wrapper = soup.new_tag(
                        "div", **{"class": "os-raise-video-container"}
                    )
                    element.wrap(div_wrapper)
                    center_wrapper = soup.new_tag(
                        "div",
                        **{
                            "class": ("os-raise-d-flex-nowrap "
                                      "os-raise-justify-content-center ")
                        }
                    )
                    div_wrapper.wrap(center_wrapper)
                    should_write = True

                for attribute in ["width", "height"]:
                    if element.get(attribute) is not None:
                        del element[attribute]
                        should_write = True

        return soup, should_write


def update_media_styles(html_dir):
    for path in Path(html_dir).glob("*.html"):
        updated_soup, should_write = wrap_elements_in_div(path)
        if should_write:
            utils.write_html_soup(path, updated_soup)


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("html_directory", type=str,
                        help="path to HTML files")

    args = parser.parse_args()
    html_directory = Path(args.html_directory).resolve(strict=True)
    update_media_styles(html_directory)


if __name__ == "__main__":  # pragma: no cover
    main()
