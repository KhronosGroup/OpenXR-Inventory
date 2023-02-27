#!/usr/bin/env python3 -i
# Copyright 2022, The Khronos Group Inc.
#
# SPDX-License-Identifier: Apache-2.0

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union


@dataclass
class ExtensionEntry:
    """
    An entry in the "extensions" array for a runtime or layer.

    Corresponds to the schema reference `#/definitions/extension`.
    """

    name: str
    """Extension name"""

    notes: Optional[str] = None
    """Optional notes about the support/use of this extension"""

    @classmethod
    def from_json(cls, d: Union[Dict, str]) -> "ExtensionEntry":
        """Create an ExtensionEntry from either a str or dict as you'd get from parsing the JSON."""
        if isinstance(d, str):
            return ExtensionEntry(name=d)
        return ExtensionEntry(name=d["name"], notes=d.get("notes"))


@dataclass
class FormFactorEntry:
    """
    An entry in the "form_factors" array for a runtime or layer.

    Corresponds to the schema reference `#/definitions/form_factor`.
    """

    name: str
    """Form Factor name"""

    @classmethod
    def from_json(cls, d: Union[Dict, str]) -> "FormFactorEntry":
        if d["form_factor"]:
            return FormFactorEntry(name=d["form_factor"])
        else:
            return FormFactorEntry(name="OPAQUE")


@dataclass(order=True)
class RuntimeData:
    """Data about a single runtime on a single platform, corresponds to a single JSON file in the inventory"""

    stub: str
    """A short identifier suitable for use as an HTML anchor, file name stem, etc."""

    name: str
    """The name of the runtime (on this platform)"""

    conformance_submission: Optional[int]
    """The conformance submission number of this runtime on this platform"""

    conformance_notes: Optional[str]
    """Free-form text about conformance status"""

    vendor: str
    """The vendor's name"""

    extensions: List[ExtensionEntry]
    """The supported extensions"""

    form_factors: List[FormFactorEntry]
    """The supported form factors"""

    def get_extension_entry(self, ext_name: str) -> Optional[ExtensionEntry]:
        """
        Get the entry for the named extension, if it exists.

        This can tell you if the runtime supports that extension, as well as any notes from the inventory.
        """
        extension_entries = [
            entry for entry in self.extensions if entry.name == ext_name
        ]

        if not extension_entries:
            return
        assert len(extension_entries) == 1
        return extension_entries[0]

    @property
    def conformance_submission_url(self) -> Optional[str]:
        if self.conformance_submission:
            return "https://www.khronos.org/conformance/adopters/conformant-products/openxr#submission_{}".format(
                self.conformance_submission
            )

    @classmethod
    def from_json(cls, stub: str, d: Dict) -> "RuntimeData":
        """
        Create an object from the data loaded from a json file.

        'stub' should be the stem of the filename, typically.
        """
        exts = [ExtensionEntry.from_json(entry) for entry in d["extensions"]]
        form_factors = [FormFactorEntry.from_json(entry) for entry in (d.get("form_factors", []))]
        return RuntimeData(
            stub=stub,
            name=d["name"],
            conformance_submission=d.get("conformance_submission"),
            conformance_notes=d.get("conformance_notes"),
            vendor=d["vendor"],
            extensions=exts,
            form_factors=form_factors,
        )


def load_all_runtimes(directory=None) -> List[RuntimeData]:
    """Load all runtime inventory files."""
    if not directory:
        directory = Path(__file__).parent.parent / "runtimes"

    failures = []
    results = []
    for f in directory.glob("*.json"):
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        try:
            parsed = RuntimeData.from_json(f.stem, data)
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
