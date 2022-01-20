# EoT Agents Manufacturing Marketplace

## Prerequisites

- Setup of smart contracts and testnet as described [here](../service-directory/Readme.md).
- [Fetchai](https://fetch.ai/) AEA version 1.1.1

## Run it out of the box

There are currently 4 agents included, two *selling_agents* and two *purchasing_agents*. These agents are already preconfigured and can be run out of the box after the testnet and smart contracts are setup as desribed in prerequisities.

To run these agents the following steps has to be performed first in the *selling_agents* and then in the *purchasing agents*:

````console
  aea -s issue-certificates
  aea -s build
  aea -s run
````

## Configure the AEAs

The following sections are describing what needs to be done using a custom configuration.

- copy the ServiceDirectory contract address (0X..) from ganache into selling and purchasing AEAs' skill.yaml files under property if not using the automated setup as described [here](../service-directory/Readme.md)

    ```console
    - contract_address: '0x..'```

- generate the private key for fetchai p2p connection

    ```console
    foo@bar:~$ aea generate-key fetchai fetchai_private_key.txt
    ```

  - if not already included, copy the key file name fetchai_private_key.txt into aea-config.yaml file under property

    ```console
    - connection_private_key_paths:
    - fetchai: fetchai_private_key.txt```

- setup the private key for ethereum ledger connection
  - copy ethereum account private key from ganache into file ethereum_private_key.txt
    - if not already included, copy the key file name ethereum_private_key.txt into aea-config.yaml file under property

    ```console
        - private_key_paths:
            - ethereum: ethereum_private_key.txt```

- to be able to run multiple AEAs,
  - put different port numbers for each AEA within aea-config.yaml under properties

    ```console
    - delegate_uri: 127.0.0.1:11000
    - local_uri: 127.0.0.1:9000
    - public_uri: 127.0.0.1:9000```

  - after running the different AEAs (see next section), put the entry peers *dns4* multiaddr to connect to within aea-config.yaml under property

    ```console
    - entry_peers: []```

## Run the AEAs

- update certificates for the p2p and ledger connection for each AEA

```console
    aea -s issue-certificates
```

- build the AEAs

```console
    aea -s build
```

- start selling AEAs

```console
    aea -s run
```

- copy its multiaddr as mentioned in the previous section into purchasing AEAs entry peers
- start purchasing AEAs

```console
    aea -s run
```

## Open issues / bugs to be fixed in a later version

- as the contract function removeServices() cannot be executed in the current version, it is possible to observe the following problem(s)
  - the number of offered services and their endpoints is increasing within contract each time the selling AEAs are (re)-started
  - multiple registration of same AEA endpoints for a service which leads to a CFP send multiple times to the same AEA endpoint
