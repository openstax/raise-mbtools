import argparse
import json
import shutil
from pathlib import Path


def create_json_content(uuid, content, json_path):
    if not Path(json_path).exists():

        json_content = {
            "id": uuid,
            "content": content}

        with open(json_path, "w") as new_file:
            new_file.write(json.dumps(json_content, indent=2))
    else:

        with open(json_path) as json_file:
            file_content = json_file.read()
            if file_content:

                content_from_json = json.loads(file_content)["content"]

        combined_content = content_from_json + content

        json_content = {"id": uuid, "content": combined_content}
        with open(json_path, "w") as new_file:
            new_file.write(json.dumps(json_content, indent=2))


def html_to_json(html_directory, json_directory):
    shutil.rmtree(json_directory)
    Path(json_directory).mkdir()

    for file in Path(html_directory).iterdir():
        if Path(f"{html_directory}/{file.name}").is_file():

            file_uuid = f"{Path(file.name).stem}"
            file_content = ""

            with open(f"{html_directory}/{file.name}") as f:
                file_content = f.read()

            create_json_content(
                file_uuid,
                [{"variant": "main", "html": file_content}],
                f"{json_directory}/" f"{Path(file.name).stem}.json",
            )

        elif Path(f'{html_directory}/{file.name}.html').exists():
            variant_list = []
            for f_name in Path(f"{html_directory}/{file.name}").iterdir():
                with open(f"{html_directory}/"
                          f"{file.name}/{f_name.name}") as varient_file:

                    variant_list.append(
                        {
                            "variant": f"{Path(f_name.name).stem}",
                            "html": varient_file.read()
                        }
                    )
            if variant_list:

                create_json_content(
                    Path(file.name).stem,
                    variant_list,
                    f"{json_directory}/" f"{Path(file.name).stem}.json",
                )


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "html_directory", type=str,
        help="relative path to HTML files")
    parser.add_argument(
        "output_directory", type=str,
        help="Path to where JSON files will be output"
    )

    args = parser.parse_args()
    html_directory = Path(args.html_directory).resolve(strict=True)
    output_directory = Path(args.output_directory).resolve(strict=True)
    html_to_json(html_directory, output_directory)


if __name__ == "__main__":  # pragma: no cover
    main()
