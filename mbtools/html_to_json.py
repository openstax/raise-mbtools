import argparse
import os
import json
from pathlib import Path


def create_json_content(uuid, content):

    json_content = {"id": uuid, "content":
                                content}
    return json.dumps(json_content, indent=2)


def html_to_json(html_directory, json_directory):

    for file_name in os.listdir(html_directory):
        if os.path.isfile(f'{html_directory}/{file_name}'):

            file_uuid = f'{Path(file_name).stem}'
            file_content = ''

            with open(f'{html_directory}/{file_name}') as f:
                file_content = f.read()

            with open(f'{json_directory}/'
                      f'{Path(file_name).stem}.json', "w") as new_file:
                new_file.write(create_json_content(
                    file_uuid, [{"variant": "main", "html": file_content}]))

        else:
            variant_list = []
            for f_name in os.listdir(f'{html_directory}/{file_name}'):
                with open(f'{html_directory}/'
                          f'{file_name}/{f_name}') as varient_file:

                    variant_list.append(
                        {"variant": f'{Path(f_name).stem}',
                         "html": varient_file.read()})
            if variant_list:

                with open(f'{json_directory}/'
                          f'{Path(file_name).stem}.json', "w") as new_file:

                    new_file.write(create_json_content(
                        Path(file_name).stem, variant_list))


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
