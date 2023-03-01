import os
from pathlib import Path
from mbtools import generate_html_content_data
import pytest
import csv


@pytest.fixture
def test_data_path():
    return Path(__file__).parent / "data/generate_html_content_data"


@pytest.fixture
def content(test_data_path):
    with open(test_data_path / "4ca6ab6d-231e-4000-b576-af7f3c021cf5.html",
                               "r") as f:
        main_variant = f.read()
    with open(
        test_data_path / "4ca6ab6d-231e-4000-b576-af7f3c021cf5" / "mm.html",
                         "r") as f:
        variant = f.read()

    input_expected_csv = csv.DictReader(
        open(test_data_path / "ib_input_instances_expected.csv", "r")
    )
    pset_expected_csv = csv.DictReader(
        open(test_data_path / "ib_pset_problems_expected.csv", "r")
    )

    return (main_variant, variant, input_expected_csv, pset_expected_csv)


def test_generate_html_content(tmp_path, mocker, content):
    (main_variant, variant, input_expected_csv, pset_expected_csv) = content

    os.mkdir(tmp_path / "html")
    os.mkdir(tmp_path / "output")
    os.mkdir(tmp_path / "html/4ca6ab6d-231e-4000-b576-af7f3c021cf5")

    html_dir = f"{tmp_path}/html"
    main_path = Path(html_dir) / "4ca6ab6d-231e-4000-b576-af7f3c021cf5.html"
    variant_path = (
        Path(html_dir) / "4ca6ab6d-231e-4000" "-b576-af7f3c021cf5" / "mm.html"
    )
    main_path.write_text(main_variant)
    variant_path.write_text(variant)

    mocker.patch("sys.argv", ["", html_dir, f"{tmp_path}/output"])

    generate_html_content_data.main()

    actual_ib_input = csv.DictReader(open(Path(f"{tmp_path}/output") /
                                     "ib_input_instances.csv"))
    expected_input_rows = list(input_expected_csv)
    actual_input_rows = list(actual_ib_input)
    assert len(expected_input_rows) == len(actual_input_rows)
    for item in expected_input_rows:
        assert item in actual_input_rows

    actual_ib_pset = csv.DictReader(open(Path(f"{tmp_path}/output") /
                                    "ib_pset_problems.csv"))

    expected_pset_rows = list(pset_expected_csv)
    actual_pset_rows = list(actual_ib_pset)
    assert len(expected_pset_rows) == len(actual_pset_rows)
    for item in expected_pset_rows:
        assert item in actual_pset_rows
