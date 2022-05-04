#!/bin/bash
set -e

# setup the agent
aea fetch bosch/purchasing_agent_1:latest
cd purchasing_agent_1/
aea install
aea build