from uuid import UUID
import pytest
from lxml import etree
from mbtools.models import MoodleQuestionBank

def validate_uuid4(uuid_string):
    try:
        val = UUID(uuid_string, version=4)
        return True

    except ValueError:
        return False

def test_inject_uuids(tmp_path):
    questionbank_xml = """
<?xml version="1.0" encoding="UTF-8"?>
<question_categories>
  <question_category id="1">
  <idnumber>$@NULL@$</idnumber>
    <question_bank_entries>
      <question_bank_entry id="1">
        <idnumber>$@NULL@$</idnumber>
        <question_version>
          <question_versions>
            <version>1</version>
            <questions>
              <question id="question1v1">
                <qtype></qtype>
              </question>
            </questions>
          </question_versions>
          <question_versions>
            <version>2</version>
            <questions>
              <question id="question1v2">
                <qtype></qtype>
              </question>
            </questions>
          </question_versions>
        </question_version>
     </question_bank_entry>
      <idnumber>$@NULL@$</idnumber>
      <question_bank_entry id="2">
      <idnumber>$@NULL@$</idnumber>
        <question_version>
          <question_versions>
            <version>11</version>
            <questions>
              <question id="question2v11">
                <qtype></qtype>
              </question>
            </questions>
          </question_versions>
        </question_version>
        <question_version>
          <question_versions>
            <version>10</version>
            <questions>
              <question id="question2v10">
                <qtype></qtype>
              </question>
            </questions>
          </question_versions>
        </question_version>
     </question_bank_entry>
    </question_bank_entries>
  </question_category>
</question_categories>
    """

    (tmp_path / "questions.xml").write_text(questionbank_xml.strip())
    questionbank = MoodleQuestionBank(tmp_path)
    questionbank.inject_question_uuids()
    elems = questionbank.etree.xpath('//question_categories/question_category')
    for elem in elems:
        questions = elem.xpath(
            './question_bank_entries/question_bank_entry'
        )

        for question in questions:
            id_number =  question.findall(
            './/idnumber'
        )
            assert(validate_uuid4(id_number[0].text))
