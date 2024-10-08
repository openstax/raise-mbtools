import hashlib
import os
import io
import magic
import boto3
import argparse
import botocore
import jinja2
from pathlib import Path
from datetime import datetime, timezone

IGNORED_FILES = [".DS_Store"]


def upload_resources(resource_dir, bucket, s3_dir):
    """Uploads resources to s3 if they dont already exist there"""

    hash_to_filedata_map, duplicates = resource_hashes(resource_dir)
    hashes_to_update = list(hash_to_filedata_map.keys())

    existing_timestamps = add_new_resources_to_s3(
        bucket, s3_dir, hashes_to_update, hash_to_filedata_map
    )

    for hash_key in hash_to_filedata_map:
        if hash_key in existing_timestamps:
            timestamp_str = existing_timestamps[hash_key].isoformat()
            hash_to_filedata_map[hash_key]['timestamp'] = timestamp_str

    for item in duplicates:
        sha1_hash = item['sha1']
        if sha1_hash in existing_timestamps:
            existing_timestamp = existing_timestamps[sha1_hash]
            timestamp_str = existing_timestamp.isoformat()
            item['timestamp'] = timestamp_str

    return hash_to_filedata_map, duplicates


def output_index_file(resource_path, hash_to_filedata_map, duplicates,
                      url_prefix, index_file):
    environment = jinja2.Environment()
    template_path = Path(__file__).parent / 'index_template.html'
    data = []

    for key, value in hash_to_filedata_map.items():
        item = {
            'filepath': os.path.relpath(value['path'], resource_path),
            'mimetype': value['mime_type'],
            'url': f'{url_prefix}/{key}',
            'timestamp': value['timestamp']
        }
        data.append(item)

    for duplicate in duplicates:
        item = {
            'filepath': os.path.relpath(duplicate['path'], resource_path),
            'mimetype': duplicate['mime_type'],
            'url': f'{url_prefix}/{duplicate["sha1"]}',
            'timestamp': duplicate['timestamp']
        }
        data.append(item)

    data.sort(key=lambda x: datetime.fromisoformat(x['timestamp']),
              reverse=True)

    for item in data:
        timestamp = datetime.fromisoformat(item['timestamp'])
        item['timestamp'] = timestamp.strftime('%B %d, %Y %I:%M %p')

    with open(template_path) as template_file:
        template = environment.from_string(template_file.read())
        with open(f'{index_file}', mode='w') as workflow_file:
            workflow_file.write(template.render(data=data))


def resource_hashes(resource_dir):
    """Generates sha1 hashes for all the resources in a local directory"""

    sha1_map = {}
    duplicates = []
    buff_size = io.DEFAULT_BUFFER_SIZE
    path_to_files = []
    for (dir_path, dir_names, file_names) in os.walk(resource_dir):
        for file in file_names:
            path_to_files.append(os.path.join(dir_path, file))

    resource_files = filter(
        lambda x: Path(x).stem not in IGNORED_FILES,
        path_to_files
    )

    for full_path in resource_files:
        mime_type = get_mime_type(full_path)
        sha1 = hashlib.sha1()
        with open(full_path, 'rb') as f:
            while True:
                data = f.read(buff_size)
                if not data:
                    break
                sha1.update(data)
            sha1_key = sha1.hexdigest()
            if sha1_key in sha1_map:
                duplicates.append({
                    'path': full_path,
                    'mime_type': mime_type,
                    'sha1': sha1_key,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            else:
                sha1_map[sha1_key] = {
                    'path': full_path,
                    'mime_type': mime_type,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }

    return sha1_map, duplicates


def get_mime_type(filepath):
    """Get the MIME type of file with libmagic """
    mime_type = ''
    try:
        mime_type = magic.from_file(filepath, mime=True)
    finally:
        return mime_type


def add_new_resources_to_s3(bucket, s3_dir, hashes_to_update,
                            hash_to_filedata_map):
    """Add the files specified in hashes_to_update to s3 if they their
    corresponding sha1 key exists in hashes"""

    s3_client = boto3.client("s3")
    existing_timestamps = {}
    metadata = []
    for hash_key in hashes_to_update:
        full_keypath = s3_dir + '/' + hash_key

        try:
            s3_response = s3_client.head_object(Bucket=bucket,
                                                Key=full_keypath)
            filename = os.path.basename(hash_to_filedata_map[hash_key]['path'])
            existing_timestamps[hash_key] = s3_response['LastModified']
            print(f"File {filename} with sha {hash_key} already exists in S3!")
        except botocore.exceptions.ClientError:
            mime_type = hash_to_filedata_map[hash_key]['mime_type']
            s3_client.upload_file(hash_to_filedata_map[hash_key]['path'],
                                  Bucket=bucket,
                                  Key=full_keypath,
                                  ExtraArgs={
                                    "ContentType": mime_type
                                    }
                                  )

        # This timestamp in metadata will be slightly off because the time
        # at which s3 will upload will be different than the time here
            metadata.append({
                "mime_type": mime_type,
                "sha1": hash_key,
                "original_filename": os.path.basename(
                    hash_to_filedata_map[hash_key]['path']
                ),
                "s3_key": full_keypath,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

    print("Uploaded " + str(len(metadata)) + " files to " +
          bucket)
    return existing_timestamps


def main():
    parser = argparse.ArgumentParser(description='Upload Resources to S3')
    parser.add_argument('resource_path', type=str,
                        help='file path to repository')
    parser.add_argument('bucket_name', type=str,
                        help='bucket name')
    parser.add_argument('s3_prefix', type=str,
                        help='prefix for s3 files')
    parser.add_argument('url_prefix', type=str,
                        help='url prefix for s3 files')
    parser.add_argument('index_path', type=str,
                        help='file path to index file')

    args = parser.parse_args()

    resource_dir = Path(args.resource_path).resolve(strict=True)

    hash_to_filedata_map, duplicates = upload_resources(resource_dir,
                                                        args.bucket_name,
                                                        args.s3_prefix)

    output_index_file(resource_dir, hash_to_filedata_map, duplicates,
                      args.url_prefix, args.index_path)


if __name__ == "__main__":
    main()
