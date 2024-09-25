import xml.etree.ElementTree as ET
from typing import Dict, Optional
import subprocess, os, sys
from copy import deepcopy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rename import replace_in_file


class URDFer(object):
    def __init__(self, file_path) -> None:
        self.file_path = file_path
        self.tree = ET.parse(file_path)
        self.root = self.tree.getroot()
        self.robot_name = self.root.get("name")
        macro = self.is_macro()
        self._is_macro = macro is not None
        is_xacro = file_path.endswith(".xacro")
        self._is_xacro = is_xacro if not self._is_macro else True
        self._to_xacro = False
        self.handle = self.root if not self._is_macro else macro
        print(f"Robot name: {self.robot_name}")
        assert self.robot_name is not None, "Robot name not found"

    def is_macro(self):
        for item in list(self.root):
            # useless methods
            # ET.register_namespace('xacro', 'http://wiki.ros.org/xacro')
            # print(item.tag)
            # print(self.root.get('{http://wiki.ros.org/xacro}macro'))
            if "macro" in item.tag and item.get("name") == self.robot_name:
                return item
        return None

    def replace_joint_limits(self, joint_limits):
        for joint in self.handle.findall("joint"):
            joint_name = joint.get("name")
            if joint_name in joint_limits:
                limit_element = joint.find("limit")
                new_limits = joint_limits[joint_name]
                continuous = None in (new_limits["lower"], new_limits["upper"])
                if continuous:
                    joint.set("type", "continuous")
                    continue
                else:
                    joint.set("type", "revolute")
                if limit_element is None:
                    # create a new limit element
                    limit_element = ET.Element("limit")
                    joint.append(limit_element)
                # update the limit element
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
                virtual = link_inertial[link_name] is None
                if virtual:
                    continue
                if inertial_element is None:
                    # create a new inertial element
                    inertial_element = ET.Element("inertial")
                    link.append(inertial_element)
                # update the inertial element
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
        self._to_xacro = True
        self._is_xacro = True
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

    def split_mesh_paths(
        self,
        old_visual_path,
        new_visual_path,
        old_collision_path,
        new_collision_path,
        create_collision,
    ):
        for link in self.handle.findall("link"):
            visuals = link.findall("visual")
            collisions = link.findall("collision")

            if len(visuals) > 0:
                for visual in visuals:
                    geo = visual.find("geometry")
                    # create collision tag if it doesn't exist
                    if len(collisions) == 0 and create_collision:
                        collision = ET.Element("collision")
                        collision.append(visual.find("origin"))
                        collision.append(deepcopy(geo))
                        link.append(collision)
                    mesh_handle = geo.find("mesh")
                    new_name = mesh_handle.get("filename").replace(
                        old_visual_path, new_visual_path
                    )
                    mesh_handle.set("filename", new_name)
            else:
                print(f"There is no visual tag in {link.get('name')}")

            collisions = link.findall("collision")  # update the collisions list
            if len(collisions) > 0:
                for collision in collisions:
                    geo = collision.find("geometry")
                    mesh_handle = geo.find("mesh")
                    new_name = mesh_handle.get("filename").replace(
                        old_collision_path, new_collision_path
                    )
                    mesh_handle.set("filename", new_name)
            else:
                print(f"There is no collision tag in {link.get('name')}")

    @staticmethod
    def format(output_path):
        result = subprocess.run(
            ["xmllint", "--format", output_path, "-o", output_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return result

    def save(self, path=None):
        path = path if path is not None else self.file_path
        self.tree.write(path, encoding="utf-8", xml_declaration=True, method="xml")
        if not self._to_xacro and self._is_xacro:
            self.restore_xacro(path)

    def restore_xacro(self, path):
        replace_in_file(path, ":ns0", ":xacro")
        replace_in_file(path, "ns0:", "xacro:")


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
    assert os.path.exists(config_path), f"Configuration file not found at {config_path}"
    sys.path.insert(0, os.path.dirname(config_path))
    module_name = os.path.basename(config_path).replace(".py", "")
    print(f"Importing configuration file from {config_path}")
    config = import_module(module_name)
    CONFIG: Optional[dict] = config.CONFIG

    # initialize URDFer
    urdfer = URDFer(input_path)
    # modify URDF file
    modify_list = modify_choices[:-1] if "all" in modify_list else modify_list
    process_dict = {
        "joints_limit": urdfer.replace_joint_limits,
        "links_inertial": urdfer.replace_link_inertial,
    }
    if CONFIG is not None:
        for key in modify_list:
            value = CONFIG.get(key)
            if value is not None:
                print(f"Modifying {key}...")
                process_dict[key](value)
    # change the URDF file to xacro style
    urdfer.to_xacro_style(prefix)
    # save modified URDF file
    urdfer.save(output_path)
    print(f"Output file saved to {output_path}")

    print("Formatting the output file...")
    urdfer.format(output_path)
    print("Done!")
