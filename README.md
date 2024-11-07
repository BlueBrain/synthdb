# SynthDB

Small database to host synthesis-related files.

The synthesis inputs stored in SynthDB are usually created by the ``synthesis-workflows`` package
and are usually meant to be used by the ``region-grower`` package.


## Installation

Use pip to install this package:

```bash
pip install  synthdb
```

For some operations (e.g. create, update or delete operations), this package should be installed in editable mode:
```bash
git clone https://github.com/BlueBrain/synthdb.git
cd synthdb
pip install  -e .
```

## Usage

This package contains a set of configuration files for the synthesis codes and a small database that
maps a given set of brain region, mtype and luigi configuration. It also provides several commands
to manage the database and to create new sets of configuration files.

The commands are listed in the Command Line Interface page of the documentation.

If you use commands that modify the internal state you will probably want to commit the changes afterwards.

## Example

Here is an example of a variety of commands

### Prepare environment

```bash
mkvirtualenv demo_synthdb
mkdir /tmp/synthdb_demo
cd /tmp/synthdb_demo
git clone https://github.com/BlueBrain/synthdb.git
pip install -e ./synthdb
```

### Show usage
```bash
synthdb --help
synthdb morphology-release --help
synthdb synthesis-inputs --help
```

### Morphology release command

#### Show list of morphology releases
```bash
synthdb morphology-release list
```

#### Create a new morphology release
```bash
synthdb morphology-release create a_new_rat_release --gpfs-path rat_release
```

#### Check the new entry
```bash
synthdb morphology-release list
```

#### Check the auto-generated `pip list` of the new entry
```bash
synthdb morphology-release list --with-pip-list
```

#### Remove a morphology release
```bash
synthdb morphology-release remove a_new_rat_release
```

#### Check that the entry was removed
```bash
synthdb morphology-release list
```

### Synthesis inputs command

#### Show list of synthesis-inputs
```bash
synthdb synthesis-inputs list
```

#### Show filtered list
```bash
synthdb synthesis-inputs list --mtype L6_TPC:A
```

#### Check that all entries are valid according to the current environment
```bash
synthdb synthesis-inputs validate
```

#### Pull params and distrs for a given entry (one can also pull several or all entries at once)
```bash
synthdb synthesis-inputs pull --brain-region sscx --mtype L6_TPC:A --luigi-config luigi_sscx --output-path synth_inputs
```
It is possible to refine the filter using any combination of the ``--brain-region``, ``--mtype`` and ``--luigi-config`` parameters.

#### Pull params and distrs for several entries into one file
```bash
synthdb synthesis-inputs pull --brain-region sscx --output-path synth_inputs_sscx --concatenate
```
Here all the distributions and parameters of the SSCx brain region are pulled in the ``tmd_parameters.json`` and ``tmd_distributions.json`` files.
It is possible to refine the filter using any combination of the ``--brain-region``, ``--mtype`` and ``--luigi-config`` parameters.

#### Create a new entry
```bash
synthdb synthesis-inputs create new_region L6_TPC:A luigi_sscx --parameters-path tmd_parameters_luigi_sscx_sscx_L6_TPC:A.json --distributions-path tmd_distributions_luigi_sscx_sscx_L6_TPC:A.json
```

#### Check the new entry
```bash
synthdb synthesis-inputs list --brain-region new_region
```

#### Remove the new entry
```bash
synthdb synthesis-inputs remove new_region L6_TPC:A luigi_sscx
```

#### Rebuild an entry using the morphology release given in the luigi config file
```bash
synthdb synthesis-inputs rebuild --brain-region sscx --mtype L6_TPC:A --luigi-config luigi_sscx
```

## Funding & Acknowledgment

The development of this software was supported by funding to the Blue Brain Project,
a research center of the École polytechnique fédérale de Lausanne (EPFL),
from the Swiss government's ETH Board of the Swiss Federal Institutes of Technology.

Copyright (c) 2022-2024 Blue Brain Project/EPFL
