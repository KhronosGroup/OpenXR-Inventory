#!/usr/bin/env python3 -i
# Copyright 2022, The Khronos Group Inc.
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
import re
from typing import Dict, List, Tuple

from .inventory_data import ExtensionEntry
from .runtime_inventory import RuntimeData
from .client_inventory import ClientData

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


def compute_known_extensions(runtimes: List[RuntimeData], clients: List[ClientData]) -> List[str]:
    """Compute a list of all known extensions, sorted as in the spec itself."""
    known_extensions = set()

    for runtime in runtimes:
        known_extensions.update(ext.name for ext in runtime.extensions)

    for client in clients:
        for component in client.components:
            known_extensions.update(ext.name for ext in component.extensions)

    return list(sorted(known_extensions, key=ext_name_key))


def compute_runtime_support(runtimes: List[RuntimeData]) -> Dict[str, List[str]]:
    """Compute a dictionary from runtime names to a list of supported extension names."""
    runtime_support = {}
    for runtime in runtimes:
        support = [ext.name for ext in runtime.extensions]
        runtime_support[runtime.name] = support
    return runtime_support

def compute_client_support(clients: List[ClientData]) -> Dict[str, List[str]]:
    """Compute a dictionary from client names to a list of supported extension names."""
    client_support = {}
    for client in clients:
        support = []
        for component in client.components:
            support += [ext.name for ext in component.extensions]
        client_support[client.name] = support
    return client_support

def compute_known_form_factors(runtimes: List[RuntimeData], clients: List[ClientData]) -> List[str]:
    known_form_factors = {}

    for runtime in runtimes:
        for ff in runtime.form_factors:
            for vc in ff.view_configurations:
                known_form_factors[ff.name] = known_form_factors.get(ff.name, {})
                for ebm in vc.environment_blend_modes:
                    known_form_factors[ff.name][vc.name] = known_form_factors[ff.name].get(vc.name, set())
                    known_form_factors[ff.name][vc.name].add(ebm.name)

    for client in clients:
        for ff in client.form_factors:
            for vc in ff.view_configurations:
                known_form_factors[ff.name] = known_form_factors.get(ff.name, {})
                for ebm in vc.environment_blend_modes:
                    known_form_factors[ff.name][vc.name] = known_form_factors[ff.name].get(vc.name, set())
                    known_form_factors[ff.name][vc.name].add(ebm.name)

    return known_form_factors


def compute_form_factor_support(runtimes: List[RuntimeData], clients: List[ClientData]) -> Dict[str, List[str]]:
    form_factor_support = {}

    for runtime in runtimes:
        if runtime.form_factors:
            form_factor_support[runtime.name] = {}

            for ff in runtime.form_factors:
                form_factor_support[runtime.name][ff.name] = {}

                for vc in ff.view_configurations:
                    form_factor_support[runtime.name][ff.name][vc.name] = set()

                    for ebm in vc.environment_blend_modes:
                        form_factor_support[runtime.name][ff.name][vc.name].add(ebm.name)

    for client in clients:
        if client.form_factors:
            form_factor_support[client.name] = {}

            for ff in client.form_factors:
                form_factor_support[client.name][ff.name] = {}

                for vc in ff.view_configurations:
                    form_factor_support[client.name][ff.name][vc.name] = set()

                    for ebm in vc.environment_blend_modes:
                        form_factor_support[client.name][ff.name][vc.name].add(ebm.name)

    return form_factor_support

class ExtensionSupport:
    runtime_count: int
    client_count: int

    def __init__(self, runtime_count, client_count):
        self.runtime_count = runtime_count
        self.client_count = client_count

def compute_extension_support(
    runtimes: List[RuntimeData],
    clients: List[ClientData],
) -> Dict[str, ExtensionSupport]:
    """
    For each extension, find all the runtimes that support it.

    Returns a dict with extension names as the keys, and a list
    of (RuntimeData, ExtensionEntry) tuples as the values.
    """
    known_extensions = compute_known_extensions(runtimes, clients)
    extension_support = {}
    for extension_name in known_extensions:
        runtime_count = 0
        client_count = 0

        # Count our runtime support
        for runtime in runtimes:
            if runtime.get_extension_entry(extension_name):
                runtime_count += 1

        # Get all the client support
        for client in clients:
            if len(client.get_extension_entry(extension_name)) > 0:
                client_count += 1

        # Filter out the empty ones
        extension_support[extension_name] = ExtensionSupport(runtime_count, client_count)
    return extension_support


def generate_runtime_report(
    runtimes: List[RuntimeData],
    clients: List[ClientData],
    template_filename: str = "runtime_extension_support.jinja2.html",
    out_filename: str = "public/runtime_extension_support.html",
):
    """
    Write an HTML file containing information about runtime extension support.
    """
    from .inventory_jinja import make_jinja_environment

    env = make_jinja_environment()
    env.globals["cat"] = ExtensionCategory
    env.globals["cat_captions"] = _category_captions
    env.globals["categorize_ext"] = categorize_ext_name
    template = env.get_template(template_filename)
    spec_url = "https://www.khronos.org/registry/OpenXR/specs/1.1/html/xrspec.html"
    contents = template.render(
        extensions=compute_known_extensions(runtimes, clients),
        extension_support=compute_extension_support(runtimes, clients),
        runtime_support=compute_runtime_support(runtimes),
        client_support=compute_client_support(clients),
        known_form_factors=compute_known_form_factors(runtimes, clients),
        form_factor_support=compute_form_factor_support(runtimes, clients),
        runtimes=runtimes,
        clients=clients,
        spec_url=spec_url,
    )

    if contents:
        out_file = Path(__file__).parent.parent / out_filename
        print("Writing {}".format(out_file))
        with open(out_file, "w", encoding="utf-8") as fp:
            fp.write(contents)


def generate_client_report(
    runtimes: List[RuntimeData],
    clients: List[ClientData],
    template_filename: str = "client_extension_support.jinja2.html",
    out_filename: str = "public/client_extension_support.html",
):
    """
    Write an HTML file containing information about client extension support.
    """
    from .inventory_jinja import make_jinja_environment

    env = make_jinja_environment()
    env.globals["cat"] = ExtensionCategory
    env.globals["cat_captions"] = _category_captions
    env.globals["categorize_ext"] = categorize_ext_name
    template = env.get_template(template_filename)
    spec_url = "https://www.khronos.org/registry/OpenXR/specs/1.1/html/xrspec.html"
    contents = template.render(
        extensions=compute_known_extensions(runtimes, clients),
        extension_support=compute_extension_support(runtimes, clients),
        runtime_support=compute_runtime_support(runtimes),
        client_support=compute_client_support(clients),
        known_form_factors=compute_known_form_factors(runtimes, clients),
        form_factor_support=compute_form_factor_support(runtimes, clients),
        runtimes=runtimes,
        clients=clients,
        spec_url=spec_url,
    )

    if contents:
        out_file = Path(__file__).parent.parent / out_filename
        print("Writing {}".format(out_file))
        with open(out_file, "w", encoding="utf-8") as fp:
            fp.write(contents)


if __name__ == "__main__":
    from .runtime_inventory import load_all_runtimes
    from .client_inventory import load_all_clients

    runtimes = load_all_runtimes()
    clients = load_all_clients()
    generate_runtime_report(runtimes, clients)
    generate_client_report(runtimes, clients)
