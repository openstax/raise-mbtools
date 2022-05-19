import argparse
import glob
import json
from pathlib import Path


def create_json_content(uuid, content, variant="main"):
    json_content = {"id": uuid, "content":
                    [{"variant": variant, "html": content}]}
    return json.dumps(json_content, indent=2)


def html_to_json(html_directory, json_directory):
    for file_name in glob.iglob(f'{html_directory}/*.html'):
        with open(f'{file_name}') as f:
            new_file = open(f'{json_directory}/'
                            f'{Path(file_name).stem}.json', "w")
            new_file.write(create_json_content(Path(file_name).stem, f.read()))
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
