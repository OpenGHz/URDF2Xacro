import re
import argparse
from typing import List
import json
import os


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
    default=1e-4,
)
args = parser.parse_args()
input_path: str = args.input_doc_path
output_path: str = args.output_json_path
threshold: float = args.threshold
assert input_path.endswith(".txt"), "Input file must be a .txt file"
output_path = (
    input_path.replace(".txt", ".json") if output_path is None else output_path
)

# 读取.doc文件
with open(input_path, "r", encoding="utf-8") as file:
    document = file.read()

# 正则表达式匹配Link和对应的惯量数据
link_pattern = re.compile(r"LINK\d+")
tensor_pattern = re.compile(
    r"Lxx = ([\d\.-]+)\s+Lxy = ([\d\.-]+)\s+Lxz = ([\d\.-]+)\s+L(?:yx = |x = )([\d\.-]+)\s+Lyy = ([\d\.-]+)\s+Lyz = ([\d\.-]+)\s+L(?:zx = |z = )([\d\.-]+)\s+L(?:zy = |zz = )([\d\.-]+)\s+Lzz = ([\d\.-]+)"
)

# 解析文件
links: List[str] = link_pattern.findall(document)
tensors = tensor_pattern.findall(document)
# 生成惯量数据字典
link_inertial = {}
intertia_keys = ["ixx", "ixy", "ixz", "iyy", "iyz", "izz"]
for link, tensor in zip(links, tensors):
    link = link.lower()
    link_inertial[link] = {"inertia": {}}
    for key, value in zip(intertia_keys, tensor):
        value = float(value)
        if abs(value) < threshold:
            value = 0
        link_inertial[link]["inertia"][key] = value

# 如果目标路径存在，则在已有的数据里更新
if os.path.exists(output_path):
    with open(output_path, "r", encoding="utf-8") as file:
        old_data: dict = json.load(file)
    old_data.update(link_inertial)
    link_inertial = old_data

# 保存惯量数据
with open(output_path, "w", encoding="utf-8") as file:
    json.dump(link_inertial, file, indent=4)
