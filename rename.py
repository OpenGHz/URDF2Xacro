import os
import re
import argparse

"""
examples:
python3 replace_name.py . 'in_name' 'out_name'
python3 replace_name.py . 'package://package_name' 'package://new_name'
"""


def replace_in_file(file_path, pattern, replacement):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin1") as file:
            content = file.read()

    new_content = re.sub(pattern, replacement, content)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(new_content)


def rename_items(root_dir, pattern, replacement):
    for root, dirs, files in os.walk(root_dir, topdown=False):
        for name in files:
            old_file_path = os.path.join(root, name)
            new_file_name = re.sub(pattern, replacement, name)
            new_file_path = os.path.join(root, new_file_name)

            replace_in_file(old_file_path, pattern, replacement)

            if new_file_path != old_file_path:
                os.rename(old_file_path, new_file_path)

        for name in dirs:
            old_dir_path = os.path.join(root, name)
            new_dir_name = re.sub(pattern, replacement, name)
            new_dir_path = os.path.join(root, new_dir_name)

            if new_dir_path != old_dir_path:
                os.rename(old_dir_path, new_dir_path)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Replace a pattern in the names of files and directories and in the content of files."
    )
    parser.add_argument(
        "-rd",
        "--root_directory",
        help="The root directory where the search will start.",
        default=".",
    )
    parser.add_argument("-in", "--search_pattern", help="The pattern to search for.")
    parser.add_argument(
        "-out", "--replacement_string", help="The string to replace the pattern with."
    )
    args = parser.parse_args()

    root_directory = os.path.expanduser(args.root_directory)
    search_pattern = args.search_pattern
    replacement_string = args.replacement_string

    rename_items(root_directory, search_pattern, replacement_string)
