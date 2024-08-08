import xml.etree.ElementTree as ET
from typing import Dict


class URDFer(object):
    def __init__(self, file_path) -> None:
        self.file_path = file_path
        self.tree = ET.parse(file_path)
        self.root = self.tree.getroot()
        self.robot_name = self.root.get("name")
        index = self.is_macro()
        self._is_macro = index is not None
        self.handle = (
            self.root if not self._is_macro else self.root.findall("xacro:macro")[index]
        )
        print(f"Robot name: {self.robot_name}")
        assert self.robot_name is not None, "Robot name not found"

    def is_macro(self):
        for index, macro in enumerate(self.root.findall("xacro:macro")):
            if macro.get("name") == self.robot_name:
                return index
        return None

    def replace_joint_limits(self, joint_limits):
        for joint in self.handle.findall("joint"):
            joint_name = joint.get("name")
            if joint_name in joint_limits:
                limit_element = joint.find("limit")
                if limit_element is not None:
                    new_limits = joint_limits[joint_name]
                    if "lower" in new_limits:
                        limit_element.set("lower", str(new_limits["lower"]))
                    if "upper" in new_limits:
                        limit_element.set("upper", str(new_limits["upper"]))
                    if "effort" in new_limits:
                        limit_element.set("effort", str(new_limits["effort"]))
                    if "velocity" in new_limits:
                        limit_element.set("velocity", str(new_limits["velocity"]))

    def replace_link_inertial(self, link_inertial: Dict[str, dict]):
        if self._is_macro:
            for key, value in link_inertial.items():
                link_inertial[f"${{prefix}}{key}"] = value
                del link_inertial[key]
        for link in self.handle.findall("link"):
            link_name = link.get("name")
            if link_name in link_inertial:
                inertial_element = link.find("inertial")
                if inertial_element is not None:
                    for key, value in link_inertial[link_name].items():
                        handle = inertial_element.find(key)
                        if isinstance(value, dict):
                            for k, v in value.items():
                                handle.set(k, str(v))
                        else:
                            handle.set("value", str(value))
            else:
                print(f"Link {link_name} not found in link_inertial config")

    def add_robot_attributes(self, attributes: dict):
        for attr, value in attributes.items():
            self.root.set(attr, value)

    def to_xacro_style(self, params):
        if self._is_macro:
            print("Already a macro")
            return
        # 添加 xacro 标志
        self.add_robot_attributes({"xmlns:xacro": "http://wiki.ros.org/xacro"})
        # 获取 <robot> 标签内的所有元素
        robot_children = list(self.root)
        # 清空 <robot> 标签内的元素
        for child in robot_children:
            self.root.remove(child)
        # 创建新的 <xacro:macro> 标签
        xacro_macro = ET.Element(
            "xacro:macro", {"name": self.robot_name, "params": params}
        )
        # 将之前的元素添加到 <xacro:macro> 标签内
        for child in robot_children:
            xacro_macro.append(child)
        # 将 <xacro:macro> 标签添加到 <robot> 标签内
        self.root.append(xacro_macro)
        # 修改全局变量
        self._is_macro = True
        self.handle = xacro_macro
        self.add_prefix_var(prefix)

    def add_prefix_var(self, name):
        for joint in self.handle.findall("joint"):
            parent = joint.find("parent")
            parent.set("link", f"${{{name}}}{parent.get('link')}")
            child = joint.find("child")
            child.set("link", f"${{{name}}}{child.get('link')}")
            joint.set("name", f"${{{name}}}{joint.get('name')}")
        for link in self.handle.findall("link"):
            link.set("name", f"${{{name}}}{link.get('name')}")

    def save(self, path=None):
        path = path if path is not None else self.file_path
        self.tree.write(path, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    import argparse
    from importlib import import_module
    import os, sys

    current_dir = os.path.dirname(os.path.abspath(__file__))
    modify_choices = ["joints_limit", "links_inertial", "all"]
    parser = argparse.ArgumentParser(description="Replace joint limits in URDF file")
    parser.add_argument(
        "-in", "--input_urdf_path", type=str, help="Path to the URDF file"
    )
    parser.add_argument(
        "-out",
        "--output_urdf_path",
        type=str,
        help="Path to the modified URDF file",
        default=None,
    )
    parser.add_argument(
        "-cfg",
        "--config_file_path",
        type=str,
        help="Path to the configuration .py file",
        default=f"{current_dir}/example_config/urdf_config.py",
    )
    parser.add_argument(
        "-p",
        "--prefix",
        type=str,
        help="The prefix to add to the joint and link names",
        default="prefix",
    )
    parser.add_argument(
        "-ml",
        "--modify_list",
        type=str,
        nargs="*",
        help="List of components to modify",
        default=[],
        choices=modify_choices,
    )
    args = parser.parse_args()
    input_path: str = args.input_urdf_path
    output_path: str = args.output_urdf_path
    config_path: str = args.config_file_path
    modify_list: list = args.modify_list
    prefix: str = args.prefix

    output_path = (
        input_path.replace(".urdf", ".xacro") if output_path is None else output_path
    )

    # import configuration file and get CONFIG dict
    sys.path.insert(0, os.path.dirname(config_path))
    module_name = os.path.basename(config_path).replace(".py", "")
    print(f"Importing configuration file from {config_path}")
    config = import_module(module_name)
    CONFIG = config.CONFIG

    # initialize URDFer
    urdfer = URDFer(input_path)
    # modify URDF file
    modify_list = modify_choices[:-1] if "all" in modify_list else modify_list
    process_dict = {
        "joints_limit": urdfer.replace_joint_limits,
        "links_inertial": urdfer.replace_link_inertial,
    }
    for key in modify_list:
        process_dict[key](CONFIG[key])
    # change the URDF file to xacro style
    urdfer.to_xacro_style(prefix)
    # save modified URDF file
    urdfer.save(output_path)
    print(f"Output file saved to {output_path}")

    print("Formatting the output file...")
    import subprocess

    result = subprocess.run(
        ["xmllint", "--format", output_path, "-o", output_path],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    print("Done!")
