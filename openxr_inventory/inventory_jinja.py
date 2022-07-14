#!/usr/bin/env python3 -i
# Copyright 2022, The Khronos Group Inc.
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from jinja2 import Environment, FileSystemLoader


def make_jinja_environment():
    """Returns a Jinja2 environment set up to find the templates in this module."""
    module_dir = Path(__file__).parent.resolve()
    search_paths = [str(module_dir / "templates")]
    return Environment(loader=FileSystemLoader(search_paths), autoescape=True)
