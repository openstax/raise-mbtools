import glob
import json
from pathlib import Path
test_path = '/Users/prabhdipgill/Documents/openstax/raise-mbtools/htmlTest'


def create_json_content(uuid, content, variant = "main"):

     json_content = {"id": uuid, "content": [{"variant": variant, "html": content}]}
     return json.dumps(json_content, indent= 4)



def html_to_json(html_directory, json_directory, recursive_option = True ):
    file_list = []
    for file_name in glob.iglob(f'{html_directory}/**/*.html', recursive=recursive_option):
        print(Path(file_name).stem)
        with open(f'{file_name}') as f:
            file_list.append({"name": Path(file_name).stem, "content": f.read()})

    for file in file_list:
        new_file = open(f'{json_directory}/{file["name"]}.json', "w")
        new_file.write(create_json_content(file["name"], file["content"]))
        new_file.close()


html_to_json(test_path, f'{test_path}/output', True)

