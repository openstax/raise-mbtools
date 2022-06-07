import argparse
from pathlib import Path
import requests
from mbtools.utils import parse_backup_elements

IM_PREFIX = "https://s3.amazonaws.com/im-ims-export/"

# Make Conditional for local instance
CONTENT_PREFIX = "https://k12.openstax.org/contents/raise/"


def collect_and_write_resources(resource_urls, output_dir):
    for url in resource_urls:
        img_data = requests.get(url, stream=True).content
        filename = url.rsplit('/', 1)[-1]
        with open(f'{output_dir}/{filename}', 'wb') as f:
            f.write(img_data)


def swap_extracted_content(elem):
    id = elem.get_attribute_values("data-content-id")[0]
    request = CONTENT_PREFIX + f"{id}.json"
    data = requests.get(request).json()
    elem.replace_tag_with_content(data['content'][0]['html'])


def get_im_resources_from_html(elem):
    extracted_swap = False
    if ('os-raise-content' in elem.get_attribute_values("class")):
        swap_extracted_content(elem)
        extracted_swap = True

    values = elem.get_attribute_values('src')
    values.extend(elem.get_attribute_values('href'))
    im_resources = []
    for val in values:
        if IM_PREFIX in val:
            im_resources.append(val)

    if extracted_swap:
        elem.replace_content_with_tag()
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

    replacements = fetch_im_resources(mbz_path, output_dir)

    print(f'Donloaded {len(replacements)} files to {output_dir}')


if __name__ == "__main__":
    main()
