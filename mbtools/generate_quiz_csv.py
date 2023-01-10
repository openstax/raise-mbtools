import argparse
import os
import csv
from mbtools import utils
from pathlib import Path
from mbtools import models


def write_quiz_csvs(
    quiz_questions_csv,
    quiz_question_contents_csv,
    quiz_multichoice_answers_csv,
    output_path
):
    with open(output_path / "quiz_questions.csv", "w") as outfile:
        headers = quiz_questions_csv[0].keys()
        result = csv.DictWriter(outfile, fieldnames=headers)
        result.writeheader()
        result.writerows(quiz_questions_csv)

    with open(output_path / "quiz_question_contents.csv", "w") as outfile:
        headers = quiz_question_contents_csv[0].keys()
        result = csv.DictWriter(outfile, fieldnames=headers)
        result.writeheader()
        result.writerows(quiz_question_contents_csv)

    with open(output_path / "quiz_multichoice_answers.csv", "w") as outfile:
        if len(quiz_multichoice_answers_csv) != 0:
            headers = quiz_multichoice_answers_csv[0].keys()
        else:
            headers = ["question_id", "text", "grade", "feedback"]
        result = csv.DictWriter(outfile, fieldnames=headers)
        result.writeheader()
        result.writerows(quiz_multichoice_answers_csv)


def order_questions(quiz):
    # Organize Questions by Order
    questions = quiz.quiz_questions
    return sorted(questions, key=lambda q: q.slot)


def generate_quiz_data(mbz_path, output_path):
    question_bank = models.MoodleQuestionBank(mbz_path)
    quizzes = utils.parse_backup_quizzes(mbz_path)

    quiz_questions_csv = []
    quiz_question_contents_csv = []
    quiz_multichoice_answers_csv = []

    moodle_questions = []
    for quiz in quizzes:
        ordered_questions = order_questions(quiz)

        question_number = 1

        for moodle_question in ordered_questions:
            q_bank_question = \
                question_bank.get_question_by_entry(
                    question_bank_entry_id=moodle_question.qbank_entry_id,
                    version=moodle_question.version
                )

            id_number = q_bank_question.id_number
            text = q_bank_question.text
            question_type = q_bank_question.question_type
            quiz_questions_csv.append(
                {"quiz_name": quiz.name,
                 "question_number": question_number,
                 "question_id": id_number
                 })

            entry_id_version = \
                (moodle_question.qbank_entry_id,
                 moodle_question.version)
            if entry_id_version in moodle_questions:
                print("Warning: duplicate question. \
                    Not appending to quiz_question_contents")
            else:
                moodle_questions.append(entry_id_version)
                quiz_question_contents_csv.append({
                    "id": id_number,
                    "text": text,
                    "type": question_type
                    })

                if question_type == 'multichoice':
                    for answer in q_bank_question.multichoice_answers():
                        answer_text = answer.text
                        feedback = answer.feedback
                        grade = answer.grade

                        quiz_multichoice_answers_csv.append({
                            "question_id": id_number,
                            "text": answer_text,
                            "grade": grade,
                            "feedback": feedback
                        })
            question_number += 1

    write_quiz_csvs(
        quiz_questions_csv,
        quiz_question_contents_csv,
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
