#!/bin/sh
# Copyright 2022, The Khronos Group Inc.
#
# SPDX-License-Identifier: Apache-2.0
set -e

for fn in runtimes/*.json; do
    echo "Checking $fn against the runtime schema"
    python3 -m jsonschema runtime_schema.json -i "$fn"
done

for fn in clients/*.json; do
    echo "Checking $fn against the client schema"
    python3 -m jsonschema client_schema.json -i "$fn"
done
