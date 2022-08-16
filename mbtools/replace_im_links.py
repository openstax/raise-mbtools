import hashlib
import json
import requests
from mbtools import utils
import argparse
from lxml import html
from pathlib import Path
from mbtools import models
from mbtools.fetch_im_resources import IM_PREFIX


def replace_src_values_tree(content_tree, src_content, swap_mapping):
    num_changes = 0
    for elem in utils.find_elements_containing(content_tree, src_content):
        im_filename = elem.attrib["src"]
        if im_filename in swap_mapping.keys():
            num_changes += 1
            elem.attrib["src"] = swap_mapping[im_filename]
        else:
            # Fetch link, calculate sha1, and replace link anyway.
            data = requests.get(im_filename).content
            sha1 = hashlib.sha1(data).hexdigest()
            for key in swap_mapping.keys():
                if sha1 in swap_mapping[key]:
                    elem.attrib["src"] = swap_mapping[key]
                    num_changes += 1
    return num_changes


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
    if (mode == 'mbz'):
        backup = utils.parse_moodle_backup(content_path)
        activities = backup.activities()
        q_bank = backup.q_bank
        act_updates = 0
        for act in activities:
            elems = act.html_elements()
            for elem in elems:
                num_changes = replace_src_values_tree(
                    elem.etree_fragments[0], IM_PREFIX, im_to_osx_mapping
                    )
                if (num_changes > 0):
                    elem.update_html()
                    act_updates += 1
            if act_updates > 0:
                utils.write_etree(act.activity_filename, act.etree)
        utils.write_etree(q_bank.questionbank_path, q_bank.etree)
    elif (mode == 'html'):
        for item in content_path.iterdir():
            num_changes = 0
            with open(item, 'r') as f:
                data = f.read()
                fragments = html.fragments_fromstring(data)
                num_changes = replace_src_values_tree(
                    fragments[0], IM_PREFIX, im_to_osx_mapping
                    )
            if num_changes > 0:
                with open(item, 'w') as f:
                    f.write(models.html_fragments_to_string(fragments))


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('content_path', type=str,
                        help='relative path to unzipped mbz or html directory')
    parser.add_argument('media_json', type=str,
                        help='Path to where files will be output')
    parser.add_argument('content_url_prefix', type=str,
                        help='prefix for content_URLS files')
    parser.add_argument('mode', choices=['mbz', 'html'])

    args = parser.parse_args()
    content_path = Path(args.content_path).resolve(strict=True)
    media_path = Path(args.media_json).resolve(strict=True)

    replace_im_links(content_path, media_path,
                     args.content_url_prefix, args.mode)


if __name__ == "__main__":  # pragma: no cover
    main()
