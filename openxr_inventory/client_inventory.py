#!/usr/bin/env python3 -i
# Copyright 2022, The Khronos Group Inc.
#
# SPDX-License-Identifier: Apache-2.0

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union

from .inventory_data import ExtensionEntry, EnvironmentBlendModeEntry, ViewConfigurationEntry, FormFactorEntry

@dataclass
class ComponentEntry:
    """Data about component of a client"""

    name: str
    """The name of the component"""

    abbreviation: str
    """The abbreviation to use in the client matrix"""

    extensions: List[ExtensionEntry]
    """The supported extensions"""

    @classmethod
    def from_json(self, d: Dict) -> "ComponentEntry":
        exts = [ExtensionEntry.from_json(entry) for entry in d["extensions"]]
        return ComponentEntry(
            name=d["name"],
            abbreviation=d["abbreviation"],
            extensions=exts
        )


@dataclass(order=True)
class ClientData:
    """Data about a single client, corresponds to a single JSON file in the inventory"""

    stub: str
    """A short identifier suitable for use as an HTML anchor, file name stem, etc."""

    name: str
    """The name of the client"""

    notes: Optional[str]
    """Free-form text with extra information"""

    vendor: str
    """The vendor's name"""

    components: List[ComponentEntry]
    """The components"""

    form_factors: List[FormFactorEntry]
    """The supported form factors"""

    def get_component_for_extension(self, ext_name: str) -> List[ComponentEntry]:
        component_entries = []
        for component in self.components:
            for entry in component.extensions:
                if entry.name == ext_name:
                    component_entries += [ component ]
        
        return component_entries

    def get_extension_entry(self, ext_name: str) -> List[ExtensionEntry]:
        """
        Get the entries for the named extension, if they exists.

        This can tell you if the client supports that extension, as well as any notes from the inventory.
        """
        extension_entries = []

        for component in self.components:
            extension_entries += [ entry for entry in component.extensions if entry.name == ext_name ]

        return extension_entries

    @property
    def conformance_submission_url(self) -> Optional[str]:
        if self.conformance_submission:
            return "https://www.khronos.org/conformance/adopters/conformant-products/openxr#submission_{}".format(
                self.conformance_submission
            )

    @classmethod
    def from_json(cls, stub: str, d: Dict) -> "ClientData":
        """
        Create an object from the data loaded from a json file.

        'stub' should be the stem of the filename, typically.
        """
        comps = [ComponentEntry.from_json(entry) for entry in d["components"]]
        form_factors = [FormFactorEntry.from_json(entry) for entry in (d.get("form_factors", []))]
        return ClientData(
            stub=stub,
            name=d["name"],
            notes=d.get("notes"),
            vendor=d["vendor"],
            components=comps,
            form_factors=form_factors,
        )


def load_all_clients(directory=None) -> List[ClientData]:
    """Load all client inventory files."""
    if not directory:
        directory = Path(__file__).parent.parent / "clients"

    failures = []
    results = []
    for f in directory.glob("*.json"):
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        try:
            parsed = ClientData.from_json(f.stem, data)
            results.append(parsed)
            print("Loaded %s" % parsed.stub)
        except KeyError as e:
            print(
                "Error loading %s (probably missing required property), skipping..."
                % str(f)
            )
            print(e)
            failures.append(str(f))
    if failures:
        print(failures)
        raise RuntimeError(
            "Could not parse some files, probably missing required properties"
        )
    return results
