import os
from pathlib import Path
from mbtools import generate_html_content_data
import pytest


@pytest.fixture
def test_data_path():
    return Path(__file__).parent / "data/generate_html_content_data"


@pytest.fixture
def html_content(test_data_path):
    with open(test_data_path /
              "4ca6ab6d-231e-4000-b576-af7f3c021cf5.html", "r") as f:
        main_variant = f.read()
    with open(
        test_data_path /
        "4ca6ab6d-231e-4000-b576-af7f3c021cf5" / "mm.html", "r"
    ) as f:
        variant = f.read()

    with open(test_data_path / "ib_input_instances_expected.csv", "r") as f:
        input_expected_csv = f.read()
    with open(test_data_path / "ib_pset_problems_expected.csv", "r") as f:
        pset_expected_csv = f.read()

    return (main_variant, variant, input_expected_csv, pset_expected_csv)


def test_generate_html_content(tmp_path, mocker, html_content):
    (main_variant,
     variant,
     input_expected_csv,
     pset_expected_csv) = html_content

    os.mkdir(tmp_path / "html")
    os.mkdir(tmp_path / "html/4ca6ab6d-231e-4000-b576-af7f3c021cf5")

    html_dir = f"{tmp_path}/html"
    main_path = Path(html_dir) / "4ca6ab6d-231e-4000-b576-af7f3c021cf5.html"
    variant_path = Path(html_dir) / "4ca6ab6d-231e-4000"\
        "-b576-af7f3c021cf5" / "mm.html"
    main_path.write_text(main_variant)
    variant_path.write_text(variant)
    input_expected = Path(html_dir) / "ib_input_instances_expected.csv"
    pset_expected = Path(html_dir) / "ib_pset_problems_expected.csv"
    input_expected.write_text(input_expected_csv)
    pset_expected.write_text(pset_expected_csv)

    mocker.patch("sys.argv", ["", html_dir, html_dir])

    generate_html_content_data.main()

    with open(
        Path(html_dir) / "ib_input_instances_expected.csv"
    ) as expected_ib_inputs, open(
        Path(html_dir) / "ib_input_instances.csv"
    ) as ib_inputs:
        actual = ib_inputs.readlines()
        expected = expected_ib_inputs.readlines()
        for line in expected:
            assert line in actual
        assert len(actual) == len(expected)

    with open(
        Path(html_dir) / "ib_pset_problems_expected.csv"
    ) as expected_pset_problems, open(
        Path(html_dir) / "ib_pset_problems.csv"
    ) as ib_psets:
        actual = ib_psets.readlines()
        expected = expected_pset_problems.readlines()
        for line in expected:
            assert line in actual
        assert len(actual) == len(expected)
