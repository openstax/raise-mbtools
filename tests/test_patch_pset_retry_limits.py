import os
from mbtools.patch_pset_retry_limits import main
import mbtools
import mbtools.extract_html_content


def test_toc_creation_lesson_pages_in_order(
    mocker, tmp_path, mbz_builder, lesson_builder
):
    lesson_name = "Only Lesson"
    # Lesson 1 is practice page with a multiple choice question
    lesson_html_1 = '''<div class="os-raise-ib-pset"
                        data-content-id="c05a82e9-1fb8-42d7-8613-a48a62ab66a0">
                        <!--Lesson 1-->
                        <div class="os-raise-ib-pset-problem"
                        data-content-id="c05a82e9-1fb8-42d7-8613-a48a62ab66a0"
                        data-problem-type="multiplechoice" data-retry-limit="7"
                        data-solution="solution"
                        data-solution-options='["solution", "solution1",
                                        "solution2",
                                        "solution3"]'></div></div>'''

    # lesson 2 is practice page with the retry limit will be set to 2
    lesson_html_2 = '''<div class="os-raise-ib-pset"
                        data-button-text="Check"
                        data-retry-limit="5"
                        data-content-id="c05a82e9-1fb8-42d7-8613-a48a62ab66a0"
                        data-schema-version="1.0">
                        <!-- Lesson 2 -->
                        </div>
                        '''
    # lesson 3 is not a practice page, data-retry-limit will be set to 0
    lesson_html_3 = '''<div class="os-raise-ib-pset"
                        data-button-text="Check"
                        data-content-id="c05a82e9-1fb8-42d7-8613-a48a62ab66a0"
                        data-schema-version="1.0">
                        <!--Lesson 3-->

                        </div>
                        '''
    lesson_page_name_1 = "Practice Page 1"
    lesson_page_name_2 = "Practice Page 2"
    lesson_page_name_3 = "Lesson Page 3"
    lesson = lesson_builder(
            id=1,
            name=lesson_name,
            pages=[
                {
                    "id": "3",
                    "title": lesson_page_name_3,
                    "html_content": lesson_html_3
                },
                {
                    "id": "2",
                    "title": lesson_page_name_2,
                    "html_content": lesson_html_2
                },
                {
                    "id": "1",
                    "title": lesson_page_name_1,
                    "html_content": lesson_html_1
                }
                ]
    )

    mbz_path = tmp_path / "mbz"
    html_path = tmp_path / "html"
    html_path.mkdir()
    mbz_builder(mbz_path, activities=[lesson])
    mbtools.extract_html_content.replace_content_tags(mbz_path, html_path)

    mocker.patch(
        "sys.argv",
        ["", f"{html_path}", str(mbz_path)]
    )
    main()
    for path, dirs, files in os.walk(html_path):
        for file in files:
            with open(f'{path}/{file}') as f:
                content = f.read()
                if "Lesson 1" in content:
                    assert 'data-retry-limit="2"' in content
                    assert 'data-retry-limit="3"' in content

                elif "Lesson 2" in content:
                    assert 'data-retry-limit="2"' in content

                elif "Lesson 3" in content:
                    assert 'data-retry-limit="0"' in content
