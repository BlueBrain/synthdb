#!/bin/bash -l

deactivate
python -m virtualenv venv
source venv/bin/activate
module load unstable python-dev

pip install  --index-url https://bbpteam.epfl.ch/repository/devpi/bbprelman/dev/+simple/ git+https://bbpgitlab.epfl.ch/neuromath/synthesis-workflow.git@boundary_examples
pip install  --index-url https://bbpteam.epfl.ch/repository/devpi/bbprelman/dev/+simple/ git+https://bbpgitlab.epfl.ch/neuromath/region-grower.git@boundary_merge
pip install git+https://github.com/BlueBrain/NeuroTS.git@boundary_new
