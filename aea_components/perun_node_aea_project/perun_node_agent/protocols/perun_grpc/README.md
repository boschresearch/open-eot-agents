# Perun protocol

## Perun GRPC messages

The grpc client code is generated using [betterproto](https://github.com/danielgtaylor/python-betterproto) from the following file coming from the perun node: [api specification](https://github.com/hyperledger-labs/perun-node/blob/07467fadaeffc4b1b6819182a5772b9a09bc74d0/api/grpc/pb/api.proto).

## AEA protocol specification

```yaml
---
name: perun_grpc
author: bosch
version: 0.1.0
description: A protocol for Perun GRPC requests and responses.
license: Apache-2.0
aea_version: '>=1.0.0, <2.0.0'
protocol_specification_id: bosch/perun_grpc:0.1.0
speech_acts:
  request:
    type: pt:str
    content: pt:bytes
  response:
    type: pt:str
    content: pt:bytes
  paychresp:
    session_id: pt:str
    type: pt:str
    content: pt:bytes
  accept: {}
  reject: {}
  end: {}
...
---
initiation: [request, paychresp]
reply:
  request: [response]
  response: []
  paychresp: [paychresp, accept, reject, end]
  accept: [paychresp, end]
  reject: [paychresp, end]
  end: []
termination: [response, end]
roles: {client, server}
end_states: [successful]
keep_terminal_state_dialogues: false
...
```