import argparse
from pathlib import Path
import csv
import re


LOCATION_COLUMN_NAME = "DescriptionOfLocation"
URL_COLUMN_NAME = "URL"


def create_url_indexes(toc_data):
    teacher_lesson_by_name = {}
    student_lesson_by_name = {}
    quiz_by_name = {}

    for item in toc_data:
        if item["lesson_page"] != "" and item["visible"] == "1":
            student_lesson_by_name[item["lesson_page"]] = item["url"]
        if item["lesson_page"] != "" and item["visible"] == "0":
            teacher_lesson_by_name[item["lesson_page"]] = item["url"]
        if item["lesson_page"] == "" and ("quiz" in item["activity_name"].lower() or "STAAR" in item["activity_name"]):
            quiz_by_name[item["activity_name"].replace(":", "").replace(",", "")] = item["url"]

    return {
        "teacher_lesson_by_name": teacher_lesson_by_name,
        "student_lesson_by_name": student_lesson_by_name,
        "quiz_by_name": quiz_by_name
    }


def main():
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('toc_csv_path', type=str,
                        help='relative path to IMRA ToC CSV')
    parser.add_argument('imra_csv_path', type=str,
                        help='Path to IMRA data CSV')
    parser.add_argument('output_path', type=str,
                        help='Path to output CSV')

    args = parser.parse_args()
    toc_csv_path = Path(args.toc_csv_path).resolve(strict=True)
    imra_csv_path = Path(args.imra_csv_path).resolve(strict=True)
    output_path = args.output_path

    imra_csv_data = []
    toc_data = []

    with imra_csv_path.open() as csv_file:
        items = csv.DictReader(csv_file)

        for item in items:
            imra_csv_data.append(item)

    with toc_csv_path.open() as csv_file:
        items = csv.DictReader(csv_file)

        for item in items:
            toc_data.append(item)

    url_indexes = create_url_indexes(toc_data)

    for row in imra_csv_data:
        location = row[LOCATION_COLUMN_NAME]

        is_lesson = False
        is_teacher_content = False
        is_quiz = False
        maybe_lesson_page_name = ""
        maybe_quiz_name = ""

        if "teacher" in location.lower():
            is_teacher_content = True

        if "quiz" in location.lower():
            is_quiz = True
            for location_item in location.split("\n"):
                location_item = location_item.strip()
                if "Quiz" in location_item:
                    maybe_quiz_name = location_item

        for location_item in location.split("\n"):
            location_item = location_item.strip()
            # Try to match #.#.# to determine if it is referencing a lesson

            if re.search(r'\d+.\d+.\d+', location_item):
                is_lesson = True
                maybe_lesson_page_name = location_item

        # Try to populate links
        if is_lesson and not is_teacher_content:
            # Attempt to lookup by maybe_lesson_page_name
            maybe_url = url_indexes["student_lesson_by_name"].get(maybe_lesson_page_name)
            if maybe_url:
                row[URL_COLUMN_NAME] = maybe_url

        if is_lesson and is_teacher_content:
            # Attempt to lookup by maybe_lesson_page_name
            maybe_url = url_indexes["teacher_lesson_by_name"].get(maybe_lesson_page_name)
            if maybe_url:
                row[URL_COLUMN_NAME] = maybe_url

        if is_quiz:
            # Get rid of ',' and ':'
            patched_quiz_name = maybe_quiz_name.replace(":", "").replace(",", "")
            patched_quiz_name = ''.join([patched_quiz_name.split("Quiz")[0], "Quiz"])
            maybe_url = url_indexes["quiz_by_name"].get(patched_quiz_name)
            if maybe_url:
                row[URL_COLUMN_NAME] = maybe_url

    # Write output CSV
    with open(output_path, "w") as outfile:
        content_headers = imra_csv_data[0].keys()
        result = csv.DictWriter(
            outfile,
            fieldnames=content_headers
        )
        result.writeheader()
        result.writerows(imra_csv_data)

if __name__ == "__main__":  # pragma: no cover
    main()
