import argparse
import glob
import json
from pathlib import Path


def create_json_content(uuid, content, variant="main"):
    json_content = {"id": uuid, "content":
                    [{"variant": variant, "html": content}]}
    return json.dumps(json_content, indent=4)


def html_to_json(html_directory, json_directory):
    file_list = []
    for file_name in glob.iglob(f'{html_directory}/*.html'):
        with open(f'{file_name}') as f:
            file_list.append({"name": Path(file_name).stem,
                              "content": f.read()})

    for file in file_list:
        new_file = open(f'{json_directory}/{file["name"]}.json', "w")
        new_file.write(create_json_content(file["name"], file["content"]))
        new_file.close()


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('html_directory', type=str,
                        help='relative path to HTML files')
    parser.add_argument('output_directory', type=str,
                        help='Path to where JSON files will be output')

    args = parser.parse_args()
    html_directory = Path(args.html_directory).resolve(strict=True)
    output_directory = Path(args.output_directory).resolve(strict=True)
    html_to_json(html_directory, output_directory)


if __name__ == "__main__":  # pragma: no cover
    main()
