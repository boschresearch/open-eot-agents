// Copyright (c) 2021 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
//
// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.4;

contract ServiceDirectory {
    struct Service {
        address owner;
        string endpoint;
    }

    mapping(string => Service[]) public topicMappings;

    event ServiceAdded(address owner, string topic, string endpoint);
    event ServiceDeleted(address owner, string topic, string[] endpoint);

    constructor() {}

    function addService(string calldata topic, string calldata endpoint)
        public
    {
        topicMappings[topic].push(Service(msg.sender, endpoint));
        emit ServiceAdded(msg.sender, topic, endpoint);
    }

    function addServices(string[] calldata topics, string calldata endpoint)
        public
    {
        for (uint256 index = 0; index < topics.length; index++) {
           addService(topics[index], endpoint); 
        }
    } 

    function getServiceEndpoints(string calldata topic)
        public
        view
        returns (string[] memory)
    {
        Service[] storage services = topicMappings[topic];
        string[] memory endpoints = new string[](services.length);
        if (topicMappings[topic].length > 0) {
            for (uint256 ii = 0; ii < services.length; ii++) {
                endpoints[ii] = services[ii].endpoint;
            }
        }
        return endpoints;
    }

    function getServiceEndpointsTopics(string[] calldata topicList)
        public
        view
        returns (string[][] memory)
    {
        string[][] memory endpoints = new string[][](topicList.length);
        for (uint256 index = 0; index < topicList.length; index++) {
            endpoints[index] = getServiceEndpoints(topicList[index]);
        }
        return endpoints;
    }

    function removeService(string calldata topic) public {
        Service[] storage services = topicMappings[topic];
        string[] memory endpoints = new string[](services.length);
        for (uint256 ii = 0; ii < services.length; ii++) {
            if (services[ii].owner == msg.sender) {
                endpoints[ii] = services[ii].endpoint;
                removeServiceFromArray(services, ii);
                if (services.length > 0 && ii == services.length-1 && services[ii].owner == msg.sender) {
                    endpoints[ii] = services[ii].endpoint;
                    removeServiceFromArray(services, ii);
                }
            }
        }
        emit ServiceDeleted(msg.sender, topic, endpoints);
    }

    function removeServices(string[] calldata topics) public {
        for (uint256 index = 0; index < topics.length; index++) {
            removeService(topics[index]);
        }
    }

    function removeServiceFromArray(Service[] storage services, uint256 index)
        private
    {
        //setting last element to given index
        services[index] = services[services.length - 1];
        //removing last element
        services.pop();
    }
}
