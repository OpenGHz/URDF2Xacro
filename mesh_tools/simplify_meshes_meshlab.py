import os
import subprocess


def process_with_meshlab(filepath, script):
    output_filepath = os.path.splitext(filepath)[0] + "_simplified.STL"
    command = ["meshlabserver", "-i", filepath, "-o", output_filepath, "-s", script]
    subprocess.run(command, check=True)
    print(f"Processed {filepath} -> {output_filepath}")


def process_directory(directory, script):
    for filename in os.listdir(directory):
        if filename.endswith(".stl") or filename.endswith(".STL"):
            filepath = os.path.join(directory, filename)
            process_with_meshlab(filepath, script)


if __name__ == "__main__":
    import argparse, os

    current_directory = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(description="Simplify meshes using convex hulls")
    parser.add_argument(
        "-in", "--directory", type=str, help="Directory containing STL files"
    )
    parser.add_argument(
        "-s",
        "--script",
        type=str,
        help="Path to MeshLab script for simplification",
        default=f"{current_directory}/meshlab.xml",
    )
    args = parser.parse_args()
    directory = args.directory
    script = args.script
    process_directory(directory, script)
