# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## [v0.1.0](https://github.com/oist/replifactory_v7/releases/tag/v0.1.0) - 2024-08-05

<small>[Compare with first commit](https://github.com/oist/replifactory_v7/compare/6c8e6958fcfcefe3043854997b550cfc5e69cb36...v0.1.0)</small>

### Features

- serve static with gunicorn ([8fa2905](https://github.com/oist/replifactory_v7/commit/8fa29057db182e5a06ea9988271556b2b1000a52) by Fedor Gagarin).
- run local with gunicorn fix: npm warnings ([a0d49ee](https://github.com/oist/replifactory_v7/commit/a0d49ee1f9c9cf1146c758abd38ed75016d30c39) by Fedor Gagarin).
- add echarts to experiment dashboard ([498e773](https://github.com/oist/replifactory_v7/commit/498e7734412d82a9fa41210f99e8fca4a84c1dbd) by Fedor Gagarin).
- display experiment details on detail page ([be4d100](https://github.com/oist/replifactory_v7/commit/be4d10081d74b6c98ae9554e5f893a7227f3237c) by Fedor Gagarin).
- integrate sphinx documentation to vue 3 app ([c8ff84c](https://github.com/oist/replifactory_v7/commit/c8ff84cc31f6a70b7c4e04774ff2617ce9b7c238) by Fedor Gagarin).
- create experiment detail page ([a5daae3](https://github.com/oist/replifactory_v7/commit/a5daae3bdcd5dcabc2ba23f04dbfb5d4f1a0dfd8) by Fedor Gagarin).
- add buttons for small screen view ([1312068](https://github.com/oist/replifactory_v7/commit/1312068286e8065215048c75ba2457769871cbca) by Fedor Gagarin).
- add modal before stop experiment ([3e0927f](https://github.com/oist/replifactory_v7/commit/3e0927fe08b3cdde30ce029647ef957d77c957d3) by Fedor Gagarin).
- run multiple experiments with the same class ([7e10393](https://github.com/oist/replifactory_v7/commit/7e10393ed89ba0592e9bf5a64901d07d6ba2cc74) by Fedor Gagarin).
- get experiment parameters from plugin component and send to start experiment ([1aae195](https://github.com/oist/replifactory_v7/commit/1aae195737a964693c0ae69ab73b5b124131f7fd) by Fedor Gagarin).
- add virtual usb device ([b6cc44e](https://github.com/oist/replifactory_v7/commit/b6cc44ef08acf3a579b5f184188bd2ea56fe653b) by Fedor Gagarin).
- implement experiments plugins ([b159949](https://github.com/oist/replifactory_v7/commit/b159949771c2f58d3e4774cffbc15d0752619a0a) by Fedor Gagarin).
- add experiments plugins autodiscovery ([963c575](https://github.com/oist/replifactory_v7/commit/963c57530268ffc40b02c49a168cf8dde355c99e) by Fedor Gagarin).
- add running experiments on home page ([c0549e1](https://github.com/oist/replifactory_v7/commit/c0549e1e734fbcbce6841e334d29aa05ef0a3891) by Fedor Gagarin).
- new application layout ([02d20ff](https://github.com/oist/replifactory_v7/commit/02d20ff8cc6f84f0a542ae2f30430c2665635acc) by Fedor Gagarin).
- add logging to machine and devices ([63cedaa](https://github.com/oist/replifactory_v7/commit/63cedaa0c853a8bdd6999d97a3d7f644331cd161) by Fedor Gagarin).
- start/stop experiment ([5c04840](https://github.com/oist/replifactory_v7/commit/5c048401c2dd17ac4449d4706ce44f73a7efb362) by Fedor Gagarin).
- new devices for new pcb ([bdf02cc](https://github.com/oist/replifactory_v7/commit/bdf02ccbc67cded1c515d82094a870526c4fdbf8) by Fedor Gagarin).
- add authentication form ([ddb25f6](https://github.com/oist/replifactory_v7/commit/ddb25f68f0e42617aeeb71c8dc5ec673268b19f7) by Fedor Gagarin).
- login form. move to vite. ([da5a8b8](https://github.com/oist/replifactory_v7/commit/da5a8b8cb54608b4b3cc892b3f6eff48e5604574) by Fedor Gagarin).
- add motor profile control ([1f3e870](https://github.com/oist/replifactory_v7/commit/1f3e870d3289627beb6ffac3e69eec44cf018189) by Fedor Gagarin).
- thermometer control ([583923f](https://github.com/oist/replifactory_v7/commit/583923f059d68c0466505397cbb0936a83f8905e) by Fedor Gagarin).
- display queue size in ui ([89a2485](https://github.com/oist/replifactory_v7/commit/89a2485485ce44f5783b868672bb0f17f0b9c106) by Fedor Gagarin).
- abort button ([3ef3128](https://github.com/oist/replifactory_v7/commit/3ef31286d14e0526c5de5fcfd2f885445a797594) by Fedor Gagarin).
- pump default speed 3rps. ui debug switch ([d35956d](https://github.com/oist/replifactory_v7/commit/d35956d8f225b114d2ab89dac2f5f9f0f04b7ecc) by Fedor Gagarin).
- pump control and vial control ([c9d88f7](https://github.com/oist/replifactory_v7/commit/c9d88f719dc9226da1a212dfa11570afcdcc2eb4) by Fedor Gagarin).
- send od values to ui ([af43b6f](https://github.com/oist/replifactory_v7/commit/af43b6f91436d00553b968ca0a4eef6d048c1527) by Fedor Gagarin).
- control stirrer. toast notifications. ([b13d973](https://github.com/oist/replifactory_v7/commit/b13d9738efc27b9e9e166b18b18ee1cae2ae3e7f) by Fedor Gagarin).
- reconnecting machine with the same serial number ([3c52e9a](https://github.com/oist/replifactory_v7/commit/3c52e9a8f403f167ec393e3772800a5010aa4eed) by Fedor Gagarin).
- script for writing serial number using make ([70dcd10](https://github.com/oist/replifactory_v7/commit/70dcd10adbd4268e78806eba2fb4623582b20654) by Fedor Gagarin).
- run with unicorn ([84fec37](https://github.com/oist/replifactory_v7/commit/84fec375302744e84aca1bbd2509c7e08e1a6e5c) by Fedor Gagarin).
- connect to replifactory with serial number ([c7c4102](https://github.com/oist/replifactory_v7/commit/c7c4102c135301eb6c138bb5bc056310149739fd) by Fedor Gagarin).
- device configuration data for initialization ([6b3b80b](https://github.com/oist/replifactory_v7/commit/6b3b80bd6b59fe055705e27174e509fdd37a216f) by Fedor Gagarin).
- util to write ftdi config to replifactory eeprom ([c72aa72](https://github.com/oist/replifactory_v7/commit/c72aa72ad0b1f6b86e4d7379274ddea2efb84e88) by Fedor Gagarin).

### Bug Fixes

- serve ui app from flask ([e09717b](https://github.com/oist/replifactory_v7/commit/e09717b7b5de885a4b2fd1834662c00fa499a410) by Fedor Gagarin).
- duplicate experiments after visiting experiment detail page ([8e48882](https://github.com/oist/replifactory_v7/commit/8e488820effce97dfe0aabde83e7ac8029f32223) by Fedor Gagarin).
- fast interrupting of experiment ([8f4333b](https://github.com/oist/replifactory_v7/commit/8f4333b54dd5db661656902fc5a50984b5a3f69c) by Fedor Gagarin).
- device tab is always selected ([d12b727](https://github.com/oist/replifactory_v7/commit/d12b72730811271e42c05db2a59011074ccf03c0) by Fedor Gagarin).
- icons not found warning ([a1de261](https://github.com/oist/replifactory_v7/commit/a1de261441eabd6193497fa4997a328fa05f554d) by Fedor Gagarin).
- csrf token validation ([1aacb7f](https://github.com/oist/replifactory_v7/commit/1aacb7fbb97baadaaab410eca1e5851cbf448b6b) by Fedor Gagarin).
- run scripts ([59f5409](https://github.com/oist/replifactory_v7/commit/59f5409af64d886a453d84d5ab00cf4f174ad64d) by Fedor Gagarin).
- build flask app docker image on Raspberry PI4 ([86dc62b](https://github.com/oist/replifactory_v7/commit/86dc62b517fb62fe83252d8fa81c4866ab51c5ab) by Fedor Gagarin).
- build vue app docker image ([366eaaa](https://github.com/oist/replifactory_v7/commit/366eaaa16d654d99151985f3bd9d1bf29eddf0bb) by Fedor Gagarin).

### Code Refactoring

- migrate backend to src/ layout ([3342b9d](https://github.com/oist/replifactory_v7/commit/3342b9ddd48de22cbe183e7bfc56a4638e64e20d) by Fedor Gagarin).
- apply prettier format ([9e01bb4](https://github.com/oist/replifactory_v7/commit/9e01bb45d04316585132c8b48dba42b049f8bd15) by Fedor Gagarin).

### Continuous Integration

- single docker image ([5083978](https://github.com/oist/replifactory_v7/commit/5083978d2d283aad9c0821714f9b086c30ff076e) by Fedor Gagarin).

