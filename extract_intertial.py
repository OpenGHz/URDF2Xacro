import re
import argparse
from typing import List, Optional
import json
import os

default_thresh = 1e-5
parser = argparse.ArgumentParser(description="Extract inertial data from a .txt file")
parser.add_argument("-in", "--input_text_path", type=str, help="Path to the .txt file")
parser.add_argument(
    "-out", "--output_json_path", type=str, help="Path to the .json file"
)
parser.add_argument(
    "-t",
    "--threshold",
    type=float,
    help="Threshold for filtering out small inertial values",
    default=default_thresh,
)
parser.add_argument(
    "-ln",
    "--links_name",
    type=str,
    nargs="*",
    help="Name of the links in the URDF file",
)
args = parser.parse_args()
input_path: str = args.input_text_path
output_path: str = args.output_json_path
threshold: float = args.threshold
links_name: Optional[List[str]] = args.links_name
assert input_path.endswith(".txt"), "Input file must be a .txt file"
output_path = (
    input_path.replace(".txt", ".json") if output_path is None else output_path
)
# 读取.txt文件
with open(input_path, "r", encoding="utf-8") as file:
    document = file.read()

# 正则表达式匹配惯量数据
tensor_pattern = re.compile(
    r"Lxx = ([\d\.-]+)\s+Lxy = ([\d\.-]+)\s+Lxz = ([\d\.-]+)\s+L(?:yx = |x = )([\d\.-]+)\s+Lyy = ([\d\.-]+)\s+Lyz = ([\d\.-]+)\s+L(?:zx = |z = )([\d\.-]+)\s+L(?:zy = |zz = )([\d\.-]+)\s+Lzz = ([\d\.-]+)"
)

# 解析文件
if links_name is None:
    link_pattern = re.compile(r"(link\d*|\w+_link\d*)")
    links_name = link_pattern.findall(document)
    assert (
        len(links_name) > 0
    ), "No supported link names found in the document, please modify or provide them through the command line"
    print(f"Found links: {links_name}")
tensors = tensor_pattern.findall(document)
assert len(tensors) == len(links_name), "Number of link names and tensors do not match"

# 生成惯量数据字典
link_inertial = {}
intertia_keys = ["ixx", "ixy", "ixz", "iyy", "iyz", "izz"]
for link, tensor in zip(links_name, tensors):
    link = link.lower()
    link_inertial[link] = {"inertia": {}}
    for key, value in zip(intertia_keys, tensor):
        # print(f"{link} {key} = {value}")
        value = float(value)
        if abs(value) < threshold:
            # print(f"Filtering out small value: {value}")
            value = default_thresh
        link_inertial[link]["inertia"][key] = value

# 如果目标路径存在，则在已有的数据里更新
if os.path.exists(output_path):
    print("Updating existing data")
    with open(output_path, "r", encoding="utf-8") as file:
        old_data: dict = json.load(file)
    old_data.update(link_inertial)
    link_inertial = old_data
else:
    print("No links_inertial.json file found")

# 保存惯量数据
with open(output_path, "w", encoding="utf-8") as file:
    json.dump(link_inertial, file, indent=4)
