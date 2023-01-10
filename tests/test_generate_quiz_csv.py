from mbtools import generate_quiz_csv
import csv


def test_generate_quiz_csv(
    quiz_builder, mbz_builder, tmp_path, mocker
):

    qb_question1_content = '<p>Question 1 Content</p>'
    qb_question1_answer1_content = '<p>q1 answer 1</p>'
    qb_question1_answer2_content = '<p>q1 answer 2</p>'
    qb_question2_content = '<p>Question 2 Content</p>'
    qb_question2_answer1_content = '<p>q2 answer 1</p>'
    qb_question2_answer2_content = '<p>q2 answer 2</p>'
    qb_question3_content = "<p>Question 3 Content</p>"
    qb_question3_answer1_content = '<p>q3 answer 1</p>'
    qb_question3_answer2_content = '<p>q3 answer 2</p>'

    quiz_1 = quiz_builder(
        id=1,
        name="Quiz 1",
        questions=[
            {
                "id": 31,
                "slot": 1,
                "page": 1,
                "questionid": 1
            }
        ]
    )
    quiz_2 = quiz_builder(
        id=2,
        name="Quiz 2",
        questions=[
            {
                "id": 32,
                "slot": 2,
                "page": 2,
                "questionid": 2
            },
            {
                "id": 33,
                "slot": 1,
                "page": 1,
                "questionid": 3
            }
        ]
    )
    quiz_3 = quiz_builder(
        id=3,
        name="Quiz 3",
        questions=[
            {
                "id": 31,
                "slot": 2,
                "page": 1,
                "questionid": 1
            },
            {
                "id": 32,
                "slot": 3,
                "page": 1,
                "questionid": 2
            },
            {
                "id": 33,
                "slot": 1,
                "page": 1,
                "questionid": 3
            }
        ]
    )

    mbz_builder(
        tmp_path,
        activities=[quiz_1, quiz_2, quiz_3],
        questionbank_questions=[
            {
                "id": 1,
                "idnumber": 1234,
                "html_content": qb_question1_content,
                "answers": [
                    {
                        "id": 11,
                        "grade": 1,
                        "html_content": qb_question1_answer1_content
                    },
                    {
                        "id": 12,
                        "grade": 0,
                        "html_content": qb_question1_answer2_content
                    }
                ]
            },
            {
                "id": 2,
                "idnumber": 1235,
                "html_content": qb_question2_content,
                "answers": [
                    {
                        "id": 13,
                        "grade": 0,
                        "html_content": qb_question2_answer1_content
                    },
                    {
                        "id": 14,
                        "grade": 1,
                        "html_content": qb_question2_answer2_content
                    }
                ]

            },
            {
                "id": 3,
                "idnumber": 1236,
                "html_content": qb_question3_content,
                "answers": [
                    {
                        "id": 15,
                        "grade": 0,
                        "html_content": qb_question3_answer1_content
                    },
                    {
                        "id": 16,
                        "grade": 1,
                        "html_content": qb_question3_answer2_content
                    }
                ]
            }
        ]
    )

    output_dir = f"{tmp_path}/outputs"
    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}", output_dir]
    )

    generate_quiz_csv.main()

    with open(f"{output_dir}/quiz_questions.csv", mode='r')as file:
        csvFile = csv.reader(file)
        all_rows = []
        for line in csvFile:
            all_rows.append(line)
        assert (all_rows ==
               [['quiz_name', 'question_number', 'question_id'],
                ['Quiz 1', '1', '1234'],
                ['Quiz 2', '1', '1236'],
                ['Quiz 2', '2', '1235'],
                ['Quiz 3', '1', '1236'],
                ['Quiz 3', '2', '1234'],
                ['Quiz 3', '3', '1235']])

    with open(f"{output_dir}/quiz_question_contents.csv", mode='r')as file:
        csvFile = csv.reader(file)
        all_rows = []
        for line in csvFile:
            all_rows.append(line)
        assert (all_rows ==
               [['id', 'text', 'type'],
                ['1234', '<p>Question 1 Content</p>', 'multichoice'],
                ['1236', '<p>Question 3 Content</p>', 'multichoice'],
                ['1235', '<p>Question 2 Content</p>', 'multichoice']])

    with open(f"{output_dir}/quiz_multichoice_answers.csv", mode='r')as file:
        csvFile = csv.reader(file)
        all_rows = []
        for line in csvFile:
            all_rows.append(line)
        assert (all_rows ==
               [['question_id', 'text', 'grade', 'feedback'],
                ['1234', '<p>q1 answer 1</p>', '1.0', ''],
                ['1234', '<p>q1 answer 2</p>', '0.0', ''],
                ['1236', '<p>q3 answer 1</p>', '0.0', ''],
                ['1236', '<p>q3 answer 2</p>', '1.0', ''],
                ['1235', '<p>q2 answer 1</p>', '0.0', ''],
                ['1235', '<p>q2 answer 2</p>', '1.0', '']])


def test_generate_quiz_data_with_answer_feedback(tmp_path, mocker):
    moodle_backup_xml = """
<?xml version="1.0" encoding="UTF-8"?>
<moodle_backup>
  <information>
    <contents>
      <activities>
        <activity>
          <sectionid>1</sectionid>
          <modulename>quiz</modulename>
          <title>Unit 1, Section A Quiz</title>
          <directory>activities</directory>
        </activity>
      </activities>
    </contents>
  </information>
</moodle_backup>
    """.strip()

    question_bank_xml = """
<?xml version="1.0" encoding="UTF-8"?>
<question_categories>
  <question_category>
    <question_bank_entry id="124">
      <idnumber>1234</idnumber>
      <question_version>
        <question_versions>
          <version>1</version>
          <questions>
            <question id="3592">
                <questiontext>What is the Right Answer</questiontext>>
                <qtype>multichoice</qtype>
                <plugin_qtype_multichoice_question>
                  <answers>
                    <answer id="7760">
                      <answertext>'&lt;p&gt;Answ 1 Text&lt;/p&gt;'</answertext>
                      <fraction>0.0000000</fraction>
                      <feedback>'&lt;p&gt;Wrong&lt;/p&gt;'</feedback>
                    </answer>
                    <answer id="7761">
                      <answertext>'&lt;p&gt;Answ 2 Text&lt;/p&gt;'</answertext>
                      <fraction>1.0000000</fraction>
                      <feedback>'&lt;p&gt;Correct&lt;/p&gt;'</feedback>
                    </answer>
                    <answer id="7762">
                      <answertext>'&lt;p&gt;Answ 3 Text&lt;/p&gt;'</answertext>
                      <fraction>0.0000000</fraction>
                      <feedback>'&lt;p&gt;Wrong&lt;/p&gt;'</feedback>
                    </answer>
                    <answer id="7763">
                      <answertext>'&lt;p&gt;Answ 4 Text&lt;/p&gt;'</answertext>
                      <fraction>0.0000000</fraction>
                      <feedback>'&lt;p&gt;Wrong&lt;/p&gt;'</feedback>
                    </answer>
                  </answers>
                </plugin_qtype_multichoice_question>
              </question>
          </questions>
        </question_versions>
      </question_version>
    </question_bank_entry>
  </question_category>
</question_categories>
    """.strip()

    quiz_xml = """
<?xml version="1.0" encoding="UTF-8"?>
<activity id="1" modulename="quiz">
  <quiz id="2">
    <name>My Quiz</name>
    <question_instances>
      <question_instance id="124">
        <slot>1</slot>
        <page>1</page>
        <question_reference>
          <questionbankentryid>124</questionbankentryid>
          <version>$@NULL@$</version>
        </question_reference>
      </question_instance>
    </question_instances>
  </quiz>
</activity>
    """.strip()

    with open(tmp_path / "moodle_backup.xml", "w") as qb:
        qb.write(moodle_backup_xml)
    with open(tmp_path / "questions.xml", "w") as qb:
        qb.write(question_bank_xml)
    (tmp_path / "activities").mkdir()
    with open(tmp_path / "activities/quiz.xml", "w") as qb:
        qb.write(quiz_xml)

    output_dir = f"{tmp_path}/outputs"
    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}", output_dir]
    )

    generate_quiz_csv.main()

    with open(f"{output_dir}/quiz_questions.csv", mode='r')as file:
        csvFile = csv.reader(file)
        all_rows = []
        for line in csvFile:
            all_rows.append(line)
        assert (all_rows ==
               [['quiz_name', 'question_number', 'question_id'],
                ['My Quiz', '1', '1234']])

    with open(f"{output_dir}/quiz_question_contents.csv", mode='r')as file:
        csvFile = csv.reader(file)
        all_rows = []
        for line in csvFile:
            all_rows.append(line)
        assert (all_rows ==
               [['id', 'text', 'type'],
                ['1234', 'What is the Right Answer', 'multichoice']])

    with open(f"{output_dir}/quiz_multichoice_answers.csv", mode='r')as file:
        csvFile = csv.reader(file)
        all_rows = []
        for line in csvFile:
            all_rows.append(line)
        assert (all_rows ==
                [['question_id', 'text', 'grade', 'feedback'],
                 ['1234', "'<p>Answ 1 Text</p>'", '0.0', "'<p>Wrong</p>'"],
                 ['1234', "'<p>Answ 2 Text</p>'", '1.0', "'<p>Correct</p>'"],
                 ['1234', "'<p>Answ 3 Text</p>'", '0.0', "'<p>Wrong</p>'"],
                 ['1234', "'<p>Answ 4 Text</p>'", '0.0', "'<p>Wrong</p>'"]])
