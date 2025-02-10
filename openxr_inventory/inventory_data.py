#!/usr/bin/env python3 -i
# Copyright 2022, The Khronos Group Inc.
#
# SPDX-License-Identifier: Apache-2.0

import json
from dataclasses import dataclass
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
class EnvironmentBlendModeEntry:
    """
    An entry in the "environment_blend_modes" array for a runtime or layer.

    Corresponds to the schema reference `#/definitions/environment_blend_mode`.
    """

    name: str
    """Environment blend mode name"""

    @classmethod
    def from_json(cls, d: Union[Dict, str]) -> "EnvironmentBlendModeEntry":
        return EnvironmentBlendModeEntry(name=d)

@dataclass
class ViewConfigurationEntry:
    """
    An entry in the "view_configurations" array for a runtime or layer.

    Corresponds to the schema reference `#/definitions/view_configuration`.
    """

    name: str
    """View configuration name"""

    environment_blend_modes: List[EnvironmentBlendModeEntry]
    """Environment blend modes supported for the view configuration"""

    @classmethod
    def from_json(cls, d: Union[Dict, str]) -> "ViewConfigurationEntry":
        return ViewConfigurationEntry(name=d["view_configuration"], environment_blend_modes=[EnvironmentBlendModeEntry.from_json(b) for b in d["environment_blend_modes"]])

@dataclass
class FormFactorEntry:
    """
    An entry in the "form_factors" array for a runtime or layer.

    Corresponds to the schema reference `#/definitions/form_factor`.
    """

    name: str
    """Form Factor name"""

    view_configurations: List[ViewConfigurationEntry]
    """View configurations supported for the form factor"""

    @classmethod
    def from_json(cls, d: Union[Dict, str]) -> "FormFactorEntry":
        return FormFactorEntry(name=d["form_factor"], view_configurations=[ViewConfigurationEntry.from_json(v) for v in d["view_configurations"]])
