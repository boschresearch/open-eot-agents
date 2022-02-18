# Open EoT Agents

Includes implementation for a decentralized manufacturing marketplace, follwoing the concept described under [iBlockchain’s Open IoT Marketplace: Order-Controlled Production](https://industrial-blockchain.medium.com/iblockchains-open-iot-marketplace-order-controlled-production-4c09483b3acc).

Agent based implementation can be found under [EoT Agents Manufacturing Marketplace](EoT-Agents-Manifacturing-Marketplace/).

## License

Open-EoT-Agents is open-sourced under the Apache-2.0 license. See the
[LICENSE](LICENSES/Apache-2.0.txt) file for details.

## Developing cross-agent-components
### Prerequisites
* Python 3.8 or later
* pipenv installed (`pip install --user pipenv`)
### Initialise a cli component
To develop cross agent components, e.g. protocols or connections, you can use the provided [cli.py](cli.py) with `cli <component-name>` to scaffold 
an aea project at `./aea_components/<component-name>_aea_project` with an aea `<component-name>_agent`.
See the output for further steps. 

In addition check [Prerequisities](EoT-Agents-Manifacturing-Marketplace/README.md#prerequisites) for needed setup of environment, especially the section for the local registry.