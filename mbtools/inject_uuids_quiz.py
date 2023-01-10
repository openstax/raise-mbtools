from mbtools import models, utils
from pathlib import Path
import argparse


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('mbz_path', type=str,
                        help='relative path to unzipped mbz')
    args = parser.parse_args()
    mbz_path = Path(args.mbz_path).resolve(strict=True)


    question_bank = models.MoodleQuestionBank(mbz_path)

    question_bank.inject_question_uuids()
    
    utils.write_etree(question_bank.questionbank_path, question_bank.etree)


if __name__ == "__main__":  # pragma: no cover
    main()
