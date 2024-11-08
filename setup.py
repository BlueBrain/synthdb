"""Setup for the synthdb package."""

import importlib.util
from pathlib import Path

from setuptools import find_namespace_packages
from setuptools import setup

spec = importlib.util.spec_from_file_location(
    "synthdb.version",
    "synthdb/version.py",
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
VERSION = module.VERSION

reqs = [
    "click>=7.0",
    "luigi>=3.2",
    "luigi-tools>=0.0.19",
    "neurots>=3.5.0,<4",
    "sqlalchemy>=1.4.24",
    "synthesis-workflow>=0.1.1",
]

doc_reqs = [
    "docutils<0.21",  # Temporary fix for m2r2
    "m2r2",
    "sphinx",
    "sphinx-autoapi",
    "sphinx-bluebrain-theme",
    "sphinx-click",
]

test_reqs = [
    "pytest>=6.1",
    "pytest-click>=1.1",
    "pytest-console-scripts>=1.4",
    "pytest-cov>=4.1",
    "pytest-html>=3.2",
]

setup(
    name="synthdb",
    author="bbp-ou-cells",
    author_email="bbp-ou-cells@groupes.epfl.ch",
    description="Small database to host synthesis-related files and integrated tools.",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://bbpteam.epfl.ch/documentation/projects/synthdb",
    project_urls={
        "Tracker": "https://bbpteam.epfl.ch/project/issues/projects/CELLS/issues",
        "Source": "https://bbpgitlab.epfl.ch/neuromath/synthdb",
    },
    license="BBP-internal-confidential",
    packages=find_namespace_packages(include=["synthdb*"], exclude=["synthdb.alembic*"]),
    python_requires=">=3.9",
    version=VERSION,
    install_requires=reqs,
    extras_require={
        "docs": doc_reqs,
        "test": test_reqs,
    },
    entry_points={
        "console_scripts": [
            "synthdb=synthdb.cli:cli",
        ],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)
