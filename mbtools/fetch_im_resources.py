import argparse
from pathlib import Path
import requests
from mbtools.utils import parse_backup_elements

IM_PREFIX = "https://s3.amazonaws.com/im-ims-export/"


def collect_and_write_resources(resource_urls, output_dir):
    for url in resource_urls:
        img_data = requests.get(url).content
        filename = url.rsplit('/', 1)[-1]
        with open(f'{output_dir}/{filename}', 'wb') as f:
            f.write(img_data)


def get_im_resources_from_html(elem):
    values = elem.get_attribute_values('src')
    values.extend(elem.get_attribute_values('href'))
    im_resources = []
    for val in values:
        if IM_PREFIX in val:
            im_resources.append(val)
    return im_resources


def fetch_im_resources(mbz_dir, output_dir):
    elems = []
    elems.extend(parse_backup_elements(mbz_dir))
    resource_urls = []
    for elem in elems:
        resource_urls.extend(get_im_resources_from_html(elem))
    collect_and_write_resources(resource_urls, output_dir)
    return resource_urls


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('mbz_path', type=str,
                        help='relative path to unzipped mbz')
    parser.add_argument('output_directory', type=str,
                        help='Path to where files will be output')
    args = parser.parse_args()

    mbz_path = Path(args.mbz_path).resolve(strict=True)
    output_dir = Path(args.output_directory)
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    fetch_im_resources(mbz_path, output_dir)


if __name__ == "__main__":
    main()
