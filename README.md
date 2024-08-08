# URDF to Xacro Converter

**Tools for modifying URDF packages and converting `URDF` into well organized `Xacro`.**

## Overview

This set of tools helps you modify your URDF ROS package and streamlines the process of converting URDF files into Xacro format, making your robot modeling workflow more efficient.

## Features

- **Package Renaming**: Replacing matching parts in all folders, files and contents in your URDF ROS package.
- **URDF Modifying**: Modify URDF files with python scripts instead of manually. What you need is to create a basic URDF file first and then automatically modifying it as you wish.
  - Extract intertial from a text file copied from solidworks and save to a json file.
  - Use a python file to flexibly load all configs to a CONFIG dict, which will be used by the convertion tool.
- **URDF to Xacro Conversion**: Convert `.urdf` files to a well organized `.xacro` format with ease.

## Getting Started

Follow these simple steps to start using the URDF to Xacro tools.

### 1. Renaming Your Package

ROS packages have specific naming conventions. Use the following command to rename your package:

```bash
python3 rename.py -path <path/of/your/package> -in <old_name> -out <new_name>
```

This command will replace the old package name in all folders, files, and file contents with the new name.

**Example:**
If your URDF package path is `~/ws/src/BAD--name`, run:

```bash
python3 rename.py -path ~/ws/src/BAD--name -in BAD--name -out new_name
```

### 2. Prepare configuration files

- **Create a configuration folder** that contains a python file(e.g. `urdf_config.py`) and ohtter config files.
- **Convert links_intertial.txt** that contains intertial information copied from solidworks to a json file:
  ```bash
  python3 extract_intertial.py -in example_config/links_inertial.txt -t 1e-5 -ln base_link link1
  ```
- **Modify the python file** to set the desired configurations, e.g. `joints_limit`, `links_intertial`, etc.

### 3. Converting URDF to Xacro

- Run the conversion script with the path to your URDF file:

```bash
python3 urdf_to_xacro.py -in <urdf_file_path> -cfg example_config/urdf_config.py -ml all
```

The conversion process includes:

- Replacing joints limit and links_intertial with values from `CONFIG` dict in `config.py`.
- Adding Xacro variables within the robot tag.
- Encapsulating the robot tag's content in a `xacro:macro` tag with a prefix parameter.
- Renaming all joints and links to incorporate the prefix, e.g., `${prefix}joint1`.
- Saving the modified file as a `.xacro` file with the same name.
- Formatting the Xacro file using `xmllint` for uniformity and readability.

## Custom Usage

For more ways to use, please refer to the source code.

## Contributing

Contributions are welcome!

## License

This project is licensed under the [MIT License](LICENSE).

---

Feel free to [open an issue](https://github.com/your_username/urdf_to_xacro/issues) for support, questions, or suggestions.
