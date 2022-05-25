from mbtools import models, utils
from pathlib import Path
import argparse


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('mbz_path', type=str,
                        help='relative path to unzipped mbz')
    args = parser.parse_args()
    mbz_path = Path(args.mbz_path).resolve(strict=True)

    quizzes = utils.parse_backup_quizzes(mbz_path)

    used_question_ids = set()

    for quiz in quizzes:
        used_question_ids.update(quiz.question_ids())

    question_bank = models.MoodleQuestionBank(mbz_path)

    question_bank.delete_unused_questions(used_question_ids)
    question_bank.delete_empty_categories()

    utils.write_etree(question_bank.questionbank_path, question_bank.etree)


if __name__ == "__main__":  # pragma: no cover
    main()
