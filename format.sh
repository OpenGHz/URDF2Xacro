#!/bin/bash

path=$1
xmllint --format "$1" -o "$1"