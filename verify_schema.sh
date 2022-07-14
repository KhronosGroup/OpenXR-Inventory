#!/bin/sh
# Copyright 2022, The Khronos Group Inc.
#
# SPDX-License-Identifier: Apache-2.0
set -e

for fn in runtimes/*.json; do
    echo "Checking $fn against the schema"
    python3 -m jsonschema schema.json -i "$fn"
done
