import pytest
import botocore.stub
import boto3
import os
import json
from mbtools import copy_resources_s3
from bs4 import BeautifulSoup

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


def test_resource_hashes(practice_filesystem):
    assert (len(copy_resources_s3.resource_hashes(
               practice_filesystem[test_dir])[0]) == 3
            )
    assert (len(copy_resources_s3.resource_hashes(
               practice_filesystem[test_dir])[1]) == 1
            )


def test_get_mime_type(practice_filesystem):
    assert os.path.exists(practice_filesystem[f1])
    assert (copy_resources_s3.get_mime_type(practice_filesystem[f1]) ==
            'application/json')


def test_upload_resources(practice_filesystem, mocker):
    s3_dir = 'resources'
    bucket_name = 'test-bucket'
    sha1_map, duplicates = copy_resources_s3.resource_hashes(
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
    stubber.add_response('head_object', {},
                         expected_params={
                                'Bucket': bucket_name,
                                'Key': full_key3
                                }
                         )

    stubber.activate()
    mocker.patch('boto3.client', lambda service: s3_client)
    url_prefix = 'https://domain.org/prefix/s3'
    resource_dir = practice_filesystem[test_dir]
    index_path = practice_filesystem[index_file]
    mocker.patch(
        "sys.argv",
        ["", resource_dir, bucket_name, s3_dir, url_prefix, index_path]
    )
    copy_resources_s3.main()
    stubber.assert_no_pending_responses()

    with open(index_path, 'r') as f:
        file_data = f.read()
    soup = BeautifulSoup(file_data, "html.parser")
    table = soup.find("table", class_="table table-striped table-bordered")
    rows = table.find_all("tr")
    sha_data_from_index = []

    for row in rows:
        cells = row.find_all("td")
        data = [cell for cell in cells]
        # first element is empty because <tr> uses <th> instead of <td>.
        if data == []:
            continue

        # test prefix
        assert os.path.dirname(data[2].text.strip()) == url_prefix

        sha_data_from_index.append({
            'path': data[0].text.strip(),
            'mime_type': data[1].text.strip(),
            'sha1': data[2].text.strip().split("/")[-1]
        })

    sha_map_data = []
    for key, value in sha1_map.items():
        sha_map_data.append({
            'path': os.path.relpath(value['path'],
                                    practice_filesystem[test_dir]),
            'mime_type': value['mime_type'],
            'sha1': key
        })
    for duplicate in duplicates:
        duplicate['path'] = os.path.relpath(duplicate['path'],
                                            practice_filesystem[test_dir])

    sha_map_data.extend(duplicates)
    # Make sure each table row corresponds with the correct key, path, and
    # mime_type in sha_map
    assert len(sha_map_data) == len(sha_data_from_index)

    for value in sha_map_data:
        assert value in sha_data_from_index
