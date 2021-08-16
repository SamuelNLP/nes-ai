"""
Setup script to package the module
"""

import ast
import re
from pathlib import Path

from setuptools import find_packages, setup

_PACKAGE_NAME = "nes_ai"

BASE_DIR = Path(__file__).resolve().parent / _PACKAGE_NAME
_VERSION_RE = re.compile(r"__version__\s+=\s+(?P<version>.*)")


def get_version():
    with open(str(BASE_DIR / "__init__.py")) as file:
        match = _VERSION_RE.search(file.read())
    version_ = match.group("version") if match else '"unknown"'
    return str(ast.literal_eval(version_))


setup(
    name=_PACKAGE_NAME.replace("_", "-"),
    version=get_version(),
    author="Samuel Pedro",
    description="Nes AI - a bot that tries to play NES games.",
    include_package_data=True,
    install_requires=["aenum", "numpy", "networkx", "nes-py", "matplotlib", "sympy"],
    data_files=list(),
    packages=find_packages(),
)
