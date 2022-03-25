import argparse
from pathlib import Path


def validate_mbz(mbz_path, output_file):
    # Get html
        # Check for style attributes
        # Check for <script> elements
        # Check for <iframe> elements
    # Get external files
        # Check for sources not prefixed by s3 or k12.openstax
    # Get moodle files
        # Check for references to moodle uploads

    pass


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('mbz_path', type=str,
                        help='relative path to unzipped mbz')
    parser.add_argument('output_file', type=str,
                        help='Path to a file where flags will be outputted')
    args = parser.parse_args()

    mbz_path = Path(args.mbz_path).resolve(strict=True)
    output_file = Path(args.output_file)

    if not output_file.exists():
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("[]")

    validate_mbz(mbz_path, output_file)


if __name__ == "__main__":
    main()
