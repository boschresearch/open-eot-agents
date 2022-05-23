#!/bin/bash

script_dir=$(dirname $0)
script_absolute=$(readlink -f $script_dir)
parent_absolute=$(readlink -f $script_dir/../)

if [ -n $1 ]
then
    echo "Using local registry path: $1"
    echo "Publish purchasing agent to local registry..."
    cd $parent_absolute/purchasing_agent
    aea publish --local --push-missing

    echo "Publish selling agent to local registry..."
    cd $parent_absolute/selling_agent
    aea publish --local --push-missing

    echo "Starting scenario..."
    cd $script_absolute
    python scenario.py $1
else
    echo "No local registry path given!"
fi