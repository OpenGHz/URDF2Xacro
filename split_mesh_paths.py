import xml.etree.ElementTree as ET
import argparse
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from urdf_to_xacro import URDFer

parser = argparse.ArgumentParser(
    "Split mesh paths in URDF file to visual and collision paths"
)

parser.add_argument(
    "-path", "--input_urdf_path", type=str, help="Path to the input URDF file"
)
parser.add_argument(
    "-out", "--output_urdf_path", type=str, help="Path to the output URDF file"
)
parser.add_argument("-ov", "--old_visual_path", type=str, help="Old visual mesh path")
parser.add_argument(
    "-oc", "--old_collision_path", type=str, help="Old collision mesh path"
)
parser.add_argument("-nv", "--new_visual_path", type=str, help="New visual mesh path")
parser.add_argument(
    "-nc", "--new_collision_path", type=str, help="New collision mesh path"
)
parser.add_argument("-cc", "--create_collision", action="store_true")

args = parser.parse_args()

input_urdf_path: str = args.input_urdf_path
output_urdf_path: str = args.output_urdf_path
old_visual_path: str = args.old_visual_path
old_collision_path: str = args.old_collision_path
new_visual_path: str = args.new_visual_path
new_collision_path: str = args.new_collision_path
create_collision: bool = args.create_collision

output_urdf_path = input_urdf_path if output_urdf_path is None else output_urdf_path
old_collision_path = (
    old_visual_path if old_collision_path is None else old_collision_path
)
new_collision_path = (
    new_visual_path if new_collision_path is None else new_collision_path
)

urdfer = URDFer(input_urdf_path)
urdfer.split_mesh_paths(
    old_visual_path,
    new_visual_path,
    old_collision_path,
    new_collision_path,
    create_collision,
)
urdfer.save(output_urdf_path)
urdfer.format(output_urdf_path)

print("Done!")
