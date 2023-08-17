import os
import json
import argparse

def create_path_map(start_path, output_file, exclude):
    path_map = {}
    for root, dirs, files in os.walk(start_path):
        # Exclude specified directories
        dirs[:] = [d for d in dirs if d not in exclude]

        # Exclude specified files
        files = [f for f in files if f not in exclude]

        relative_root = os.path.relpath(root, start_path)
        path_map[relative_root] = files

    with open(output_file, 'w') as f:
        json.dump(path_map, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a JSON map of a directory structure.')
    parser.add_argument('-d', '--directory', type=str, help='The directory to map. Defaults to the current directory.', default='.')
    parser.add_argument('-o', '--output', type=str, help='The output file. Defaults to "paths.json".', default='paths.json')
    parser.add_argument('-e', '--exclude', type=str, help='Comma-separated list of files or directories to exclude.', default='')
    args = parser.parse_args()

    exclude = args.exclude.split(',')
    create_path_map(args.directory, args.output, exclude)
