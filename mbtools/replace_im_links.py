import json

import requests
from mbtools.utils import parse_backup_elements
import argparse
from pathlib import Path

IM_PREFIX = "https://s3.amazonaws.com/im-ims-export/"
# Make Conditional for local instance
CONTENT_PREFIX = "https://k12.openstax.org/contents/raise/"


def replace_references(elem, mapping):
    extracted_swap = False
    if ('os-raise-content' in elem.get_attribute_values("class")):
        swap_extracted_content(elem)
        extracted_swap = True

    replacements = elem.replace_attribute_values(['src', 'href'], mapping)

    if extracted_swap:
        elem.replace_content_with_tag()
    return replacements


def swap_extracted_content(elem):
    id = elem.get_attribute_values("data-content-id")[0]
    request = CONTENT_PREFIX + f"{id}.json"
    data = requests.get(request).json()
    elem.replace_tag_with_content(data['content'][0]['html'])


def parse_media_file(media_path, s3_prefix):
    mapping = {}
    with open(media_path) as f:
        data = json.load(f)
        for entry in data:
            im_url = IM_PREFIX + entry['original_filename']
            s3_url = s3_prefix + '/' + entry['s3_key']
            mapping[im_url] = s3_url
    return mapping


def replace_im_links(mbz_path, media_path, s3_prefix):
    im_to_osx_mapping = parse_media_file(media_path, s3_prefix)
    elems = parse_backup_elements(mbz_path)
    replacements = {}
    for elem in elems:
        changes = replace_references(elem, im_to_osx_mapping)
        if len(changes) > 0:
            replacements.update(changes)
    return replacements


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('mbz_path', type=str,
                        help='relative path to unzipped mbz')
    parser.add_argument('media_json', type=str,
                        help='Path to where files will be output')
    parser.add_argument('s3_prefix', type=str,
                        help='prefix for s3 files')
    args = parser.parse_args()
    mbz_path = Path(args.mbz_path).resolve(strict=True)
    media_path = Path(args.media_json).resolve(strict=True)
    replace_im_links(mbz_path, media_path, args.s3_prefix)


if __name__ == "__main__":
    main()
