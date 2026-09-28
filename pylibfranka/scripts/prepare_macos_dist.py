"""Turn the pylibfranka project into the unofficial pylibfranka-macos distribution.

Run this before building the macOS wheels for PyPI. It only changes the package
metadata: the wheels still install the pylibfranka module, and installing from
git with `pip install "pylibfranka @ git+..."` keeps working without it.
"""

import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]


def replace(path, old, new):
    text = path.read_text()
    if text.count(old) != 1:
        sys.exit(f"{path.name}: expected exactly one occurrence of {old!r}")
    path.write_text(text.replace(old, new))


pyproject = PROJECT / "pyproject.toml"
replace(pyproject, 'name = "pylibfranka"', 'name = "pylibfranka-macos"')
replace(
    pyproject,
    'description = "Python bindings for libfranka - Control Franka robots with Python"',
    'description = "Unofficial macOS build of pylibfranka, the Python bindings for libfranka"',
)
replace(pyproject, 'readme = "README.md"', 'readme = "README-macos.md"')
replace(
    pyproject,
    'authors = [{name = "Franka Robotics GmbH", email = "info@franka.de"}]\n',
    'authors = [{name = "Franka Robotics GmbH", email = "info@franka.de"}]\n'
    'maintainers = [{name = "Younghyo Park"}]\n',
)
replace(pyproject, '"Operating System :: POSIX :: Linux",', '"Operating System :: MacOS",')
replace(
    pyproject,
    '"Programming Language :: Python :: 3.12",',
    '"Programming Language :: Python :: 3.12",\n'
    '    "Programming Language :: Python :: 3.13",\n'
    '    "Programming Language :: Python :: 3.14",',
)
replace(
    pyproject,
    'Homepage = "https://github.com/frankarobotics/libfranka"\n',
    'Homepage = "https://github.com/younghyopark/libfranka/tree/macos-support"\n'
    'Upstream = "https://github.com/frankarobotics/libfranka"\n',
)
replace(
    pyproject,
    'Repository = "https://github.com/frankarobotics/libfranka"',
    'Repository = "https://github.com/younghyopark/libfranka"',
)
replace(
    pyproject,
    'Issues = "https://github.com/frankarobotics/libfranka/issues"',
    'Issues = "https://github.com/younghyopark/libfranka/issues"',
)
replace(PROJECT / "setup.py", 'name="pylibfranka",', 'name="pylibfranka-macos",')
print("Prepared the pylibfranka-macos distribution")
