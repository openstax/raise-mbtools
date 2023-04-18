import pytest
import botocore.stub
import boto3
import os
import json
from mbtools import copy_resources_s3


test_dir = 'test_content/'
nested_dir = 'test_content/nested'

f1 = 'test_content/example1.txt'
f2 = 'test_content/example2.mp4'
f3 = 'test_content/example3.jpeg'
f4 = 'test_content/nested/example4.jpeg'

f1_data = {'txt_data': 2}
f2_data = {'mp4_data': 'video'}
f3_data = {'jpeg_data': 'picture'}
f4_data = {'jpeg_data': 'picture'}

index_file = "index.html"


@pytest.fixture
def practice_filesystem(tmp_path):

    (tmp_path / test_dir).mkdir()
    (tmp_path / nested_dir).mkdir()

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

    path_dict = {
                 index_file: str(tmp_path / index_file),
                 test_dir: str(tmp_path / test_dir),
                 f1: str(tmp_path / f1),
                 }
    return path_dict


def test_new_resource_hashes(practice_filesystem):
    assert (len(copy_resources_s3.resource_hashes(
               practice_filesystem[test_dir])) == 3
            )


def test_get_mime_type(practice_filesystem):
    assert os.path.exists(practice_filesystem[f1])
    assert (copy_resources_s3.get_mime_type(practice_filesystem[f1]) ==
            'application/json')


def test_upload_resources(practice_filesystem, mocker):
    s3_dir = 'resources'
    bucket_name = 'test-bucket'
    sha1_map = copy_resources_s3.resource_hashes(
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
    url_prefix = 'prefix/s3'
    resource_dir = practice_filesystem[test_dir]
    print(resource_dir)
    index_path = practice_filesystem[index_file]
    mocker.patch(
        "sys.argv",
        ["", resource_dir, bucket_name, s3_dir, url_prefix, index_path]
    )
    copy_resources_s3.main()
    stubber.assert_no_pending_responses()

    with open(index_path, 'r') as f:
        data = f.read()
    for key, value in sha1_map.items():
        assert key in data
        assert value['mime_type'] in data
        assert value['path'] in data
