#!/bin/bash

script_dir=$(dirname $0)
script_absolute=$(readlink -f $script_dir)
parent_absolute=$(readlink -f $script_dir/../)

if [ -n $1 ]
then
    echo "Using local registry path: $1"
    echo "publish agent and components to local registry..."
    cd $parent_absolute 
    aea publish --local --push-missing

    cd $script_absolute
    rm -rf $script_absolute/packages
    echo "Copy packages folder [$1] to build folder..."
    cp -r $1 $script_absolute
    echo "Starting docker container build..."
    docker build --network=host -t selling_agent -f Dockerfile .
    #docker build --build-arg http_proxy="http://172.17.0.1:3128" --build-arg https_proxy="http://172.17.0.1:3128" --build-arg no_proxy="bosch.com" --network=host -t selling_agent -f Dockerfile .
else
    echo "No local registry path given!"
fi
