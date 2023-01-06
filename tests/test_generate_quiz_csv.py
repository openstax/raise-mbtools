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
                "slot": 1,
                "page": 1,
                "questionid": 2
            },
            {
                "id": 33,
                "slot": 1,
                "page": 2,
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
                "slot": 1,
                "page": 1,
                "questionid": 1
            },
            {
                "id": 32,
                "slot": 1,
                "page": 2,
                "questionid": 2
            },
            {
                "id": 33,
                "slot": 1,
                "page": 3,
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

    with open(f"{output_dir}/quizzes.csv", mode='r')as file:
        csvFile = csv.reader(file)
        all_rows = []
        for line in csvFile:
            all_rows.append(line)
        assert(all_rows ==
               [['quiz_name', 'question_number', 'question_id'],
                ['Quiz 1', '0', '1234'],
                ['Quiz 2', '0', '1235'],
                ['Quiz 2', '1', '1236'],
                ['Quiz 3', '0', '1234'],
                ['Quiz 3', '1', '1235'],
                ['Quiz 3', '2', '1236']])

    with open(f"{output_dir}/quiz_questions.csv", mode='r')as file:
        csvFile = csv.reader(file)
        all_rows = []
        for line in csvFile:
            all_rows.append(line)
        assert(all_rows ==
               [['id', 'text', 'type'],
                ['1234', '<p>Question 1 Content</p>', 'multichoice'],
                ['1235', '<p>Question 2 Content</p>', 'multichoice'],
                ['1236', '<p>Question 3 Content</p>', 'multichoice']])

    with open(f"{output_dir}/quiz_multichoice_answers.csv", mode='r')as file:
        csvFile = csv.reader(file)
        all_rows = []
        for line in csvFile:
            all_rows.append(line)
        assert(all_rows ==
               [['id', 'question_id', 'text', 'grade', 'feedback'],
                ['0', '1234', '<p>q1 answer 1</p>', '1.0', ''],
                ['1', '1234', '<p>q1 answer 2</p>', '0.0', ''],
                ['2', '1235', '<p>q2 answer 1</p>', '0.0', ''],
                ['3', '1235', '<p>q2 answer 2</p>', '1.0', ''],
                ['4', '1236', '<p>q3 answer 1</p>', '0.0', ''],
                ['5', '1236', '<p>q3 answer 2</p>', '1.0', '']])
