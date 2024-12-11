# Changelog

## [synthdb-v2.3.4](https://bbpgitlab.epfl.ch/neuromath/synthdb/compare/synthdb-v0.1.0...synthdb-v2.3.4)

> 25 July 2023

### New Features

- Hippocampus settings (Alexis Arnaudon - [36811fd](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/36811fd733085696776c0d8183e470bff98fd9b5))
- Add CA1 synthesis data (Alexis Arnaudon - [c5a9622](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/c5a9622b35b0269c9ef58185c4de88654617b0f0))
- Add thalamus data (Alexis Arnaudon - [eeaa710](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/eeaa710b30c923d86db96433666e1621880e3a44))
- Default region data (Alexis Arnaudon - [594b800](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/594b8009cb997959aeca2acb6f017518846872e5))
- Add boundary data for O1 (Alexis Arnaudon - [2581494](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/2581494382ecdfd231923d48d92bdf6fc7a3a682))
- Add inner-only option (Alexis Arnaudon - [252a19f](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/252a19fad373ac8845e52c7cf72801425b8fd66a))

### Fixes

- Concatenate can work with multi brain regions (Adrien Berchet - [b37b8c4](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/b37b8c447cce59db3e00543d8cbf6fe31872dd68))
- Concatenate parameters keeps all mtypes (Adrien Berchet - [673acbf](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/673acbff112ce4c980e9f4cc6dd2eaf7b276eca9))
- Rename _CHC mtypes into _ChC (Adrien Berchet - [9e3ec8a](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/9e3ec8a844605cc49867fe7c85b69c2a25dca44b))
- Fix substitution (Alexis Arnaudon - [019e698](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/019e6982d52a66ff553790fbf38fa2f971048c34))

### Documentation Changes

- Add example in README for the --concatenate parameter (Adrien Berchet - [f7acc9f](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/f7acc9f76ae6a4f504e625a1e106ad15f548775b))

### General Changes

- Fix mouse thickness (arnaudon - [541b9b8](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/541b9b8e81038f7f126dd2d22dad5b7efdc95a29))
- Added O1 insitu (Alexis Arnaudon - [e51b70e](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/e51b70ebd7280426da968875d39b6828196a3490))

## [synthdb-v0.1.0](https://bbpgitlab.epfl.ch/neuromath/synthdb/compare/synthdb-v0.0.5...synthdb-v0.1.0)

> 15 May 2023

### New Features

- Add multi-region and easier rebuild (Alexis Arnaudon - [69b44f7](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/69b44f7d13fd0652e248319b5d3d29615b425d09))

### Chores And Housekeeping

- Replace `distutils.dir_util.copy_tree` by `shutil.copytree` in tests (Adrien Berchet - [ed9023c](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/ed9023c1b621f59b4edaf0160c7245ea6fb1763d))

### General Changes

- Add missing region_structure (arnaudon - [148edad](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/148edade386f8b0a6955014de3db73f0df54d95a))

## [synthdb-v0.0.5](https://bbpgitlab.epfl.ch/neuromath/synthdb/compare/synthdb-v0.0.4...synthdb-v0.0.5)

> 14 March 2023

### New Features

- Update to 3d_angles (Alexis Arnaudon - [fa0ef26](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/fa0ef26ab8d6594f48b414ad2ff4d16d5300cbbe))
- Add concatenate option (Alexis Arnaudon - [e79eccf](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/e79eccfe80c63a8762aa5a9e94b4756876069c99))

### Chores And Housekeeping

- Apply Copier template (Adrien Berchet - [a3c55da](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/a3c55da4e078f4c393def5f70f0dea330a813b30))

### CI Improvements

- Bump pre-commit hooks (Adrien Berchet - [90cc3e1](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/90cc3e14eed528f0c7de2391b9f9e90786b8a734))
- Setup min_versions job (Adrien Berchet - [4c23485](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/4c23485bebcfb4cdcf3fa9df080109fbe73bd1fc))

### General Changes

- Update synthesis-input with 3d angles (Alexis Arnaudon - [2de0fde](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/2de0fde9391b827edd61b0d43a7ee0ca3866e24b))

## [synthdb-v0.0.4](https://bbpgitlab.epfl.ch/neuromath/synthdb/compare/synthdb-v0.0.3...synthdb-v0.0.4)

> 13 December 2022

### New Features

- Automatically import files in the internal directory (Adrien Berchet - [aeb697c](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/aeb697cd8b8fcb0dfe0464ed541bdf8b67bf72cb))

### Fixes

- The pip list was not properly displayed in CLI function (Adrien Berchet - [c3b7f45](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/c3b7f4519f0dff83b2ee04e5856fbdcc40b6fcd4))

### Documentation Changes

- Add example in README (Adrien Berchet - [1a70345](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/1a7034546a5803a3f4e94c6c3583b1b4d0ac9d60))
- Fix changelog generation (Adrien Berchet - [9b0967d](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/9b0967d8c95f0f5fb12d109c3d2d52d7559d3936))

### CI Improvements

- Fix rules for jobs that should not be run in multi-project pipelines (Adrien Berchet - [47cea1d](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/47cea1dafb43740249143088907d01bb9b22423c))
- Fix tox 4 (Adrien Berchet - [66b74ed](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/66b74ed7202cbf392012d622e271deec26e76479))

<!-- auto-changelog-above -->

## [synthdb-v0.0.3](https://bbpgitlab.epfl.ch/neuromath/synthdb/compare/SynthDB-v0.0.2...synthdb-v0.0.3)

> 7 September 2022

### Documentation Changes

- Fix requirements for doc generation (Adrien Berchet - [88f8d1c](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/88f8d1cb73947327c7d423d7b42a06b40865ab4e))

### Refactoring and Updates

- Apply Copier template (Adrien Berchet - [7d488b7](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/7d488b7b46fc23c6046105d78c463b9f670e37be))

### Uncategorized Changes

- Add environment variable to skip version check (Adrien Berchet - [32833cf](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/32833cfd34ca452250198285f5980bde1f7ade3a))
- Add feature to validate inputs (Adrien Berchet - [991d32f](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/991d32f2b99ad3a78ab4fbcc79b184e842cf280a))
- Adding some circuit data (Alexis Arnaudon - [ea8b890](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/ea8b8902d7feea28d7d58da54661c7a13b0be289))
- Fix job that uses pre-version of synthesis-workflow (Adrien Berchet - [c63d32b](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/c63d32bfe2babd36ad1ffc7b01044ad87a59284e))
- Use pre-version for docs and lint jobs (Adrien Berchet - [24223d2](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/24223d2d8195c02c24388568247419b959f67d6d))
- Change name of package to be consistent with (Alexander Dietz - [aeeaa49](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/aeeaa4981de2a130d9b096b63ce044de3bd43b83))
- Add morphology release tools (Adrien Berchet - [01b968b](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/01b968bc137174282268ea47ec9dea4eed618b91))
- Mmb releases (Alexis Arnaudon - [5de2008](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/5de20088ea87311e14852fa55d8f553ca5a7e1b1))
- Rat sscx data (Alexis Arnaudon - [0e81f07](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/0e81f07824cbf4db5aea69e0aa525bb33e76353b))
- Fix _dendrite in scaling (arnaudon - [5930a47](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/5930a47e99aae3eb75889280d1cc7789cc097c0f))
- Add custom_parameter files and update-all cli (Alexis Arnaudon - [a545486](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/a545486046761c46da65cf52ef2dbaab41feb868))

## [SynthDB-v0.0.2](https://bbpgitlab.epfl.ch/neuromath/synthdb/compare/SynthDB-v0.0.1...SynthDB-v0.0.2)

> 6 April 2022

### Uncategorized Changes

- Fix coverage (Adrien Berchet - [e4185f1](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/e4185f17ed87ce9948a137b4e22a7dacb605b0c8))
- Add doc (Adrien Berchet - [7e51d4c](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/7e51d4cf554280a081516753cb1039f615f9bdfc))
- Improve CI (Adrien Berchet - [8206296](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/82062968dff18417234ff60b5a6a34add1638f39))

## SynthDB-v0.0.1

> 4 April 2022

### Uncategorized Changes

- Initial commit (Alexis Arnaudon - [cbfb0ea](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/cbfb0ea42b3953995d2c7eb48069ad5e2864e985))
- Setup SQLIte DB (arnaudon - [871f28c](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/871f28cc7bc6db33171823d225a18ff348102391))
- Add all sscx mtypes (arnaudon - [f62f6bb](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/f62f6bb060686de412f3e58ae2bcbaa7365cb749))
- Can pull multiple inputs at once, remove orphans and use only file names for params and distrs (Adrien Berchet - [bc56212](https://bbpgitlab.epfl.ch/neuromath/synthdb/commit/bc56212c8b7ecba642a17d327346b7491cffe120))
