import argparse
from lxml import html
from pathlib import Path
import requests
from mbtools.utils import parse_backup_elements, find_references_containing

IM_PREFIX = "https://s3.amazonaws.com/im-ims-export/"


def collect_and_write_resources(resource_urls, output_dir):
    for url in resource_urls:
        img_data = requests.get(url).content
        filename = url.rsplit('/', 1)[-1]
        with open(f'{output_dir}/{filename}', 'wb') as f:
            f.write(img_data)


def fetch_im_resources(content_dir, output_dir, mode):
    resource_urls = []
    if (mode == 'mbz'):
        elems = []
        elems.extend(parse_backup_elements(content_dir))
        for elem in elems:
            resource_urls.extend(
                find_references_containing(elem.etree_fragments[0], IM_PREFIX)
            )
    elif (mode == 'html'):
        for item in content_dir.iterdir():
            with open(item, 'r') as f:
                data = f.read()
                tree = html.fragments_fromstring(data)[0]
                resource_urls.extend(
                    find_references_containing(tree, IM_PREFIX)
                )
    collect_and_write_resources(set(resource_urls), output_dir)
    return resource_urls


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('content_path', type=str,
                        help='relative path to unzipped mbz or html directory')
    parser.add_argument('output_directory', type=str,
                        help='Path to where files will be output')
    parser.add_argument('mode', choices=['mbz', 'html'])

    args = parser.parse_args()

    content_path = Path(args.content_path).resolve(strict=True)
    output_dir = Path(args.output_directory)
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    resource_urls = fetch_im_resources(content_path, output_dir, args.mode)

    print(f'Processed {len(resource_urls)} URLs resulting in'
          f'{len(set(resource_urls))} files to {output_dir}')


if __name__ == "__main__":  # pragma: no cover
    main()
