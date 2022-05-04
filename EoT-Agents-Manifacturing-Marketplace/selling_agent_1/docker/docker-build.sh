#!/bin/bash
set -e

# setup the agent
aea fetch bosch/selling_agent_1:latest
cd selling_agent_1/
aea install
aea build