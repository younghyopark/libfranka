"""Bundle the non-system dylibs of a macOS wheel together with their licenses.

Usage: repair_macos_wheel.py <wheel> <dest_dir>

This is the cibuildwheel repair command for the pylibfranka-macos wheels. Like
cibuildwheel's default, it runs delocate, which copies the Homebrew dylibs the
extension links against into the wheel. It then adds the licenses of libfranka
and of every bundled or compiled-in third-party library to the wheel's
.dist-info/licenses directory, and fails if a license cannot be found.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

from delocate.libsana import wheel_libs
from delocate.wheeltools import InWheel

REPO_ROOT = Path(__file__).resolve().parents[2]
VENDORED_LICENSES = REPO_ROOT / "pylibfranka" / "licenses"
LICENSE_PATTERNS = ("LICEN[CS]E*", "COPYING*", "NOTICE*", "COPYRIGHT*")
CELLAR_PATH = re.compile(r"^(?P<prefix>.*/Cellar/(?P<name>[^/]+)/[^/]+)/")

# Header-only libraries that are compiled into the wheel but not bundled as dylibs.
HEADER_ONLY_FORMULAE = ("eigen", "urdfdom_headers")
HEADER_ONLY_VENDORED = ("pybind11",)


def formula_prefix(name):
    """Return the Homebrew Cellar directory of an installed formula."""
    prefix = subprocess.check_output(["brew", "--prefix", name], text=True).strip()
    return Path(prefix).resolve()


def license_files(name, prefix=None):
    """Return the license files of a library, preferring the ones Homebrew installed."""
    files = []
    if prefix is not None:
        for directory in (prefix, prefix / "share" / "doc" / name):
            for pattern in LICENSE_PATTERNS:
                files += [path for path in directory.glob(pattern) if path.is_file()]
    if not files:
        files = [path for path in (VENDORED_LICENSES / name).glob("*") if path.is_file()]
    if not files:
        sys.exit(f"No license found for {name}. Add it to {VENDORED_LICENSES / name}.")
    return sorted(set(files))


def bundled_formulae(wheel):
    """Return the Homebrew formulae whose dylibs the wheel links against."""
    formulae = {}
    for library in wheel_libs(str(wheel)):
        match = CELLAR_PATH.match(str(Path(library).resolve()))
        if match:
            formulae[match["name"]] = Path(match["prefix"])
    return formulae


def main():
    wheel, dest_dir = Path(sys.argv[1]), Path(sys.argv[2])
    dest_dir.mkdir(parents=True, exist_ok=True)

    libraries = bundled_formulae(wheel)
    libraries.update({name: formula_prefix(name) for name in HEADER_ONLY_FORMULAE})
    libraries.update({name: None for name in HEADER_ONLY_VENDORED})

    before = set(dest_dir.glob("*.whl"))
    subprocess.check_call(
        ["delocate-wheel", "--require-archs", "arm64", "--sanitize-rpaths", "-w", str(dest_dir),
         "-v", str(wheel)]
    )
    (repaired,) = set(dest_dir.glob("*.whl")) - before

    with InWheel(str(repaired), str(repaired)):
        (dist_info,) = Path.cwd().glob("*.dist-info")
        licenses = dist_info / "licenses"
        for name in ("LICENSE", "NOTICE"):
            (licenses / "libfranka").mkdir(parents=True, exist_ok=True)
            shutil.copy(REPO_ROOT / name, licenses / "libfranka" / name)
        for name, prefix in sorted(libraries.items()):
            (licenses / "third_party" / name).mkdir(parents=True, exist_ok=True)
            for path in license_files(name, prefix):
                shutil.copy(path, licenses / "third_party" / name / path.name)
            print(f"Added licenses of {name}")


if __name__ == "__main__":
    main()
