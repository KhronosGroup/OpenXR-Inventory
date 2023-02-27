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
_RE_IS_EXTX = re.compile(r"^XR_EXTX_.*")
_RE_IS_OTHER_X = re.compile(r"^XR_([A-Z0-9]+)X_.*")


class ExtensionCategory:
    KHR = 0
    EXT = 1
    VENDOR = 2
    KHX = 3
    EXTX = 4
    VENDORX = 5

    @classmethod
    def all_categories(cls):
        return (
            cls.KHR,
            cls.EXT,
            cls.VENDOR,
            cls.KHX,
            cls.EXTX,
            cls.VENDORX,
        )


def categorize_ext_name(ext_name: str) -> int:
    """Return an integer corresponding to the category/group an extension name belongs to."""
    if _RE_IS_KHR.match(ext_name):
        return ExtensionCategory.KHR
    if _RE_IS_EXT.match(ext_name):
        return ExtensionCategory.EXT

    # anything else gets a 2
    ret = ExtensionCategory.VENDOR

    if _RE_IS_KHX.match(ext_name):
        return ExtensionCategory.KHX
    if _RE_IS_EXTX.match(ext_name):
        return ExtensionCategory.EXTX
    if _RE_IS_OTHER_X.match(ext_name):
        return ExtensionCategory.VENDORX

    return ret


_category_captions = {
    ExtensionCategory.KHR: "Khronos",
    ExtensionCategory.EXT: "Multi-Vendor",
    ExtensionCategory.VENDOR: "Vendor",
    ExtensionCategory.KHX: "Provisional/Experimental Khronos",
    ExtensionCategory.EXTX: "Provisional/Experimental Multi-Vendor",
    ExtensionCategory.VENDORX: "Provisional/Experimental Vendor",
}


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
    return (categorize_ext_name(ext_name), ext_name)


def compute_known_extensions(runtimes: List[RuntimeData]) -> List[str]:
    """Compute a list of all known extensions, sorted as in the spec itself."""
    known_extensions = set()
    for runtime in runtimes:
        known_extensions.update(ext.name for ext in runtime.extensions)
    return list(sorted(known_extensions, key=ext_name_key))


def compute_runtime_support(runtimes: List[RuntimeData]) -> Dict[str, List[str]]:
    """Compute a dictionary from runtime names to a list of supported extension names."""
    runtime_support = {}
    for runtime in runtimes:
        support = [ext.name for ext in runtime.extensions]
        runtime_support[runtime.name] = support
    return runtime_support


def compute_known_form_factors(runtimes: List[RuntimeData]) -> List[str]:
    known_modes = set()
    for runtime in runtimes:
        known_modes.update(ff.name for ff in runtime.form_factors)
    return list(sorted(known_modes, key=ext_name_key))


def compute_form_factor_support(runtimes: List[RuntimeData]) -> Dict[str, List[str]]:
    runtime_form_factor_support = {}
    for runtime in runtimes:
        support = [ff.name for ff in runtime.form_factors]
        runtime_form_factor_support[runtime.name] = support
    return runtime_form_factor_support


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
    out_filename: str = "public/" + _FILENAME_STEM + ".html",
):
    """
    Write an HTML file in the parent directory containing information about the available extensions
    and the runtimes that support them.
    """
    from .inventory_jinja import make_jinja_environment

    env = make_jinja_environment()
    env.globals["cat"] = ExtensionCategory
    env.globals["cat_captions"] = _category_captions
    env.globals["categorize_ext"] = categorize_ext_name
    template = env.get_template(template_filename)
    contents = template.render(
        extensions=compute_known_extensions(runtimes),
        extension_support=compute_extension_support(runtimes),
        runtime_support=compute_runtime_support(runtimes),
        known_form_factors=compute_known_form_factors(runtimes),
        form_factor_support=compute_form_factor_support(runtimes),
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
