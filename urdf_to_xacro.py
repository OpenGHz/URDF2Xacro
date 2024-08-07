import xml.etree.ElementTree as ET
import argparse


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

    def add_robot_attributes(self, attributes: dict):
        for attr, value in attributes.items():
            self.root.set(attr, value)

    def to_macro(self, params):
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

    def add_prefix_var(self, name):
        for joint in self.handle.findall("joint"):
            joint.set("name", f"${{{name}}}_{joint.get('name')}")
        for link in self.handle.findall("link"):
            link.set("name", f"${{{name}}}_{link.get('name')}")

    def save(self, path=None):
        path = path if path is not None else self.file_path
        self.tree.write(path, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":

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
        "-p",
        "--prefix",
        type=str,
        help="The prefix to add to the joint and link names",
        default="prefix",
    )
    args = parser.parse_args()
    input_path:str = args.input_urdf_path
    output_path:str = args.output_urdf_path
    prefix:str = args.prefix

    # configure joint limits
    from urdf_config import CONFIG

    joint_limits = CONFIG["joint_limits"]
    # modify URDF file
    urdfer = URDFer(input_path)
    urdfer.replace_joint_limits(joint_limits)
    urdfer.to_macro(prefix)
    urdfer.add_prefix_var(prefix)
    # save modified URDF file
    output_path = input_path.replace(".urdf", ".urdf.xacro") if output_path is None else output_path
    urdfer.save(output_path)

    # format the output file
    import subprocess

    result = subprocess.run(
        ["xmllint", "--format", output_path, "-o", output_path],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
