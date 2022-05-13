import pytest
import html
from string import Template

ANSWER_TEXT_TEMPLATE = Template("""
<answer id="$id">
  <answer_text>$content</answer_text>
</answer>
""")

LESSON_PAGE_TEMPLATE = Template("""
<page id="$id">
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
  <questionid>$questionid</questionid>
</question_instance>
""")

MOODLE_ACTIVITY_TEMPLATE = Template("""
<activity>
  <modulename>$activity_type</modulename>
  <directory>activities/${activity_type}_$id</directory>
</activity>
""")

MOODLE_BACKUP_TEMPLATE = Template("""
<?xml version="1.0" encoding="UTF-8"?>
<moodle_backup>
  <contents>
    <activities>
      $activitydata
    </activities>
  </contents>
</moodle_backup>
""")

QUESTION_TEMPLATE = Template("""
<question id="$id">
  <questiontext>$content</questiontext>
  <answers>
    $answerdata
  </answers>
</question>
""")

QUESTION_BANK_TEMPLATE = Template("""
<?xml version="1.0" encoding="UTF-8"?>
<question_categories>
  <question_category>
    <questions>
      $questiondata
    </questions>
  </question_category>
</question_categories>
""")


@pytest.fixture
def mbz_builder():
    def _builder(tmp_path, activities, questionbank_questions=[]):
        activitydata = ""
        for act in activities:
            activity_id = act["id"]
            activity_type = act["activity_type"]
            activitydata += MOODLE_ACTIVITY_TEMPLATE.substitute(
                id=activity_id,
                activity_type=activity_type
            )
            activity_dir = \
                tmp_path / f"activities/{activity_type}_{activity_id}"
            activity_path = activity_dir / f"{activity_type}.xml"
            activity_dir.mkdir(parents=True)
            activity_path.write_text(act["xml_content"].strip())

        questiondata = ""
        for question in questionbank_questions:
            answerdata = ""
            for ans in question.get("answers", []):
                answerdata += ANSWER_TEXT_TEMPLATE.substitute(
                    id=ans["id"],
                    content=html.escape(ans["html_content"])
                )
            questiondata += QUESTION_TEMPLATE.substitute(
                id=question["id"],
                content=html.escape(question["html_content"]),
                answerdata=answerdata
            )

        questionbank_xml = QUESTION_BANK_TEMPLATE.substitute(
            questiondata=questiondata
        )
        (tmp_path / "questions.xml").write_text(questionbank_xml.strip())

        moodle_backup_xml = MOODLE_BACKUP_TEMPLATE.substitute(
            activitydata=activitydata
        )
        (tmp_path / "moodle_backup.xml").write_text(moodle_backup_xml.strip())

    return _builder


@pytest.fixture
def lesson_page_builder():
    def _builder(id, html_content, answers=[]):
        answerdata = ""
        for ans in answers:
            answerdata += ANSWER_TEXT_TEMPLATE.substitute(
                id=ans["id"],
                content=html.escape(ans["html_content"])
            )
        return LESSON_PAGE_TEMPLATE.substitute(
            id=id,
            content=html.escape(html_content),
            answerdata=answerdata
        )
    return _builder


@pytest.fixture
def lesson_builder(lesson_page_builder):
    def _builder(id, name, pages=[]):
        pagedata = ""

        for page in pages:
            pagedata += lesson_page_builder(
                id=page["id"],
                html_content=page["html_content"],
                answers=page.get("answers", [])
            )

        lesson_content = LESSON_TEMPLATE.substitute(
            id=id,
            name=name,
            pagedata=pagedata
        )

        return {
            "id": id,
            "activity_type": "lesson",
            "xml_content": lesson_content
        }
    return _builder


@pytest.fixture
def page_builder():
    def _builder(id, name, html_content):
        page_content = PAGE_TEMPLATE.substitute(
            id=id,
            name=name,
            content=html.escape(html_content)
        )

        return {
            "id": id,
            "activity_type": "page",
            "xml_content": page_content
        }

    return _builder


@pytest.fixture
def quiz_builder():
    def _builder(id, name, questions=[]):
        questiondata = ""
        for question in questions:
            questiondata += QUIZ_QUESTION_TEMPLATE.substitute(
                id=question["id"],
                questionid=question["questionid"]
            )

        quiz_content = QUIZ_TEMPLATE.substitute(
            id=id,
            name=name,
            questiondata=questiondata
        )

        return {
            "id": id,
            "activity_type": "quiz",
            "xml_content": quiz_content
        }

    return _builder
