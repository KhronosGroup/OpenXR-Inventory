#!/usr/bin/env python3 -i
# Copyright 2022, The Khronos Group Inc.
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
import re
from typing import Dict, List, Tuple

from .runtime_inventory import ExtensionEntry, RuntimeData

_RE_IS_KHR = re.compile(r"^XR_KHR_.*")
_RE_IS_EXT = re.compile(r"^XR_EXT_.*")
_RE_IS_KHX = re.compile(r"^XR_KHX_.*")
_RE_IS_EXTX = re.compile(r"^XR_KHX_.*")
_RE_IS_OTHER_X = re.compile(r"^XR_([A-Z0-9]+)X_.*")


def _categorize(ext_name: str) -> int:
    """Return an integer corresponding to the category/group an extension name belongs to."""
    if _RE_IS_KHR.match(ext_name):
        return 0
    if _RE_IS_EXT.match(ext_name):
        return 1

    # anything else gets a 2
    ret = 2

    if _RE_IS_KHX.match(ext_name):
        return 3
    if _RE_IS_EXTX.match(ext_name):
        return 4
    if _RE_IS_OTHER_X.match(ext_name):
        return 5

    return ret


def ext_name_key(ext_name: str):
    """
    Turn an OpenXR extension name into a tuple that can be used as a key for sorting.

    This puts the extensions in the order:

    - KHR
    - EXT (multi-vendor)
    - single-vendor
    - Provisional/experimental extensions (based on their author tag):
      - KHX
      - EXTX
      - any other author ID ending in X
    """
    return (_categorize(ext_name), ext_name)


def compute_known_extensions(runtimes: List[RuntimeData]) -> List[str]:
    """Compute a list of all known extensions, sorted as in the spec itself."""
    known_extensions = set()
    for runtime in runtimes:
        known_extensions.update(ext.name for ext in runtime.extensions)
    return list(sorted(known_extensions, key=ext_name_key))


def compute_extension_support(
    runtimes: List[RuntimeData],
) -> Dict[str, List[Tuple[RuntimeData, ExtensionEntry]]]:
    """
    For each extension, find all the runtimes that support it.

    Returns a dict with extension names as the keys, and a list
    of (RuntimeData, ExtensionEntry) tuples as the values.
    """
    known_extensions = compute_known_extensions(runtimes)
    extension_support = {}
    for extension_name in known_extensions:
        # Get all the support
        support = [
            (runtime, runtime.get_extension_entry(extension_name))
            for runtime in runtimes
        ]
        # Filter out the empty ones
        support = [(runtime, entry) for runtime, entry in support if entry]
        extension_support[extension_name] = support
    return extension_support


_FILENAME_STEM = "extension_support"


def generate_report(
    runtimes: List[RuntimeData],
    template_filename: str = _FILENAME_STEM + ".jinja2.html",
    out_filename: str = _FILENAME_STEM + ".html",
):
    """
    Write an HTML file in the parent directory containing information about the available extensions
    and the runtimes that support them.
    """
    from .inventory_jinja import make_jinja_environment

    env = make_jinja_environment()
    template = env.get_template(template_filename)
    contents = template.render(
        extensions=compute_known_extensions(runtimes),
        extension_support=compute_extension_support(runtimes),
        runtimes=runtimes,
    )
    if contents:
        out_file = Path(__file__).parent.parent / out_filename
        print("Writing {}".format(out_file))
        with open(out_file, "w", encoding="utf-8") as fp:
            fp.write(contents)


if __name__ == "__main__":
    from .runtime_inventory import load_all_runtimes

    runtimes = load_all_runtimes()
    generate_report(runtimes)
