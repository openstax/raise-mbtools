import os
from mbtools.patch_video_iframe_styles import main
from bs4 import BeautifulSoup
import mbtools
import mbtools.extract_html_content


def test_patch_video_iframe_styles(mocker, tmp_path, mbz_builder,
                                   lesson_builder):
    lesson_name = "Only Lesson"
    lesson_html_1 = """  <iframe class="os-raise-iframe" allow="accelerometer;
        autoplay; clipboard-write; encrypted-media;
        gyroscope; picture-in-picture"
        allowfullscreen frameborder="0"
        height="303" width="1000"
        src="https://www.youtube.com/embed/sample"
        title="Linear equation word problems"></iframe>
         <iframe class="os-raise-iframe" allow="accelerometer;
        autoplay; clipboard-write; encrypted-media;
        gyroscope; picture-in-picture"
        allowfullscreen frameborder="0"
        height="303" width="1000"
        src="https://www.youtube.com/embed/sample"
        title="Linear equation word problems"></iframe>"""

    lesson_html_2 = """<video controls="true" crossorigin="anonymous">
        <source src="https://k12.openstax.org/contents/">
        <track default="true"
        kind="captions" label="On"
        height="303" width="1000"
        src="https://k12.openstax.org/"
        srclang="en_us">https://k12.openstax.org/
        </video>"""

    lesson_page_name_1 = "Practice Page 1"
    lesson_page_name_2 = "Practice Page 2"
    lesson = lesson_builder(
        id=1,
        name=lesson_name,
        pages=[
            {"id": "2", "title": lesson_page_name_2,
             "html_content": lesson_html_2},
            {"id": "1", "title": lesson_page_name_1,
             "html_content": lesson_html_1},
        ],
    )

    mbz_path = tmp_path / "mbz"
    html_path = tmp_path / "html"
    html_path.mkdir()
    mbz_builder(mbz_path, activities=[lesson])
    mbtools.extract_html_content.replace_content_tags(mbz_path, html_path)
    mocker.patch("sys.argv", ["", f"{html_path}"])
    main()
    for path, dirs, files in os.walk(html_path):
        for file in files:
            with open(f"{path}/{file}") as f:
                content = f.read()
                soup = BeautifulSoup(content, "html.parser")
                if soup.find("iframe"):
                    assert (
                        len(soup.find_all("div",
                                          class_="os-raise-video-container"))
                        == 2
                    )
                    assert (
                        len(soup.find_all("div",
                                          class_="os-raise-d-flex-nowrap"))
                        == 2
                    )

                assert soup.find("div", class_="os-raise-video-container")
                assert soup.find("div", class_="os-raise-d-flex-nowrap")
                assert soup.find("div",
                                 class_="os-raise-justify-content-center")

                video_tags = soup.find_all(["iframe", "video"])
                for tag in video_tags:
                    assert tag.get("width") is None
                    assert tag.get("height") is None
