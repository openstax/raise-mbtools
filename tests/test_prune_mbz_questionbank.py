from mbtools import prune_mbz_questionbank
from lxml import etree


def test_prune_mbz_questionbank(
    tmp_path, mbz_builder, quiz_builder, mocker
):
    quiz1 = quiz_builder(
        id=1,
        name="Quiz 1",
        questions=[
            {
                "id": 31,
                "questionid": 1
            },
            {
                "id": 32,
                "questionid": 2
            }
        ]
    )

    quiz2 = quiz_builder(
        id=2,
        name="Quiz 2",
        questions=[
            {
                "id": 31,
                "questionid": 3
            }
        ]
    )

    mbz_builder(
        tmp_path,
        activities=[quiz1, quiz2],
        questionbank_questions=[
            {
                "id": 1,
                "html_content": "<p>Question 1</p>"
            },
            {
                "id": 2,
                "html_content": "<p>Question 2</p>"
            },
            {
                "id": 3,
                "html_content": "<p>Question 3</p>"
            },
            {
                "id": 4,
                "html_content": "<p>Question 4</p>"
            },
        ]
    )

    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}"]
    )

    prune_mbz_questionbank.main()

    questionbank_etree = etree.parse(f"{tmp_path / 'questions.xml'}")
    questions = questionbank_etree.xpath("//questions/question")
    categories = questionbank_etree.xpath("//question_category")
    assert len(questions) == 3
    assert len(categories) == 1


def test_prune_mbz_questionbank_no_quizzes(
    tmp_path, mbz_builder, mocker
):
    mbz_builder(
        tmp_path,
        activities=[],
        questionbank_questions=[
            {
                "id": 1,
                "html_content": "<p>Question 1</p>"
            },
            {
                "id": 2,
                "html_content": "<p>Question 2</p>"
            },
            {
                "id": 3,
                "html_content": "<p>Question 3</p>"
            },
            {
                "id": 4,
                "html_content": "<p>Question 4</p>"
            },
        ]
    )

    mocker.patch(
        "sys.argv",
        ["", f"{tmp_path}"]
    )

    prune_mbz_questionbank.main()

    questionbank_etree = etree.parse(f"{tmp_path / 'questions.xml'}")
    questions = questionbank_etree.xpath("//questions/question")
    categories = questionbank_etree.xpath("//question_category")
    assert len(questions) == 0
    assert len(categories) == 0
