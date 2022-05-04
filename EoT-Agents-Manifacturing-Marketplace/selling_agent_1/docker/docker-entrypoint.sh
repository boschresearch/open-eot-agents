#!/bin/bash
set -e

aea --version

cd selling_agent_1

# create private key files
echo ${AGENT_PRIV_KEY} > fetchai_private_key.txt
echo ${CONNECTION_PRIV_KEY} > connection_fetchai_private_key.txt
echo ${ETH_PRIV_KEY} > ethereum_private_key.txt

# add keys
aea add-key fetchai fetchai_private_key.txt
aea add-key fetchai connection_fetchai_private_key.txt --connection
aea add-key ethereum ethereum_private_key.txt

# issue certs
aea issue-certificates

# run
aea run