import pytest
import botocore.stub
import boto3
import os
import json
from mbtools import copy_resources_s3


test_dir = 'test_content/'
f1 = 'test_content/example1.txt'
f2 = 'test_content/example2.mp4'
f3 = 'test_content/example3.jpeg'

f1_data = {"txt_data": 2}
f2_data = {"mp4_data": "video"}
f3_data = {"jpeg_data": "picture"}

metadata_file = "metadata/tags.json"

metadata_tags = [{"mime_type": "video/mp4",
                  "original_filename": "Example_2.mp4",
                  "s3_key": "contents/raise/resources/f83a0cabe1fc9bfe35d70947e9c0ed8e5285b76e",
                  "sha1": "f83a0cabe1fc9bfe35d70947e9c0ed8e5285b76e"
                  },
                 {"mime_type": "video/mp4",
                  "sha1": "d3614ca5260104f401a96415b448943725c2feb0",
                  "original_filename": "TwoLines.mp4",
                  "s3_key": "contents/raise/resources/d3614ca5260104f401a96415b448943725c2feb0"}
                 ]

s3_response = {'Contents':
               [
                {'Key': 'contents/raise/resources/51ca61528ae211e79e1f9ad0bd53621737312dd5',
                 },
                {'Key': 'contents/raise/resources/5929d87f8eaa15037cbb3166d2947c1e5d168387'
                 }
                ]
               }


@pytest.fixture
def practice_filesystem(tmp_path):

    (tmp_path / test_dir).mkdir()
    with open(str(tmp_path / f1), 'w') as f:
        json.dump(f1_data, f)
    with open(str(tmp_path / f2), 'w') as f:
        json.dump(f2_data, f)
    with open(str(tmp_path / f3), 'w') as f:
        json.dump(f3_data, f)

    (tmp_path / "metadata").mkdir()
    with open(str(tmp_path / metadata_file), 'w') as f:
        json.dump(metadata_tags, f)

    path_dict = {metadata_file: str(tmp_path / metadata_file),
                 test_dir: str(tmp_path / test_dir),
                 f1: str(tmp_path / f1)
                 }
    return path_dict


def test_existing_metadata_hashes(practice_filesystem):
    assert (copy_resources_s3.existing_metadata_hashes(practice_filesystem[metadata_file]) ==
           [metadata_tags[0]["sha1"], metadata_tags[1]["sha1"]])
    try:
        copy_resources_s3.existing_metadata_hashes("")
    except FileExistsError:
        assert True


def test_new_resorce_hashes(practice_filesystem):
    assert(len(copy_resources_s3.new_resource_hashes(practice_filesystem[test_dir])) == 3)
    assert(copy_resources_s3.new_resource_hashes("") == FileNotFoundError)


def test_compare_and_remove_hashes():
    new_hashes = ['123', '456', '789']
    existing_hashes = ['123']
    hashes_for_update = ['456', '789']
    assert (copy_resources_s3.compare_and_remove_hashes(new_hashes,
                                                        existing_hashes) ==
            hashes_for_update)
    assert (copy_resources_s3.compare_and_remove_hashes([], existing_hashes) ==
            [])


def test_existing_s3_hashes(practice_filesystem, mocker):
    s3_client = boto3.client('s3')
    stubber = botocore.stub.Stubber(s3_client)

    s3_dir = 'resources/'
    bucket_name = 'test-bucket'
    expected_params = {'Bucket': bucket_name,
                       'Prefix': s3_dir}
    stubber.add_response('list_objects', s3_response, expected_params)
    stubber.activate()
    mocker.patch("boto3.client", lambda service: s3_client)

    # extract the hash value from the response for comparison
    h1 = s3_response['Contents'][0]['Key'].split('/')[-1].split('.')[0]
    h2 = s3_response['Contents'][1]['Key'].split('/')[-1].split('.')[0]

    assert (copy_resources_s3.existing_s3_hashes(bucket=bucket_name, s3_dir=s3_dir) ==
            [h1, h2])


def test_get_mime_type(practice_filesystem):
    assert os.path.exists(practice_filesystem[f1])
    assert copy_resources_s3.get_mime_type(practice_filesystem[f1]) == "application/json"


# def test_upload_resources(practice_filesystem, mocker):
#     s3_client = boto3.client('s3')
#     stubber = botocore.stub.Stubber(s3_client)

#     s3_dir = 'resources/'
#     bucket_name = 'test-bucket'
#     expected_params_list = {'Bucket': bucket_name,
#                        'Prefix': s3_dir}
#     stubber.add_response('list_objects', s3_response, expected_params_list)

#     expected_params_put1 = {'Filename': ,
#                             'Bucket': bucket_name,
#                             'Key':}
#     expected_params_put2 = {'Filename': ,
#                             'Bucket': bucket_name,
#                             'Key':}

#     stubber.add_response('put_object', {}, )
#     stubber.activate()
#     mocker.patch("boto3.client", lambda service: s3_client)

#     resource_dir = practice_filesystem[test_dir]
#     metadata_dir = practice_filesystem[metadata_file]
#     copy_resources_s3.upload_resources(resource_dir=resource_dir,
#                                        metadata_dir=metadata_dir,
#                                        bucket=bucket_name,
#                                        s3_dir=s3_dir)

#     with open(practice_filesystem[metadata_file], 'r') as f:
#         data = json.load(f)
#     print(data)
