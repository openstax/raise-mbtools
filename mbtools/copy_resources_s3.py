import hashlib
import json
import os
import io
import magic
import boto3
import argparse
import botocore
from pathlib import Path


def upload_resources(resource_dir, metadata_file, bucket, s3_dir):
    """Uploads resources to s3 if they dont already exist there"""

    hash_to_filename_map = new_resource_hashes(resource_dir)
    hashes_new = list(hash_to_filename_map.keys())

    hashes_metadata = existing_metadata_hashes(metadata_file)
    hashes_to_update = list(
        filter(lambda h: h not in hashes_metadata, hashes_new)
    )
    add_new_resources_to_s3(
        bucket, s3_dir, hashes_to_update, hash_to_filename_map, metadata_file
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
    new_metadata = []
    for hash_key in hashes:
        full_keypath = s3_dir + '/' + hash_key

        try:
            s3_client.head_object(Bucket=bucket,
                                  Key=full_keypath)
            filename = os.path.basename(hash2filename_map[hash_key])
            print(f"File {filename} with sha {hash_key} already exists in S3!")

        except botocore.exceptions.ClientError:
            mime_type = get_mime_type(hash2filename_map[hash_key])
            s3_client.upload_file(hash2filename_map[hash_key],
                                  Bucket=bucket,
                                  Key=full_keypath,
                                  ExtraArgs={
                                    "ContentType": mime_type
                                    }
                                  )
            new_metadata.append({
                "mime_type": mime_type,
                "sha1": hash_key,
                "original_filename": os.path.basename(
                    hash2filename_map[hash_key]
                ),
                "s3_key": full_keypath
            })

    add_metadata(new_metadata, metadata_file)
    print("Uploaded " + str(len(new_metadata)) + " files to " +
          bucket)


def add_metadata(new_metadata, metadata_file):
    """Append metadata tags to a metadata_file"""

    with open(metadata_file) as f:
        data = json.load(f)
        for tag in new_metadata:
            data.append(tag)
    with open(metadata_file, 'w') as f:
        json.dump(data, f)


def main():
    parser = argparse.ArgumentParser(description='Upload Resources to S3')
    parser.add_argument('new_resource_path', type=str,
                        help='relative path to files')
    parser.add_argument('metadata_file', type=str,
                        help='relative path to metadata file')
    parser.add_argument('bucket_name', type=str,
                        help='bucket name')
    parser.add_argument('s3_prefix', type=str,
                        help='prefix for s3 files')
    args = parser.parse_args()

    new_resource_dir = Path(args.new_resource_path).resolve(strict=True)

    metadata_file = Path(args.metadata_file)

    if not metadata_file.exists():
        metadata_file.parent.mkdir(parents=True, exist_ok=True)
        metadata_file.write_text("[]")

    upload_resources(new_resource_dir, args.metadata_file, args.bucket_name,
                     args.s3_prefix)


if __name__ == "__main__":
    main()
