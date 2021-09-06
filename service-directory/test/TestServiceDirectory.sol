// Copyright (c) 2021 - for information on the respective copyright owner see the NOTICE file and/or the repository https://github.com/boschresearch/open-eot-agents.
//
// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.2;

import "truffle/Assert.sol";
import "truffle/DeployedAddresses.sol";
import "../contracts/ServiceDirectory.sol";

contract TestServiceDirectory {
    function testAddService() public {
        ServiceDirectory servDir = new ServiceDirectory();
        // initial test for not existent topic
        string memory topic = "testtopic1";
        string memory endpoint = "myendpoint1";
        string[] memory result = servDir.getServiceEndpoints(topic);
        Assert.equal(result.length, 0, "should be empty");
        // adding new endpoint to topic
        servDir.addService(topic, endpoint);
        //checking new endpoint
        result = servDir.getServiceEndpoints(topic);
        Assert.equal(result.length, 1, "1 entry should be existent");
        Assert.equal(result[0], endpoint, "endpoint value is wrong");
    }

    function testAddService2() public {
        ServiceDirectory servDir = new ServiceDirectory();
        // initial test for not existent topic
        string memory topic = "testtopic1";
        string memory endpoint = "myendpoint1";
        string[] memory result = servDir.getServiceEndpoints(topic);
        Assert.equal(result.length, 0, "should be empty");
        // adding new endpoint to topic
        servDir.addService(topic, endpoint);
        servDir.addService(topic, endpoint);
        //checking new endpoint
        result = servDir.getServiceEndpoints(topic);
        Assert.equal(result.length, 2, "2 entry should be existent");
        Assert.equal(result[0], endpoint, "endpoint value is wrong");
        Assert.equal(result[1], endpoint, "endpoint value is wrong");
    }

    function testAddServices() public {
        ServiceDirectory servDir = new ServiceDirectory();
        // initial test for not existent topic
        string[] memory topic = new string[](1);
        topic[0] = "testtopic1";
        string memory endpoint = "myendpoint1";
        string[] memory result = servDir.getServiceEndpoints(topic[0]);
        Assert.equal(result.length, 0, "should be empty");
        // adding new endpoint to topic
        servDir.addServices(topic, endpoint);
        //checking new endpoint
        result = servDir.getServiceEndpoints(topic[0]);
        Assert.equal(result.length, 1, "1 entry should be existent");
        Assert.equal(result[0], endpoint, "endpoint value is wrong");
    }

    function testAddServices2() public {
        ServiceDirectory servDir = new ServiceDirectory();
        // initial test for not existent topic
        string[] memory topic = new string[](1);
        topic[0] = "testtopic1";
        string memory endpoint = "myendpoint1";
        string[] memory result = servDir.getServiceEndpoints(topic[0]);
        Assert.equal(result.length, 0, "should be empty");
        // adding new endpoint to topic
        servDir.addServices(topic, endpoint);
        servDir.addServices(topic, endpoint);
        //checking new endpoint
        result = servDir.getServiceEndpoints(topic[0]);
        Assert.equal(result.length, 2, "2 entry should be existent");
        Assert.equal(result[0], endpoint, "endpoint value is wrong");
        Assert.equal(result[1], endpoint, "endpoint value is wrong");
    }

    function testRemoveService() public {
        ServiceDirectory servDir = new ServiceDirectory();
        //initial test for not existent topic
        string memory topic = "testtopic1";
        string memory endpoint = "myendpoint1";
        string[] memory result = servDir.getServiceEndpoints(topic);
        Assert.equal(result.length, 0, "should be empty");
        //adding endpoint
        servDir.addService(topic, endpoint);
        //checking new endpoint
        result = servDir.getServiceEndpoints(topic);
        Assert.equal(result.length, 1, "1 entry should be existent");
        Assert.equal(result[0], endpoint, "added endpoint value is wrong");
        //removing endpoint
        servDir.removeService(topic);
        //checking removal of endpoint
        result = servDir.getServiceEndpoints(topic);
        Assert.equal(result.length, 0, "0 entry should be existent");
    }

    function testRemoveService2() public {
        ServiceDirectory servDir = new ServiceDirectory();
        //initial test for not existent topic
        string memory topic = "testtopic1";
        string memory endpoint = "myendpoint1";
        string memory endpoint2 = "myendpoint2";
        string[] memory result = servDir.getServiceEndpoints(topic);
        Assert.equal(result.length, 0, "should be empty");
        //adding endpoint
        servDir.addService(topic, endpoint);
        servDir.addService(topic, endpoint2);
        //checking new endpoint
        result = servDir.getServiceEndpoints(topic);
        Assert.equal(result.length, 2, "2 entry should be existent");
        Assert.equal(result[0], endpoint, "added endpoint value is wrong");
        Assert.equal(result[1], endpoint2, "added endpoint value is wrong");
        //removing endpoint
        servDir.removeService(topic);
        //checking removal of endpoint
        result = servDir.getServiceEndpoints(topic);
        Assert.equal(result.length, 0, "0 entry should be existent");
    }

    function testRemoveServices() public {
        ServiceDirectory servDir = new ServiceDirectory();
        //initial test for not existent topic
        string[] memory topic = new string[](1);
        topic[0] = "testtopic1";
        string memory endpoint = "myendpoint1";
        string[] memory result = servDir.getServiceEndpoints(topic[0]);
        Assert.equal(result.length, 0, "should be empty");
        //adding endpoint
        servDir.addService(topic[0], endpoint);
        //checking new endpoint
        result = servDir.getServiceEndpoints(topic[0]);
        Assert.equal(result.length, 1, "1 entry should be existent");
        Assert.equal(result[0], endpoint, "added endpoint value is wrong");
        //removing endpoint
        servDir.removeServices(topic);
        //checking removal of endpoint
        result = servDir.getServiceEndpoints(topic[0]);
        Assert.equal(result.length, 0, "0 entry should be existent");
    }

    function testRemoveServices2() public {
        ServiceDirectory servDir = new ServiceDirectory();
        //initial test for not existent topic
        string[] memory topic = new string[](1);
        topic[0] = "testtopic1";
        string memory endpoint = "myendpoint1";
        string memory endpoint2 = "myendpoint2";
        string[] memory result = servDir.getServiceEndpoints(topic[0]);
        Assert.equal(result.length, 0, "should be empty");
        //adding endpoint
        servDir.addService(topic[0], endpoint);
        servDir.addService(topic[0], endpoint2);
        //checking new endpoint
        result = servDir.getServiceEndpoints(topic[0]);
        Assert.equal(result.length, 2, "2 entry should be existent");
        Assert.equal(result[0], endpoint, "added endpoint value is wrong");
        Assert.equal(result[1], endpoint2, "added endpoint value is wrong");
        //removing endpoint
        servDir.removeServices(topic);
        //checking removal of endpoint
        result = servDir.getServiceEndpoints(topic[0]);
        Assert.equal(result.length, 0, "0 entry should be existent");
    }

    //wor in progress
    function testGetServiceEndpointsTopics() public {
        ServiceDirectory servDir = new ServiceDirectory();
        //initial test for not existent topic
        string[] memory topic = new string[](2);
        topic[0] = "testtopic1";
        topic[1] = "testtopic2";
        string memory endpoint = "myendpoint1";
        // string[] memory result = servDir.getServiceEndpoints(topic[0]);
        // Assert.equal(result.length, 0, "should be empty");
        // result = servDir.getServiceEndpoints(topic[1]);
        // Assert.equal(result.length, 0, "should be empty");
        //adding endpoint
        servDir.addServices(topic, endpoint);
        //checking new endpoint
        string[][] memory results = servDir.getServiceEndpointsTopics(topic);
        Assert.equal(results.length, 2, "2 entry should be existent");
        Assert.equal(results[0][0], endpoint, "added endpoint value is wrong");
        Assert.equal(results[1][0], endpoint, "added endpoint value is wrong");
        
        string memory endpoint2 = "myendpoint2";
        string[] memory topic2 = new string[](3);
        topic2[0] = "testtopic2";
        topic2[1] = "testtopic3";
        topic2[2] = "testtopic4";
        servDir.addServices(topic2, endpoint2);
        //string[] memory topicCheck = new string[](2);
        string memory topicTest1 = "testtopic1";
        string memory topicTest2 = "testtopic2";
        string[] memory results2 = servDir.getServiceEndpoints(topicTest1);
        Assert.equal(results2.length, 1, "1 entry should be existent");
        Assert.equal(results2[0], endpoint, "added endpoint value is wrong");
        results2 = servDir.getServiceEndpoints(topicTest2);
        Assert.equal(results2.length, 2, "2 entry should be existent");
        Assert.equal(results2[0], endpoint, "added endpoint value is wrong");
        Assert.equal(results2[1], endpoint2, "added 2 endpoint value is wrong");
    }

    //not working at moment
    // function testGetServiceEndpointsTopics2() public {
    //     ServiceDirectory servDir = new ServiceDirectory();
    //     //initial test for not existent topic
    //     string[] memory topic = new string[](3);
    //     topic[0] = "testtopic1";
    //     topic[1] = "testtopic2";
    //     topic[2] = "testtopic3";

    //     string[] memory topic2 = new string[](3);
    //     topic2[0] = "testtopic2";
    //     topic2[1] = "testtopic3";
    //     topic2[2] = "testtopic4";

    //     string memory endpoint = "myendpoint1";
    //     string memory endpoint2 = "myendpoint2";
    //     // string[] memory result = servDir.getServiceEndpoints(topic[0]);
    //     // Assert.equal(result.length, 0, "should be empty");
    //     // result = servDir.getServiceEndpoints(topic[1]);
    //     // Assert.equal(result.length, 0, "should be empty");
    //     // result = servDir.getServiceEndpoints(topic[2]);
    //     // Assert.equal(result.length, 0, "should be empty");
    //     // result = servDir.getServiceEndpoints(topic2[2]);
    //     // Assert.equal(result.length, 0, "should be empty");
    //     //adding endpoint
    //     servDir.addServices(topic, endpoint);
    //     //servDir.addServices(topic2, endpoint2);
    //     //checking new endpoint
    //     string[] memory topicCheck = new string[](2);
    //     topic2[0] = "testtopic1";
    //     topic2[1] = "testtopic3";
    //     string[][] memory results = servDir.getServiceEndpointsTopics(topicCheck);
    //     Assert.equal(results.length, 2, "2 entry should be existent");
    //     Assert.equal(results[0][0], endpoint, "added endpoint value is wrong");
    //     // Assert.equal(results[1][0], endpoint, "added endpoint value is wrong");
    //     // Assert.equal(results[1][1], endpoint2, "added endpoint value is wrong");
    // }
}
