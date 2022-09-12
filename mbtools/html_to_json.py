import argparse
import os
import json
import shutil
from pathlib import Path


def create_json_content(uuid, content, json_path):
    print('JSON Path: ', json_path)
    if(not os.path.exists(json_path)):
        print('JSON Path NOT EXISTS')

        json_content = {
            "id": uuid,
            "content": content}
        # print(json.dumps(json_content))
        with open(json_path, "w") as new_file:
            new_file.write(json.dumps(json_content, indent=2))
    else:
        print('JSON Path EXISTS')

        content_json = ""
        with open(json_path) as json_file:
            # content_json = json.load(json_file.read())
            file_content = json_file.read()
            if file_content:

                content_json = json.loads(file_content)['content']

        combined_content = content_json + content
        print(combined_content)
        json_content = {
            "id": uuid,
            "content": combined_content}
        with open(json_path, "w") as new_file:
            new_file.write(json.dumps(json_content, indent=2))


    # return json.dumps(json_content, indent=2)

def html_to_json(html_directory, json_directory):
    shutil.rmtree(json_directory) 
    os.mkdir(json_directory)

    for file_name in os.listdir(html_directory):
        if os.path.isfile(f'{html_directory}/{file_name}'):

            file_uuid = f'{Path(file_name).stem}'
            file_content = ''

            with open(f'{html_directory}/{file_name}') as f:
                file_content = f.read()

            create_json_content(
                    file_uuid, [{"variant": "main", "html": file_content}], f'{json_directory}/'
                          f'{Path(file_name).stem}.json')

        elif(f'{file_name}.html' in os.listdir(html_directory)):
            variant_list = []
            for f_name in os.listdir(f'{html_directory}/{file_name}'):
                with open(f'{html_directory}/'
                          f'{file_name}/{f_name}') as varient_file:

                    variant_list.append(
                        {"variant": f'{Path(f_name).stem}',
                         "html": varient_file.read()})
            if variant_list:

                    create_json_content(
                        Path(file_name).stem, variant_list, f'{json_directory}/'
                          f'{Path(file_name).stem}.json')


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
    # main()
    html_to_json('./html', './json')
