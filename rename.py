import os
import re
import argparse

"""
examples:
python3 replace_name.py -path package_path -in 'in_name' -out 'out_name'
python3 replace_name.py -path package_path -in 'path://path_name' -out 'path://new_name'
"""


def is_binary_file(file_path):
    try:
        with open(file_path, "rb") as file:
            chunk = file.read(1024)
            if b"\0" in chunk:  # 检查是否有空字节
                return True
        return False
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return False


def replace_in_file(file_path, pattern, replacement):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
    except UnicodeDecodeError:
        print(f"Ignore modifying contents in {file_path}")
    else:
        new_content = re.sub(pattern, replacement, content)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(new_content)


def rename_items(root_dir, pattern, replacement):
    for root, dirs, files in os.walk(root_dir, topdown=False):
        # print(f"Processing {root}")
        for name in files:
            # print("Processing file: ", name)
            old_file_path = os.path.join(root, name)
            new_file_name = re.sub(pattern, replacement, name)
            new_file_path = os.path.join(root, new_file_name)

            # Replace the pattern in the content of the file
            if ".STL" not in name:  # skip STL files
                # print(f"Modifying contents in {old_file_path}")
                replace_in_file(old_file_path, pattern, replacement)
            else:
                print(f"Ignore modifying contents in {old_file_path}")

            if new_file_path != old_file_path:
                os.rename(old_file_path, new_file_path)

        for name in dirs:
            # print("Processing directory: ", name)
            old_dir_path = os.path.join(root, name)
            new_dir_name = re.sub(pattern, replacement, name)
            new_dir_path = os.path.join(root, new_dir_name)

            if new_dir_path != old_dir_path:
                os.rename(old_dir_path, new_dir_path)


def rename_path(path, pattern, replacement):
    dir = os.path.dirname(path)
    old_name = os.path.basename(path)
    new_name = re.sub(pattern, replacement, old_name)
    new_path = os.path.join(dir, new_name)

    if new_path != path:
        os.rename(path, new_path)

    return new_path


def replace_mesh_paths(
    urdf_path,
    old_visual_path,
    old_collision_path,
    new_visual_path,
    new_collision_path,
) -> None:
    # 读取URDF文件内容
    with open(urdf_path, "r") as file:
        urdf_content = file.read()
    # 替换 <collision> 中的路径
    urdf_content = re.sub(
        r'(<collision>[\s\S]*?<mesh filename=")'
        + re.escape(old_collision_path)
        + r'([^"]+")',
        r"\1" + new_collision_path + r"\2",
        urdf_content,
    )

    # 替换 <visual> 中的路径
    urdf_content = re.sub(
        r'(<visual>[\s\S]*?<mesh filename=")'
        + re.escape(old_visual_path)
        + r'([^"]+")',
        r"\1" + new_visual_path + r"\2",
        urdf_content,
    )

    with open(urdf_path, "w") as file:
        file.write(urdf_content)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Replace a pattern in the names of files and directories and in the content of files."
    )
    parser.add_argument(
        "-path", "--package_path", help="The path of your URDF package."
    )
    parser.add_argument("-in", "--search_pattern", help="The pattern to search for.")
    parser.add_argument(
        "-out", "--replacement_string", help="The string to replace the pattern with."
    )

    parser.add_argument(
        "-mesh",
        "--replace_mesh_path",
        nargs=5,
        help="Replace the mesh file paths in the URDF file.",
        metavar=(
            "urdf_path",
            "old_visual_path",
            "old_collision_path",
            "new_visual_path",
            "new_collision_path",
        ),
    )

    args = parser.parse_args()

    replace_mesh_path = args.replace_mesh_path
    if replace_mesh_path is not None:
        replace_mesh_paths(*replace_mesh_path)
    else:
        path = os.path.expanduser(args.package_path)
        search_pattern = args.search_pattern
        replacement_string = args.replacement_string
        rename_items(path, search_pattern, replacement_string)
        rename_path(path, search_pattern, replacement_string)
    print("Done!")
