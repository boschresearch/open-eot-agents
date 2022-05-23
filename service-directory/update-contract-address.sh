#!/bin/bash

script_dir=$(dirname $0)
parent_absolute=$(readlink -f $script_dir/../)
echo 'Getting contract address from truffle network with id 1111...'
address=$(truffle networks | grep '1111' -A 2 | grep 'ServiceDirectory:' | grep -o '\b0x\w*')
echo "contract address is: $address"
echo "Dumping contract address for aea_manager..."
eval echo $address > ../EoT-Agents-Manifacturing-Marketplace/aea_manager/contract_address.txt