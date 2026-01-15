#!/usr/bin/env python3
# Copyright 2022, The Khronos Group Inc.
#
# SPDX-License-Identifier: Apache-2.0

from openxr_inventory.extensions import generate_report, generate_runtime_report, generate_client_report
from openxr_inventory.runtime_inventory import load_all_runtimes
from openxr_inventory.client_inventory import load_all_clients

if __name__ == "__main__":
    runtimes = load_all_runtimes()
    clients = load_all_clients()
    generate_runtime_report(runtimes, clients)
    generate_client_report(runtimes, clients)
