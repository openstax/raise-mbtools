import pytest
import botocore.stub
import boto3
import os
import json
import csv
from mbtools import copy_resources_s3


test_dir = 'test_content/'
f1 = 'test_content/example1.txt'
f2 = 'test_content/example2.mp4'
f3 = 'test_content/example3.jpeg'
f4 = 'test_content/example4.jpeg'

f1_data = {'txt_data': 2}
f2_data = {'mp4_data': 'video'}
f3_data = {'jpeg_data': 'picture'}
f4_data = {'jpeg_data': 'picture'}

metadata_file = 'metadata/tags.json'
new_metadata_file = 'new_tags.json'
csv_file = "csv_output.csv"

metadata_tags = [
    {
        'mime_type': 'video/mp4',
        'original_filename': 'Example_2.mp4',
        's3_key': 'contents/raise/resources/f83a0cabe1fc9bfe35d709' +
                  '47e9c0ed8e5285b76e',
        'sha1': 'f83a0cabe1fc9bfe35d70947e9c0ed8e5285b76e'
    },
    {
        'mime_type': 'video/mp4',
        'sha1': 'd3614ca5260104f401a96415b448943725c2feb0',
        'original_filename': 'TwoLines.mp4',
        's3_key': 'contents/raise/resources/d3614ca5260104f401a964' +
                  '15b448943725c2feb0'
    }
]

metadata_updates = [
    {
        'mime_type': 'application/json',
        'sha1': 'dc330ae2bc1d0b2edac442ed3f8245647cf5c0c0',
        'original_filename': 'example1.txt',
        's3_key': 'resources/dc330ae2bc1d0b2edac442ed3f8245647cf5c0c0'
    },
    {
        'mime_type': 'application/json',
        'sha1': 'a31e7f061d762f1e5099ecebfe6877310e5be420',
        'original_filename': 'example2.mp4',
        's3_key': 'resources/a31e7f061d762f1e5099ecebfe6877310e5be420'
     },
    {
        'mime_type': 'application/json',
        'sha1': 'e606bc6acc83666e1d40722e9c743a01e12e65ab',
        'original_filename': 'example4.jpeg',
        's3_key': 'resources/e606bc6acc83666e1d40722e9c743a01e12e65ab'
     },
]


@pytest.fixture
def practice_filesystem(tmp_path):

    (tmp_path / test_dir).mkdir()
    with open(str(tmp_path / f1), 'w') as f:
        json.dump(f1_data, f)
    with open(str(tmp_path / f2), 'w') as f:
        json.dump(f2_data, f)
    with open(str(tmp_path / f3), 'w') as f:
        json.dump(f3_data, f)
    with open(str(tmp_path / f4), 'w') as f:
        json.dump(f4_data, f)
    with open(f"{tmp_path}/{test_dir}/.DS_Store", "w") as f:
        f.write(".DS_Store file")

    (tmp_path / 'metadata').mkdir()
    with open(str(tmp_path / metadata_file), 'w') as f:
        json.dump(metadata_tags, f)

    path_dict = {metadata_file: str(tmp_path / metadata_file),
                 csv_file: str(tmp_path / csv_file),
                 test_dir: str(tmp_path / test_dir),
                 f1: str(tmp_path / f1),
                 "home": str(tmp_path),
                 }
    return path_dict


def test_existing_metadata_hashes(practice_filesystem):
    assert (copy_resources_s3.existing_metadata_hashes(
            practice_filesystem[metadata_file]) ==
           [metadata_tags[0]['sha1'], metadata_tags[1]['sha1']])
    with pytest.raises(FileNotFoundError):
        copy_resources_s3.existing_metadata_hashes("")


def test_new_resource_hashes(practice_filesystem):
    assert(len(copy_resources_s3.new_resource_hashes(
               practice_filesystem[test_dir])[0]) == 3
           )
    with pytest.raises(FileNotFoundError):
        copy_resources_s3.new_resource_hashes("")


def test_get_mime_type(practice_filesystem):
    assert os.path.exists(practice_filesystem[f1])
    assert (copy_resources_s3.get_mime_type(practice_filesystem[f1]) ==
            'application/json')


def test_upload_resources(practice_filesystem, mocker):
    s3_dir = 'resources'
    bucket_name = 'test-bucket'
    sha1_map, _ = copy_resources_s3.new_resource_hashes(
               practice_filesystem[test_dir])
    hash_keys = list(sha1_map)
    s3_client = boto3.client('s3')
    stubber = botocore.stub.Stubber(s3_client)

    full_key1 = s3_dir + '/' + hash_keys[0]
    full_key2 = s3_dir + '/' + hash_keys[1]
    full_key3 = s3_dir + '/' + hash_keys[2]

    stubber.add_client_error('head_object',
                             service_error_meta={'Code': '404'},
                             expected_params={
                                 'Bucket': bucket_name,
                                 'Key': full_key1
                              }
                             )
    stubber.add_response('put_object', {},
                         expected_params={
                            'Body': botocore.stub.ANY,
                            'Bucket': bucket_name,
                            'Key': full_key1,
                            'ContentType': 'application/json'
                          }
                         )
    stubber.add_client_error('head_object',
                             service_error_meta={'Code': '404'},
                             expected_params={
                                'Bucket': bucket_name,
                                'Key': full_key2
                                }
                             )
    stubber.add_response('put_object', {},
                         expected_params={
                            'Body': botocore.stub.ANY,
                            'Bucket': bucket_name,
                            'Key': full_key2,
                            'ContentType': 'application/json'
                            }
                         )
    stubber.add_client_error('head_object',
                             service_error_meta={'Code': '404'},
                             expected_params={
                                'Bucket': bucket_name,
                                'Key': full_key3
                                }
                             )
    stubber.add_response('put_object', {},
                         expected_params={
                            'Body': botocore.stub.ANY,
                            'Bucket': bucket_name,
                            'Key': full_key3,
                            'ContentType': 'application/json'
                            }
                         )
    stubber.activate()
    mocker.patch('boto3.client', lambda service: s3_client)

    resource_dir = practice_filesystem[test_dir]
    print(resource_dir)
    metadata_path = practice_filesystem[metadata_file]
    mocker.patch(
        "sys.argv",
        ["", resource_dir, metadata_path, bucket_name, s3_dir]
    )
    copy_resources_s3.main()

    with open(metadata_path, 'r') as f:
        data = json.load(f)
    assert len(data) == 5
    for item in metadata_updates:
        assert item in data


def test_upload_resources_no_existing_metadata_file(practice_filesystem,
                                                    mocker):
    s3_dir = 'resources'
    bucket_name = 'test-bucket'
    sha1_map, _ = copy_resources_s3.new_resource_hashes(
               practice_filesystem[test_dir])
    hash_keys = list(sha1_map)
    s3_client = boto3.client('s3')
    stubber = botocore.stub.Stubber(s3_client)

    full_key1 = s3_dir + '/' + hash_keys[0]
    full_key2 = s3_dir + '/' + hash_keys[1]
    full_key3 = s3_dir + '/' + hash_keys[2]

    stubber.add_client_error('head_object',
                             service_error_meta={'Code': '404'},
                             expected_params={
                                 'Bucket': bucket_name,
                                 'Key': full_key1
                              }
                             )
    stubber.add_response('put_object', {},
                         expected_params={
                            'Body': botocore.stub.ANY,
                            'Bucket': bucket_name,
                            'Key': full_key1,
                            'ContentType': 'application/json'
                          }
                         )
    stubber.add_client_error('head_object',
                             service_error_meta={'Code': '404'},
                             expected_params={
                                'Bucket': bucket_name,
                                'Key': full_key2
                                }
                             )
    stubber.add_response('put_object', {},
                         expected_params={
                            'Body': botocore.stub.ANY,
                            'Bucket': bucket_name,
                            'Key': full_key2,
                            'ContentType': 'application/json'
                            }
                         )
    stubber.add_client_error('head_object',
                             service_error_meta={'Code': '404'},
                             expected_params={
                                'Bucket': bucket_name,
                                'Key': full_key3
                                }
                             )
    stubber.add_response('put_object', {},
                         expected_params={
                            'Body': botocore.stub.ANY,
                            'Bucket': bucket_name,
                            'Key': full_key3,
                            'ContentType': 'application/json'
                            }
                         )
    stubber.activate()
    mocker.patch('boto3.client', lambda service: s3_client)

    resource_dir = practice_filesystem[test_dir]
    metadata_path = practice_filesystem["home"] + new_metadata_file
    mocker.patch(
        "sys.argv",
        ["", resource_dir, metadata_path, bucket_name, s3_dir]
    )
    copy_resources_s3.main()

    with open(metadata_path, 'r') as f:
        data = json.load(f)
    assert len(data) == 3
    for item in metadata_updates:
        assert item in data


def test_upload_resources_with_csv(practice_filesystem, mocker):
    s3_dir = 'resources'
    bucket_name = 'test-bucket'
    sha1_map, _ = copy_resources_s3.new_resource_hashes(
               practice_filesystem[test_dir])
    hash_keys = list(sha1_map)
    s3_client = boto3.client('s3')
    stubber = botocore.stub.Stubber(s3_client)

    full_key1 = s3_dir + '/' + hash_keys[0]
    full_key2 = s3_dir + '/' + hash_keys[1]
    full_key3 = s3_dir + '/' + hash_keys[2]

    stubber.add_client_error('head_object',
                             service_error_meta={'Code': '404'},
                             expected_params={
                                 'Bucket': bucket_name,
                                 'Key': full_key1
                              }
                             )
    stubber.add_response('put_object', {},
                         expected_params={
                            'Body': botocore.stub.ANY,
                            'Bucket': bucket_name,
                            'Key': full_key1,
                            'ContentType': 'application/json'
                          }
                         )
    stubber.add_client_error('head_object',
                             service_error_meta={'Code': '404'},
                             expected_params={
                                'Bucket': bucket_name,
                                'Key': full_key2
                                }
                             )
    stubber.add_response('put_object', {},
                         expected_params={
                            'Body': botocore.stub.ANY,
                            'Bucket': bucket_name,
                            'Key': full_key2,
                            'ContentType': 'application/json'
                            }
                         )
    stubber.add_client_error('head_object',
                             service_error_meta={'Code': '404'},
                             expected_params={
                                'Bucket': bucket_name,
                                'Key': full_key3
                                }
                             )
    stubber.add_response('put_object', {},
                         expected_params={
                            'Body': botocore.stub.ANY,
                            'Bucket': bucket_name,
                            'Key': full_key3,
                            'ContentType': 'application/json'
                            }
                         )
    stubber.activate()
    mocker.patch('boto3.client', lambda service: s3_client)

    resource_dir = practice_filesystem[test_dir]

    metadata_path = practice_filesystem[metadata_file]
    csv_path = practice_filesystem[csv_file]
    mocker.patch(
        "sys.argv",
        ["", resource_dir, metadata_path, bucket_name,
         s3_dir, "--csv", csv_path]
    )
    copy_resources_s3.main()

    expected_csv_data = [
        {
            "filename": "example1.txt",
            "hash": "dc330ae2bc1d0b2edac442ed3f8245647cf5c0c0"
        },
        {
            "filename": "example3.jpeg",
            "hash": "e606bc6acc83666e1d40722e9c743a01e12e65ab"
        },
        {
            "filename": "example2.mp4",
            "hash": "a31e7f061d762f1e5099ecebfe6877310e5be420"
        },
        {
            "filename": "example4.jpeg",
            "hash": "e606bc6acc83666e1d40722e9c743a01e12e65ab"
        }
    ]

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]
        assert len(data) == 4
        for row in data:
            assert row in expected_csv_data


def test_add_metadata_indent(tmp_path):
    metadata_file = tmp_path / "media.json"
    metadata_file.write_text("[]")

    copy_resources_s3.add_metadata(
        [{"foo": 1, "bar": 2}],
        str(metadata_file)
    )

    text = metadata_file.read_text()

    assert text == """[
  {
    "foo": 1,
    "bar": 2
  }
]"""
