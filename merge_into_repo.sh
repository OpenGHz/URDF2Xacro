#!/bin/bash

# input obsolute paths to the raw directory and the output directory
raw_dir=$1
out_dir=$2
# get the package name from the raw directory
package_name=$(basename $raw_dir)

echo "Merging $package_name into $out_dir"

# Merge all the files in the raw directory into out_dir
#TODO: Seperate raw meshes into visual and collision
cp ${raw_dir}/meshes ${out_dir}/meshes/${package_name}/collision
cp ${raw_dir}/meshes ${out_dir}/meshes/${package_name}/visual



# cp ${raw_dir}/urdf/*.urdf ${out_dir}/urdf/robots/