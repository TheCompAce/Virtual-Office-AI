
import os
import argparse
import zipfile

def create_zip(start_path, output_file, exclude):
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(start_path):
            # Exclude specified directories
            dirs[:] = [d for d in dirs if d not in exclude]

            # Exclude specified files
            files = [f for f in files if f not in exclude]

            for file in files:
                absolute_file_path = os.path.join(root, file)
                relative_file_path = os.path.relpath(absolute_file_path, start_path)
                zipf.write(absolute_file_path, arcname=relative_file_path)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Create a zip of a directory structure.')
    parser.add_argument('-d', '--directory', type=str, help='The directory to zip. Defaults to the current directory.', default='.')
    parser.add_argument('-o', '--output', type=str, help='The output file. Defaults to "archive.zip".', default='archive.zip')
    parser.add_argument('-e', '--exclude', type=str, help='Comma-separated list of files or directories to exclude.', default='')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    exclude = args.exclude.split(',')
    create_zip(args.directory, args.output, exclude)
