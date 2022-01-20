#!/bin/bash

script_dir=$(dirname $0)
parent_absolute=$(readlink -f $script_dir/../)
echo 'Getting contract address from truffle network with id 1111...'
address=$(truffle networks | grep '1111' -A 2 | grep 'ServiceDirectory:' | grep -o '\b0x\w*')
echo "contract address is: $address"
command="sed -i \"s/^\(\s*contract_address\s*:\s*\).*/\1'$address'/\""
echo "Updating skill.yaml files with contract address..."
eval $command $parent_absolute/EoT-Agents-Manifacturing-Marketplace/purchasing_agent_1/skills/fipa_negotiation/skill.yaml
eval $command $parent_absolute/EoT-Agents-Manifacturing-Marketplace/purchasing_agent_2/skills/fipa_negotiation/skill.yaml
eval $command $parent_absolute/EoT-Agents-Manifacturing-Marketplace/selling_agent_1/skills/fipa_negotiation/skill.yaml
eval $command $parent_absolute/EoT-Agents-Manifacturing-Marketplace/selling_agent_2/skills/fipa_negotiation/skill.yaml