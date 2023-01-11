from uuid import UUID
from mbtools.models import MoodleQuestionBank
from mbtools.inject_uuids import main


def validate_uuid4(uuid_string):
    try:
        UUID(uuid_string, version=4)
        return True

    except ValueError:
        return False


def test_inject_uuids(tmp_path, mocker):
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

    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}"]
    )

    main()

    questionbank = MoodleQuestionBank(tmp_path)
    elems = questionbank.etree.xpath('//question_categories/question_category')
    for elem in elems:
        questions = elem.xpath(
            './question_bank_entries/question_bank_entry'
        )

        for question in questions:
            id_number = question.findall('.//idnumber')
            assert (validate_uuid4(id_number[0].text))


def test_parent_idnumber_unchanged(tmp_path, mocker):
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

    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}"]
    )

    main()

    questionbank = MoodleQuestionBank(tmp_path)
    elems = questionbank.etree.xpath('//question_categories/question_category')
    for elem in elems:
        questions = elem.xpath(
            './question_bank_entries'
        )

        for question in questions:
            id_number = question.findall('idnumber')
            assert (id_number[0].text == '$@NULL@$')


def test_existing_id_unchanged(tmp_path, mocker):
    questionbank_xml = """
<?xml version="1.0" encoding="UTF-8"?>
<question_categories>
  <question_category id="1">
  <idnumber>$@NULL@$</idnumber>
    <question_bank_entries>
      <question_bank_entry id="1">
        <idnumber>25754128-6ef7-4f58-ac79-d9538375739d</idnumber>
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
        <idnumber>25754128-6ef7-4f58-ac79-d9538375739d</idnumber>
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

    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}"]
    )

    main()

    questionbank = MoodleQuestionBank(tmp_path)
    elems = questionbank.etree.xpath('//question_categories/question_category')
    for elem in elems:
        questions = elem.xpath(
            './question_bank_entries/question_bank_entry'
        )

        for question in questions:
            id_number = question.findall('idnumber')
            assert (id_number[0].text ==
                    '25754128-6ef7-4f58-ac79-d9538375739d')
