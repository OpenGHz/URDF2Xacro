#!/bin/bash

set -e

# input obsolute paths to the raw directory and the output directory
raw_path=$1
out_path=$2
type=$3
# get the package name from the raw directory
package_name=$(basename $raw_path)

# Merge all the files in the raw directory into out_path
#TODO: Seperate raw meshes into visual and collision
raw_visual_meshes_dir=${raw_path}/meshes
raw_collision_meshes_dir=${raw_path}/meshes

target_meshes_dir=${out_path}/meshes/${package_name}
mkdir -p ${target_meshes_dir}/collision
mkdir -p ${target_meshes_dir}/visual

cp ${raw_collision_meshes_dir}/* ${target_meshes_dir}/collision
cp ${raw_collision_meshes_dir}/* ${target_meshes_dir}/visual

# move all the xacro files into the target urdf directory
cp ${raw_path}/urdf/*.xacro ${out_path}/urdf/${type}s/

echo "Merged $package_name into $out_path"