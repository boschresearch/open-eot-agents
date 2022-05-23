# EoT Agents Manufacturing Marketplace

## Prerequisites

- Setup of smart contracts and testnet as described [here](../service-directory/Readme.md).
- Installation of [Fetchai](https://fetch.ai/) AEA version 1.1.0 and the needed [Ethereum ledger plugin](https://pypi.org/project/aea-ledger-ethereum/). This can be done either manually or with the provided pipenv environment ([Pipfile](Pipfile)). Using [pipenv](https://github.com/pypa/pipenv) execute `pipenv install` in this folder, where the corresponding [Pipfile](Pipfile) is located.
- Setup of local packages registry for development: fetch describes 2 approaches in the [docu](https://docs.fetch.ai/aea/development-setup/). To enable a local registry to be used in different agent implementations, a [.env](.env) file is provided which points the packages folder inside the user home .aea folder(*~/.aea/packages*). To use this folder, it needs to be created and in addition added to the global aea cli config, which is located under *~/.aea/cli_config.yaml*. There the key `registry_path: /home/<user>/.aea/packages/` has to be added.

## Run it out of the box

To run a predefined scenario with selling agents and purchasing agents in one environment, the provided [aea_manager](aea_manager) can be used. This contains an automated way to start and configure AEA and connect them to the ganache node as well as to each other.

After setting up the environment as described in [Prerequisites](#prerequisites), the marketplace scenario can be started in the [aea_manager](aea_manager) folder using the following command:

````console
  ./setup-and-run.sh <full path to local aea registry>
````

## Configure the AEAs

The following sections are describing what needs to be done using a custom configuration.

- copy the ServiceDirectory contract address (0X..) from ganache into selling and purchasing AEAs' aea-config.yaml files under property if not using the automated setup as described [here](../service-directory/Readme.md)

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
