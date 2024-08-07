# URDF to XACRO Converter

**Tools for modifying URDF packages and converting `URDF` into well organized `XACRO`.**

## Overview

This set of tools helps you modify your URDF ROS package and streamlines the process of converting URDF files into XACRO format, making your robot modeling workflow more efficient.

## Features

- **Package Renaming**: Rename all folders, files and contents in your URDF ROS package.
- **URDF to XACRO Conversion**: Convert `.urdf` files to `.xacro` format with ease.

## Getting Started

Follow these simple steps to start using the URDF to XACRO tools.

### 1. Renaming Your Package

ROS packages have specific naming conventions. Use the following command to rename your package:

```bash
python3 rename.py -rd <directory/of/your/package> -in <old_name> -out <new_name>
```

This command will replace the old package name in all folders, files, and file contents with the new name.

**Example:**
If your URDF package path is `~/ws/src/bad--name`, run:

```bash
python3 rename.py -rd ~/ws/src -in BAD--name -out new_name
```

### 2. Converting URDF to XACRO

To convert your URDF file to XACRO, follow these steps:

- **Modify the `config.py` file** to set the desired joint limits and other configurations.
- Run the conversion script with the path to your URDF file:

```bash
python3 urdf_to_xacro.py -in <urdf_file_path>
```

The conversion process includes:

- Replacing joint limits with values from `config.py`.
- Adding XACRO variables within the robot tag.
- Encapsulating the robot tag's content in a `xacro:macro` tag with a prefix parameter.
- Renaming all joints and links to incorporate the prefix, e.g., `${prefix}_joint1`.
- Saving the modified file as a `.urdf.xacro` file with the same name.
- Formatting the XACRO file using `xmllint` for readability.

## Custom Usage

For more ways to use, please refer to the source code.

## Contributing

Contributions are welcome!

## License

This project is licensed under the [MIT License](LICENSE).

---

Feel free to [open an issue](https://github.com/your_username/urdf_to_xacro/issues) for support, questions, or suggestions.
