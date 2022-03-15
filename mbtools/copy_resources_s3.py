import hashlib
import json
import os
import io
import sys
import magic
import boto3
import botocore
from pathlib import Path


def upload_resources(resource_dir, metadata_file, bucket, s3_dir):
    """Uplaods resources to s3 if they dont already exist there"""

    hash_to_filename_map = new_resource_hashes(resource_dir)
    hashes_new = list(hash_to_filename_map.keys())

    hashes_metadata = existing_metadata_hashes(metadata_file)
    hashes_to_update = list(filter(lambda h: h not in hashes_metadata,
                                   hashes_new)
                            )
    add_new_resources_to_s3(bucket, s3_dir, hashes_to_update,
                            hash_to_filename_map, metadata_file
                            )


def existing_metadata_hashes(dir):
    """Gathers the sha1s for existing resources from a local metadata json"""
    hashes = []
    with open(dir) as f:
        data = json.load(f)
        for item in data:
            hashes.append(item["sha1"])
    return hashes


def new_resource_hashes(resource_dir):
    """Generates sha1 hashes for all the resources in a local directory"""
    sha1_map = {}
    buff_size = io.DEFAULT_BUFFER_SIZE
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


def get_mime_type(filename):
    """Get the MIME type of file with libmagic """
    mime_type = ''
    try:
        mime_type = magic.from_file(filename, mime=True)
    finally:
        return mime_type


def add_new_resources_to_s3(bucket, s3_dir, hashes, hash2filename_map,
                            metadata_file
                            ):
    """Add the files specified in filename_map to s3 iff they their
    corresponding sha1 key exists in hashes"""

    s3_client = boto3.client("s3")
    hashkey2mimes_map = {}
    hashkey2filenames_map = {}
    hashkey2keypath_map = {}
    for hash_key in hashes:
        full_keypath = s3_dir + '/' + hash_key

        try:
            s3_client.head_object(Bucket=bucket,
                                  Key=full_keypath)
        except botocore.exceptions.ClientError:
            mime_type = get_mime_type(hash2filename_map[hash_key])
            s3_client.upload_file(hash2filename_map[hash_key],
                                  Bucket=bucket,
                                  Key=full_keypath,
                                  ExtraArgs={
                                    "ContentType": mime_type
                                    }
                                  )
            hashkey2mimes_map[hash_key] = mime_type
            hashkey2keypath_map[hash_key] = full_keypath
            hashkey2filenames_map[hash_key] = os.path.basename(
                                              hash2filename_map[hash_key]
                                              )

    add_metadata(hashkey2mimes_map,
                 hashkey2filenames_map,
                 hashkey2keypath_map,
                 metadata_file)
    print("SUCCESS")
    print("Uploaded " + str(len(hashkey2mimes_map.keys())) + " files to " +
          bucket)


def add_metadata(new_tag_mimes, new_tag_filenames, new_tag_keypath,
                 metadata_file
                 ):
    """Append metadata tags to a metadata_file"""

    with open(metadata_file) as f:
        data = json.load(f)
        for key in new_tag_mimes:
            tag = {"mime_type": new_tag_mimes[key],
                   "sha1": key,
                   "original_filename": new_tag_filenames[key],
                   "s3_key": new_tag_keypath[key]
                   }
            data.append(tag)
    with open(metadata_file, 'w') as f:
        json.dump(data, f)


def main():
    new_resource_dir = Path(sys.argv[1]).resolve(strict=True)
    metadata_file = Path(sys.argv[2]).resolve(strict=True)
    bucket = sys.argv[3]
    s3_dir = sys.argv[4]

    upload_resources(new_resource_dir, metadata_file, bucket, s3_dir)


if __name__ == "__main__":
    main()
