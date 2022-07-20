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

    used_qbank_entry_ids = set()

    for quiz in quizzes:
        used_qbank_entry_ids.update(quiz.used_qbank_entry_ids())

    question_bank = models.MoodleQuestionBank(mbz_path)

    question_bank.delete_unused_question_bank_entries(used_qbank_entry_ids)
    question_bank.delete_empty_categories()

    utils.write_etree(question_bank.questionbank_path, question_bank.etree)


if __name__ == "__main__":  # pragma: no cover
    main()
