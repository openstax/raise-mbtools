from mbtools import utils


def test_parse_backup_activities(
    tmp_path, mbz_builder, page_builder, lesson_builder, quiz_builder
):
    page = page_builder(id=1, name="Page 1", html_content="<p>page 1</p>")
    lesson = lesson_builder(id=2, name="Lesson 2")
    quiz = quiz_builder(id=3, name="Quiz 3")
    mbz_builder(tmp_path, [page, lesson, quiz])
    activities = utils.parse_backup_activities(tmp_path)
    assert len(activities) == 3


def test_parse_backup_quizzes(
    tmp_path, mbz_builder, page_builder, lesson_builder, quiz_builder
):
    page = page_builder(id=1, name="Page 1", html_content="<p>page 1</p>")
    lesson = lesson_builder(id=2, name="Lesson 2")
    quiz = quiz_builder(id=3, name="Quiz 3")
    mbz_builder(tmp_path, [page, lesson, quiz])
    activities = utils.parse_backup_quizzes(tmp_path)
    assert len(activities) == 1


def test_parse_activity_html_contents(
    tmp_path, mbz_builder, page_builder, lesson_builder, quiz_builder
):
    lesson1_page1_content = "<div><p>Lesson 1 Page 1</p></div>"
    lesson1_page2_content = "<div><p>Lesson 1 Page 2</p></div>"
    lesson1_page2_answer1_content = "<p>L1 P2 A1</p>"
    lesson1_page2_answer2_content = "<p>L1 P2 A2</p>"
    lesson1_page2_answer1_response = "<p>L1 P2 A1 R</p>"
    lesson1_page2_answer2_response = "<p>L1 P2 A1 R</p>"
    page2_content = "<div><p>Page 2</p></div>"
    qb_question1_content = "<p>Question 1</p>"
    qb_question1_answer1_content = "<p>answer 1</p>"
    qb_question1_answer2_content = "<p>answer 2</p>"
    qb_question2_content = "<p>Question 2</p>"
    qb_question3_content = "<p>Question 3</p>"

    lesson1 = lesson_builder(
        id=1,
        name="Lesson 1",
        pages=[
            {
                "id": 11,
                "title": "Lesson 1 Page 1",
                "html_content": lesson1_page1_content
            },
            {
                "id": 12,
                "title": "Lesson 1 Page 2",
                "html_content": lesson1_page2_content,
                "answers": [
                    {
                        "id": 111,
                        "html_content": lesson1_page2_answer1_content,
                        "response": lesson1_page2_answer1_response
                    },
                    {
                        "id": 112,
                        "html_content": lesson1_page2_answer2_content,
                        "response": lesson1_page2_answer2_response
                    }
                ]
            }
        ]
    )
    page2 = page_builder(id=2, name="Page 2", html_content=page2_content)
    quiz3 = quiz_builder(
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
            }
        ]
    )

    mbz_builder(
        tmp_path,
        activities=[lesson1, page2, quiz3],
        questionbank_questions=[
            {
                "id": 1,
                "idnumber": 1234,
                "html_content": qb_question1_content,
                "answers": [
                    {
                        "id": 11,
                        "grade": 0,
                        "html_content": qb_question1_answer1_content,
                    },
                    {
                        "id": 12,
                        "grade": 1,
                        "html_content": qb_question1_answer2_content,
                    }
                ]
            },
            {
                "id": 2,
                "idnumber": 1235,
                "html_content": qb_question2_content
            },
            {
                "id": 3,
                "idnumber": 1236,
                "html_content": qb_question3_content
            }
        ]
    )

    activities = utils.parse_backup_activities(tmp_path)

    parsed_html_content_strings = []
    for act in activities:
        for html_elem in act.html_elements():
            parsed_html_content_strings.append(
                html_elem.tostring()
            )
    assert set([
        lesson1_page1_content,
        lesson1_page2_content,
        lesson1_page2_answer1_content,
        lesson1_page2_answer2_content,
        lesson1_page2_answer1_response,
        lesson1_page2_answer2_response,
        page2_content,
        qb_question1_content,
        qb_question1_answer1_content,
        qb_question1_answer2_content,
        qb_question2_content,
    ]) == set(parsed_html_content_strings)


def test_find_question_html(tmp_path, mbz_builder):
    qb_question1_content = "<p>Question 1</p>"
    qb_question1_answer1_content = "<p>answer 1</p>"
    qb_question1_answer2_content = "<p>answer 2</p>"
    qb_question2_content = "<p>Question 2</p>"
    qb_question3_content = "<p>Question 3</p>"
    qb_question3_match1_question = "<p>Match 1</p>"
    qb_question3_match2_question = "<p>Match 1</p>"

    mbz_builder(
        tmp_path,
        activities=[],
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
                "html_content": qb_question2_content
            },
            {
                "id": 3,
                "idnumber": 1236,
                "html_content": qb_question3_content,
                "matches": [
                    {
                        "id": 1,
                        "answer_content": "Some non-HTML content",
                        "question_html_content": qb_question3_match1_question
                    },
                    {
                        "id": 2,
                        "answer_content": "Some non-HTML content",
                        "question_html_content": qb_question3_match2_question
                    }
                ]
            }
        ]
    )
    html_elements = utils.parse_question_bank_latest_for_html(tmp_path)
    html = []
    for elem in html_elements:
        html.append(elem.tostring())
    assert len(html) == 7
    assert set([
        qb_question1_content,
        qb_question1_answer1_content,
        qb_question1_answer2_content,
        qb_question2_content,
        qb_question3_content,
        qb_question3_match1_question,
        qb_question3_match2_question
    ]) == set(html)
