import os
from pathlib import Path
from uuid import UUID
from mbtools import inject_ib_uuids
import pytest


@pytest.fixture
def test_data_path():
    return Path(__file__).parent / "data/inject_ib_uuids"


@pytest.fixture
def single_input_and_variant_data(test_data_path):
    with open(test_data_path / "single_input_in.html", "r") as f:
        single_input_in = f.read()
    with open(test_data_path / "single_input_out.html", "r") as f:
        single_input_out = f.read()
    with open(test_data_path / "single_input_variant_in.html", "r") as f:
        single_input_variant_in = f.read()
    with open(test_data_path / "single_input_variant_out.html", "r") as f:
        single_input_variant_out = f.read()
    return (
        single_input_in,
        single_input_out,
        single_input_variant_in,
        single_input_variant_out
    )


@pytest.fixture
def pset_data(test_data_path):
    with open(test_data_path / "pset_in.html", "r") as f:
        pset_in = f.read()
    with open(test_data_path / "pset_out.html", "r") as f:
        pset_out = f.read()
    return pset_in, pset_out


@pytest.fixture
def mix_with_input_data(test_data_path):
    with open(test_data_path / "mix_in.html", "r") as f:
        mix_in = f.read()
    with open(test_data_path / "mix_out.html", "r") as f:
        mix_out = f.read()
    return mix_in, mix_out


@pytest.fixture
def autogenerated_uuid():
    return UUID("7080c78d-298b-40ba-a68d-55d6a93b00fb")


def test_inject_ib_ids_input_and_cta(
    tmp_path, mocker, autogenerated_uuid, pset_data, mix_with_input_data
):
    pset_in, pset_out = pset_data
    mix_in, mix_out = mix_with_input_data

    os.mkdir(tmp_path / "html")
    html_dir = f"{tmp_path}/html"
    fp1 = Path(html_dir) / "page_1.html"
    fp2 = Path(html_dir) / "page_2.html"
    fp1.write_text(pset_in)
    fp2.write_text(mix_in)

    mocker.patch(
        "mbtools.inject_ib_uuids.uuid4",
        lambda: autogenerated_uuid
    )

    mocker.patch(
        "sys.argv",
        ["", html_dir]
    )

    inject_ib_uuids.main()

    with open(fp1, 'r') as f:
        result = f.read()
        assert pset_out == result

    with open(fp2, 'r') as f:
        result = f.read()
        print(result)
        assert mix_out == result


def test_inject_ib_ids_variant(
    tmp_path, mocker, autogenerated_uuid, single_input_and_variant_data
):
    (single_input_in,
     single_input_out,
     single_input_variant_in,
     single_input_variant_out
     ) = single_input_and_variant_data

    html_dir = f"{tmp_path}/html"
    os.mkdir(html_dir)
    os.mkdir(html_dir + "/page_1")
    fp1 = Path(html_dir) / "page_1.html"
    fp2 = Path(html_dir) / "page_1" / "page_1.html"
    fp1.write_text(single_input_in)
    fp2.write_text(single_input_variant_in)

    mocker.patch(
        "mbtools.inject_ib_uuids.uuid4",
        lambda: autogenerated_uuid
    )

    mocker.patch(
        "sys.argv",
        ["", html_dir]
    )

    inject_ib_uuids.main()

    with open(fp1, 'r') as f:
        result = f.read()
        assert single_input_out == result

    with open(fp2, 'r') as f:
        result = f.read()
        assert single_input_variant_out == result
