import os
import subprocess


def process_with_meshlab(input_filepath, output_filepath, script):
    command = [
        "meshlabserver",
        "-i",
        input_filepath,
        "-o",
        output_filepath,
        "-s",
        script,
    ]
    subprocess.run(command, check=True)
    print(f"Processed {input_filepath} -> {output_filepath}")


def process_directory(in_dir, out_dir, prefix, script):
    for filename in os.listdir(in_dir):
        if filename.endswith(".stl") or filename.endswith(".STL"):
            input_filepath = os.path.join(in_dir, filename)
            output_filepath = os.path.join(out_dir, prefix + filename)
            process_with_meshlab(input_filepath, output_filepath, script)


if __name__ == "__main__":
    import argparse, os

    current_directory = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(description="Simplify meshes using convex hulls")
    parser.add_argument(
        "-in", "--input_dir", type=str, help="Directory containing STL files"
    )
    parser.add_argument(
        "-out", "--output_dir", type=str, help="Directory to save simplified meshes"
    )
    parser.add_argument(
        "-pre",
        "--name_prefix",
        type=str,
        help="Prefix to add to simplified meshes",
        default="simplified_",
    )
    parser.add_argument(
        "-s",
        "--script_path",
        type=str,
        help="Path to MeshLab script for simplification",
        default=f"{current_directory}/meshlab.xml",
    )
    args = parser.parse_args()
    in_dir = args.input_dir
    out_dir = args.output_dir
    script = args.script_path
    name_prefix = args.name_prefix

    out_dir = out_dir if out_dir is not None else in_dir
    process_directory(in_dir, out_dir, name_prefix, script)
