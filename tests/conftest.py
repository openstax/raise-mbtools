import pytest
import html
from string import Template

DEFAULT_SECTION = {"id": "DEFAULT", "title": "Default Section"}

LESSON_ANSWER_TEXT_TEMPLATE = Template("""
<answer id="$id">
  <answerformat>1</answerformat>
  <answer_text>$content</answer_text>
  <response>$response</response>
  <responseformat>1</responseformat>
</answer>
""")

LESSON_PAGE_TEMPLATE = Template("""
<page id="$id">
  <title>$title</title>
  <prevpageid>$prevpageid</prevpageid>
  <nextpageid>$nextpageid</nextpageid>
  <contents>$content</contents>
  <answers>
    $answerdata
  </answers>
</page>
""")

LESSON_TEMPLATE = Template("""
<?xml version="1.0" encoding="UTF-8"?>
<activity id="$id" modulename="lesson">
  <lesson id="$id">
    <name>$name</name>
    <pages>
      $pagedata
    </pages>
  </lesson>
</activity>
""")

PAGE_TEMPLATE = Template("""
<?xml version="1.0" encoding="UTF-8"?>
<activity id="$id" modulename="page">
  <page id="$id">
    <name>$name</name>
    <content>$content</content>
  </page>
</activity>
""")

QUIZ_TEMPLATE = Template("""
<?xml version="1.0" encoding="UTF-8"?>
<activity id="$id" modulename="quiz">
  <quiz id="$id">
    <name>$name</name>
    <question_instances>
      $questiondata
    </question_instances>
  </quiz>
</activity>
""")

QUIZ_QUESTION_TEMPLATE = Template("""
<question_instance id="$id">
  <slot>$slot</slot>
  <page>$page</page>
  <question_reference>
    <questionbankentryid>$questionid</questionbankentryid>
    <version>$@NULL@$</version>
  </question_reference>
</question_instance>
""")

MOODLE_ACTIVITY_TEMPLATE = Template("""
<activity>
  <sectionid>$section_id</sectionid>
  <modulename>$activity_type</modulename>
  <directory>activities/${activity_type}_$id</directory>
</activity>
""")

MOODLE_SECTION_TEMPLATE = Template("""
  <section>
    <sectionid>$section_id</sectionid>
    <title>$title</title>
  </section>
""")

MOODLE_BACKUP_TEMPLATE = Template("""
<?xml version="1.0" encoding="UTF-8"?>
<moodle_backup>
  <contents>
    <activities>
      $activitydata
    </activities>
    <sections>
      $section_data
    </sections>
  </contents>
</moodle_backup>
""")

QUESTION_TEMPLATE = Template("""
<question_bank_entry id="$id">
  <idnumber>$idnumber</idnumber>
  <question_version>
    <question_versions>
      <version>1</version>
      <questions>
        <question id="questionid$id">
          <questiontext>$content</questiontext>
          <qtype>multichoice</qtype>
          <plugin_qtype_multichoice_question>
            <answers>
              $answerdata
            </answers>
          </plugin_qtype_multichoice_question>
          <plugin>
            <matches>
              $matchdata
            </matches>
          </plugin>
        </question>
    </questions>
    </question_versions>
  </question_version>
</question_bank_entry>
""")

QUESTION_BANK_TEMPLATE = Template("""
<?xml version="1.0" encoding="UTF-8"?>
<question_categories>
  <question_category>
    <question_bank_entries>
      $questiondata
    </question_bank_entries>
  </question_category>
</question_categories>
""")

QUESTION_BANK_ANSWER_TEXT_TEMPLATE = Template("""
<answer id="$id">
  <answertext>$content</answertext>
  <fraction>$grade</fraction>
  <feedback></feedback>
</answer>
""")

QUESTION_BANK_MATCH_TEXT_TEMPLATE = Template("""
<match id="$id">
  <answertext>$answercontent</answertext>
  <questiontext>$questioncontent</questiontext>
</match>
""")

MODULE_TEMPLATE = Template("""<?xml version="1.0" encoding="UTF-8"?>
<module>
  <visible>$visible</visible>
</module>
""")


@pytest.fixture
def mbz_builder():
    def _builder(
        tmp_path, activities, sections=[DEFAULT_SECTION],
        questionbank_questions=[]
    ):
        tmp_path.mkdir(parents=True, exist_ok=True)
        activitydata = ""
        section_data = ""
        for act in activities:
            activity_id = act["id"]
            activity_section_id = act["section_id"]
            activity_type = act["activity_type"]
            activitydata += MOODLE_ACTIVITY_TEMPLATE.substitute(
                section_id=activity_section_id,
                id=activity_id,
                activity_type=activity_type
            )
            activity_dir = \
                tmp_path / f"activities/{activity_type}_{activity_id}"
            activity_path = activity_dir / f"{activity_type}.xml"
            module_path = activity_dir / "module.xml"
            activity_dir.mkdir(parents=True)
            activity_path.write_text(act["xml_content"].strip())
            module_data = MODULE_TEMPLATE.substitute(
              visible='1'
            )
            module_path.write_text(module_data)
        for sect in sections:
            section_id = sect["id"]
            section_title = sect["title"]
            section_data += MOODLE_SECTION_TEMPLATE.substitute(
                section_id=section_id,
                title=section_title
            )

        questiondata = ""
        for question in questionbank_questions:
            answerdata = ""
            matchdata = ""
            for ans in question.get("answers", []):
                answerdata += QUESTION_BANK_ANSWER_TEXT_TEMPLATE.substitute(
                    id=ans["id"],
                    grade=ans["grade"],
                    content=html.escape(ans["html_content"])
                )
            for match in question.get("matches", []):
                matchdata += QUESTION_BANK_MATCH_TEXT_TEMPLATE.substitute(
                    id=match["id"],
                    answercontent=match["answer_content"],
                    questioncontent=html.escape(match["question_html_content"])
                )
            questiondata += QUESTION_TEMPLATE.substitute(
                id=question["id"],
                idnumber=question["idnumber"],
                content=html.escape(question["html_content"]),
                answerdata=answerdata,
                matchdata=matchdata
            )

        questionbank_xml = QUESTION_BANK_TEMPLATE.substitute(
            questiondata=questiondata
        )
        (tmp_path / "questions.xml").write_text(questionbank_xml.strip())

        moodle_backup_xml = MOODLE_BACKUP_TEMPLATE.substitute(
            activitydata=activitydata,
            section_data=section_data
        )
        (tmp_path / "moodle_backup.xml").write_text(moodle_backup_xml.strip())

    return _builder


@pytest.fixture
def lesson_page_builder():
    def _builder(
      id, title, html_content, prevpageid=1, nextpageid=1, answers=[]
    ):
        answerdata = ""
        for ans in answers:
            answerdata += LESSON_ANSWER_TEXT_TEMPLATE.substitute(
                id=ans["id"],
                content=html.escape(ans["html_content"]),
                response=html.escape(ans["response"])
            )
        return LESSON_PAGE_TEMPLATE.substitute(
            id=id,
            title=title,
            content=html.escape(html_content),
            prevpageid=prevpageid,
            nextpageid=nextpageid,
            answerdata=answerdata
        )
    return _builder


@pytest.fixture
def lesson_builder(lesson_page_builder):
    def _builder(id, name, pages=[], section_id=DEFAULT_SECTION["id"]):
        pagedata = ""

        llist = {}
        for idx in range(0, len(pages)):
            next = ""
            prev = ""
            if idx == len(pages) - 1:
                next = "0"
            if idx == 0:
                prev = "0"
            if next == "":
                next = pages[idx + 1]["id"]
            if prev == "":
                prev = pages[idx - 1]["id"]
            llist[pages[idx]["id"]] = {"next": next, "prev": prev}

        for page in pages:
            pagedata += lesson_page_builder(
                id=page["id"],
                title=page["title"],
                html_content=page["html_content"],
                prevpageid=llist[page["id"]]["prev"],
                nextpageid=llist[page["id"]]["next"],
                answers=page.get("answers", [])
            )

        lesson_content = LESSON_TEMPLATE.substitute(
            id=id,
            name=name,
            pagedata=pagedata
        )

        return {
            "section_id": section_id,
            "id": id,
            "activity_type": "lesson",
            "xml_content": lesson_content
        }
    return _builder


@pytest.fixture
def page_builder():
    def _builder(id, name, html_content, section_id=DEFAULT_SECTION["id"]):
        page_content = PAGE_TEMPLATE.substitute(
            id=id,
            name=name,
            content=html.escape(html_content)
        )

        return {
            "section_id": section_id,
            "id": id,
            "activity_type": "page",
            "xml_content": page_content
        }

    return _builder


@pytest.fixture
def quiz_builder():
    def _builder(id, name, questions=[], section_id=DEFAULT_SECTION["id"]):
        questiondata = ""
        for question in questions:
            questiondata += QUIZ_QUESTION_TEMPLATE.safe_substitute(
                id=question["id"],
                slot=question["slot"],
                page=question["page"],
                questionid=question["questionid"]
            )

        quiz_content = QUIZ_TEMPLATE.substitute(
            id=id,
            name=name,
            questiondata=questiondata
        )

        return {
            "section_id": section_id,
            "id": id,
            "activity_type": "quiz",
            "xml_content": quiz_content
        }

    return _builder
