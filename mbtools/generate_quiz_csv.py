import argparse
from collections import defaultdict
import os
import csv
from mbtools import utils
from pathlib import Path


def write_quiz_csvs(
    quizzes_csv, quiz_questions_csv, quiz_multichoice_answers_csv, output_path
):
    with open(output_path / "quizzes.csv", "w") as outfile:
        writer = csv.writer(outfile)
        writer = csv.writer(outfile)
        writer.writerow(quizzes_csv.keys())
        writer.writerows(zip(*quizzes_csv.values()))

    with open(output_path / "quiz_questions.csv", "w") as outfile:
        writer = csv.writer(outfile)
        writer = csv.writer(outfile)
        writer.writerow(quiz_questions_csv.keys())
        writer.writerows(zip(*quiz_questions_csv.values()))

    with open(output_path / "quiz_multichoice_answers.csv", "w") as outfile:
        writer = csv.writer(outfile)
        writer = csv.writer(outfile)
        writer.writerow(quiz_multichoice_answers_csv.keys())
        writer.writerows(zip(*quiz_multichoice_answers_csv.values()))


def order_questions(quiz):
    # Organize Questions by Order
    pages = defaultdict(list)
    for question in quiz.quiz_questions:
        pages[question.page].append(question)
    for page in pages.values():
        page.sort(key=lambda h: h.slot)
    ordered_questions = []
    ordered_keys = list(pages.keys())
    ordered_keys.sort()
    for key in ordered_keys:
        ordered_questions.extend(pages[key])
    return ordered_questions


def generate_quiz_data(mbz_path, output_path):
    question_bank = utils.parse_moodle_questionbank(mbz_path)
    quizzes = utils.parse_backup_quizzes(mbz_path)

    quizzes_csv = {
        "quiz_name": [],
        "question_number": [],
        "question_id": []
    }
    quiz_questions_csv = {
        "id": [],
        "text": [],
        "type": []
    }
    quiz_multichoice_answers_csv = {
        "id": [],
        "question_id": [],
        "text": [],
        "grade": [],
        "feedback": []
    }

    answer_number = 0
    for quiz in quizzes:
        ordered_questions = order_questions(quiz)

        question_number = 0

        for moodle_question in ordered_questions:
            q_bank_question = \
                question_bank.get_question_by_entry(
                    question_bank_entry_id=moodle_question.qbank_entry_id,
                    version=moodle_question.version
                )

            id_number = q_bank_question.id_number
            text = q_bank_question.etree.xpath('./questiontext')[0].text
            question_type = q_bank_question.question_type

            quizzes_csv["quiz_name"].append(quiz.name)
            quizzes_csv["question_number"].append(question_number)
            quizzes_csv["question_id"].append(id_number)

            if id_number not in quiz_questions_csv["id"]:
                quiz_questions_csv["id"].append(id_number)
                quiz_questions_csv["text"].append(text)
                quiz_questions_csv["type"].append(question_type)

                if question_type == 'multichoice':
                    for answer in q_bank_question.multichoice_answers():
                        answer_text = answer.answer_html_element().tostring()
                        feedback = ""
                        if answer.feedback_html_element() is not None:
                            feedback = \
                                answer.feedback_html_element().tostring()
                        grade = answer.grade

                        quiz_multichoice_answers_csv["id"].append(
                            answer_number)
                        quiz_multichoice_answers_csv["question_id"].append(
                            id_number)
                        quiz_multichoice_answers_csv["text"].append(
                            answer_text)
                        quiz_multichoice_answers_csv["grade"].append(
                            grade)
                        quiz_multichoice_answers_csv["feedback"].append(
                            feedback)
                        answer_number += 1
            question_number += 1

    write_quiz_csvs(
        quizzes_csv,
        quiz_questions_csv,
        quiz_multichoice_answers_csv,
        output_path
    )


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('mbz_path', type=str,
                        help='relative path to unzipped mbz')
    parser.add_argument('output_dir', type=str,
                        help='relative path output dir')
    args = parser.parse_args()
    mbz_path = Path(args.mbz_path).resolve(strict=True)
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)
    output_path = Path(args.output_dir).resolve(strict=True)

    generate_quiz_data(mbz_path, output_path)


if __name__ == "__main__":
    main()
