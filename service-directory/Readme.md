# Service Directory Smart Contracts

To develop the smart contracts, the [Truffle suite](https://www.trufflesuite.com/docs/truffle/overview) is used.

It is preconfigured to use a local running [Ganache](https://www.trufflesuite.com/docs/ganache/overview) on port 8545 on localhost.

## Prerequisities

1. Installation of ganache CLI as described [here](https://github.com/trufflesuite/ganache#command-line-use). Alternatevily installation of [Ganache](https://www.trufflesuite.com/docs/ganache/quickstart). CLI is the preferred way for the scripts.
2. Installation of [Truffle](https://www.trufflesuite.com/docs/truffle/getting-started/installation)

## Using ganache-cli with provided scripts

### Starting ganache

The provided script [start-ganache-aea.sh](start-ganache-aea.sh) starts a local ganache-cli instance with the following parameters:

- network id 1111, which will be used later to identify the network to retrieve the deployed contract address
- Running port of 8545
- Proper mnemonic configuration for the preconfigured accounts in the agents

This configuration is also reflected in the [truffle-config.js](truffle-config.js) file in the *development* network.

### Deploying contracts to ganache

Migrating/deploying to Ganache can be done using `truffle migrate`.

### Updating contract address in agents

As the agents needs to know the current address of the newly deployed [*ServiceDirectory*](contracts/ServiceDirectory.sol), this address needs to be updated in the corresponding *skill.yaml* files.

This can be done in an automated way by executing [update-contract-address.sh](update-contract-address.sh) along with the already running ganache-cli instance. It will fetch the address of the deployed [*ServiceDirectory*](contracts/ServiceDirectory.sol) contract at network id 1111 and dumps the address to a file for the aea_manager.

For a manual update, the corresponding *aea-config.yaml* file of the agents needs to be updated in the agents folder under *<agent_folder>/aea-config.yaml*.
There the property
```
public_id: bosch/fipa_negotiation_(purchasing|selling):<version>
type: skill
models:
  strategy:
    args:
      contract_address: <address>

```
needs to be updated.


## Using truffle

Common commands from [Quickstart](https://www.trufflesuite.com/docs/truffle/quickstart):

* Compiling solidity contracts using `truffle compile`.
* Migrating/deploying to Ganache using `truffle migrate`.
* Running provided tests with `truffle test`.

ABI for further usage can be found under build/contracts folder.