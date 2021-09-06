// Copyright (c) 2021 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
//
// SPDX-License-Identifier: Apache-2.0

const ServiceDirectoryContract = artifacts.require('ServiceDirectory');
 
module.exports = function(deployer) {
  // Use deployer to state migration tasks.
  deployer.deploy(ServiceDirectoryContract);
};