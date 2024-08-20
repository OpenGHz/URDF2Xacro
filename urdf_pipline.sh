#!/bin/bash

# Usage: ./urdf_pipline.sh

mkdir -p ./temp_urdf  # create temp folder to copy urdf files

set -e

# custom variables
export urdf2xacro="/home/ghz/Work/OpenGHz/URDF2Xacro"
export OLD_NAME="inspire_eg2_4cx"
export NAME="inspire_eg2_4cx"
export CONFIGS_DIR=${urdf2xacro}
export type="gripper"
export REPO_DIR="/home/ghz/Work/airbot_play/arm-models"

# automatically generated variables
export TARGET_DIR="package://airbot_description/meshes/${NAME}"
export target_meshes_dir=${REPO_DIR}/meshes/${NAME}

# copy raw urdf files to temp folder
cp -r ${OLD_NAME} ./temp_urdf/ && cd ./temp_urdf

# create urdf folder and move all urdf files into it
mkdir -p ${OLD_NAME}/urdf
mv ${OLD_NAME}/*.urdf ${OLD_NAME}/urdf/

# rename base_link and name of&in urdf files
python3 ${urdf2xacro}/rename.py -path ${OLD_NAME} -in World_${OLD_NAME}_${OLD_NAME} -out base_link
python3 ${urdf2xacro}/rename.py -path ${OLD_NAME} -in name=\"${OLD_NAME}\" -out name=\"${NAME}\"
if [ $OLD_NAME != $NAME ]; then
    rm -rf ${NAME} && mv ${OLD_NAME} ${NAME}
    mv ${NAME}/urdf/${OLD_NAME}.urdf ${NAME}/urdf/${NAME}.urdf
fi

# split mesh paths into visual and collision
mv ${NAME}/meshes ${NAME}/visual
mkdir -p ${NAME}/meshes
mv ${NAME}/visual ${NAME}/meshes/
cp -r ${NAME}/meshes/visual ${NAME}/meshes/collision
# TODO: the path is used in TARGET_DIR, not current urdf package
python3 ${urdf2xacro}/split_mesh_paths.py -path ${NAME}/urdf/${NAME}.urdf -ov "meshes" -oc "meshes" -nv "${TARGET_DIR}/visual" -nc "${TARGET_DIR}/collision" -cc

# convert urdf to xacro
python3 ${urdf2xacro}/urdf_to_xacro.py -ml all -in ${NAME}/urdf/${NAME}.urdf -cfg ${CONFIGS_DIR}/urdf_config_${NAME}/urdf_config.py

# simplify meshes
python3 ${urdf2xacro}/mesh_tools/simplify_meshes_meshlab.py -pre "" -in ${NAME}/meshes/collision -fmt obj

# merge_into_repo
mkdir -p ${target_meshes_dir}/collision
mkdir -p ${target_meshes_dir}/visual
mv ${NAME}/meshes/collision/* ${target_meshes_dir}/collision/
mv ${NAME}/meshes/visual/* ${target_meshes_dir}/visual/

# move all the xacro files into the target urdf directory
cp ${NAME}/urdf/*.xacro ${REPO_DIR}/urdf/${type}s/

echo "Merged $NAME into $REPO_DIR"
