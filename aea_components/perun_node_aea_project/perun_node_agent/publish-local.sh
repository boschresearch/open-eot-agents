#!/bin/bash

script_dir=$(dirname $0)
script_absolute=$(readlink -f $script_dir)
parent_absolute=$(readlink -f $script_dir/../)

echo "Publish perun agent components to local registry..."
cd $script_absolute
aea publish --local --push-missing
