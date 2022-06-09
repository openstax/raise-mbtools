import json
from mbtools import utils
import argparse
from lxml import html
from pathlib import Path

IM_PREFIX = "https://s3.amazonaws.com/im-ims-export/"
# Make Conditional for local instance
CONTENT_PREFIX = "https://k12.openstax.org/contents/raise/"


def parse_media_file(media_path, s3_prefix):
    mapping = {}
    with open(media_path) as f:
        data = json.load(f)
        for entry in data:
            im_url = IM_PREFIX + entry['original_filename']
            s3_url = s3_prefix + '/' + entry['s3_key']
            mapping[im_url] = s3_url
    return mapping


def replace_im_links(content_path, media_path, s3_prefix, mode):
    im_to_osx_mapping = parse_media_file(media_path, s3_prefix)
    replacements = {}
    if (mode == 'mbz'):
        backup = utils.parse_moodle_backup(content_path)
        activities = backup.activities()
        q_bank = backup.q_bank
        for act in activities:
            elems = act.html_elements()
            for elem in elems:
                changes = elem.replace_attribute_values(
                              ['src', 'href'], im_to_osx_mapping)
                if (len(changes) > 0):
                    replacements.update(changes)
                    utils.write_etree(act.activity_filename, act.etree)
                    utils.write_etree(q_bank.questionbank_path, q_bank.etree)
        return replacements
    elif (mode == 'html'):
        for item in content_path.iterdir():
            content_tree = None
            with open(item, 'r') as f:
                data = f.read()
                content_tree = html.fragments_fromstring(data)[0]
                utils.replace_attribute_values_tree(
                    content_tree, ['src', 'href'], im_to_osx_mapping
                    )
            with open(item, 'w') as f:
                f.write(html.tostring(content_tree).decode())


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('content_path', type=str,
                        help='relative path to unzipped mbz or html directory')
    parser.add_argument('media_json', type=str,
                        help='Path to where files will be output')
    parser.add_argument('s3_prefix', type=str,
                        help='prefix for s3 files')
    parser.add_argument('mode', choices=['mbz', 'html'])

    args = parser.parse_args()
    content_path = Path(args.content_path).resolve(strict=True)
    media_path = Path(args.media_json).resolve(strict=True)

    replace_im_links(content_path, media_path, args.s3_prefix, args.mode)


if __name__ == "__main__":
    main()
