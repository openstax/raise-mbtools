import hashlib
import json
import os
import sys
import magic
import boto3
import botocore
from pathlib import Path


def upload_resources(resource_dir, metadata_dir, bucket, s3_dir):
    """Uplaods resources to s3 if they dont already exist there"""
    hash_to_filename_map = new_resource_hashes(resource_dir)
    hashes_new = list(hash_to_filename_map.keys())
    hashes_metadata = existing_metadata_hashes(metadata_dir)
    hashes_s3 = existing_s3_hashes(bucket, s3_dir)
    hashes_new = compare_and_remove_hashes(hashes_new, hashes_metadata)
    hashes_new = compare_and_remove_hashes(hashes_new, hashes_s3)
    add_new_resources_to_s3(bucket, s3_dir, hashes_new, hash_to_filename_map,
                            metadata_dir
                            )


def existing_metadata_hashes(dir):
    """Gathers the sha1s for existing resources from a local metadata json"""
    hashes = []
    try:
        with open(dir) as f:
            data = json.load(f)
            for item in data:
                hashes.append(item["sha1"])
        return hashes
    except FileNotFoundError:
        return FileNotFoundError


def existing_s3_hashes(bucket, s3_dir):
    """Gathers the sha1s (filenames) for a given s3 bucket/directory"""
    s3_client = boto3.client("s3")
    try:
        all_s3_resources = s3_client.list_objects(
            Bucket=bucket,
            Prefix=s3_dir
        )
        sha1_list = []
        print(all_s3_resources)
        for file_info in all_s3_resources['Contents']:
            # extract the sha1 from the key
            sha1 = file_info['Key'].split('/')[-1].split('.')[0]
            sha1_list.append(sha1)
    except botocore.exceptions.ClientError:
        sha1_list = None
    return sha1_list


def new_resource_hashes(resource_dir):
    """Generates sha1 hashes for all the resources in a local directory"""
    sha1_map = {}
    buff_size = 8 * 1024 * 1024
    try:
        for filename in os.listdir(resource_dir):

            sha1 = hashlib.sha1()
            full_path = os.path.join(resource_dir, filename)
            with open(full_path, 'rb') as f:
                while True:
                    data = f.read(buff_size)
                    if not data:
                        break
                    sha1.update(data)
            sha1_map[sha1.hexdigest()] = full_path
        return sha1_map
    except FileNotFoundError:
        return FileNotFoundError


def compare_and_remove_hashes(keys, existing_keys):
    """Returns a list of the items from keys that arent in existing_keys"""
    new_keys = []
    for i in keys:
        if i not in existing_keys:
            new_keys.append(i)
    return new_keys


def get_mime_type(filename):
    """ get MIME type of file with libmagic """
    mime_type = ''
    try:
        mime_type = magic.from_file(filename, mime=True)
    finally:
        return mime_type


def add_new_resources_to_s3(bucket, s3_dir, hashes, filename_map,
                            metadata_dir
                            ):
    """Add the files specified in filename_map to s3 iff they their
    corresponding sha1 key exists in hashes"""
    s3_client = boto3.client("s3")
    print(hashes)
    for key in hashes:
        full_keypath = s3_dir + key
        s3_client.upload_file(filename_map[key], bucket,
                              full_keypath
                              )
        mime_type = get_mime_type(filename_map[key])
        print(mime_type)
        add_metadata(key, filename_map, metadata_dir, mime_type, full_keypath)


def add_metadata(key, filename_map, metadata_dir, mime_type, full_keypath):
    """"""
    tag = {"mime_type": mime_type,
           "sha1": key,
           "original_filename": os.path.basename(filename_map[key]),
           "s3_key": full_keypath
           }

    with open(metadata_dir) as f:
        data = json.load(f)
        data.append(tag)
    with open(metadata_dir, 'w') as f:
        json.dump(data, f)


def main():
    new_resource_dir = Path(sys.argv[1]).resolve(strict=True)
    metadata_dir = Path(sys.argv[2]).resolve(strict=True)

    bucket = "k12-content-primary"
    s3_dir = "contents/raise/resources/"
    upload_resources(new_resource_dir, metadata_dir, bucket, s3_dir)


if __name__ == "__main__":
    main()
