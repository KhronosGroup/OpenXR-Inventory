#!/usr/bin/env make -f
# Copyright 2022, The Khronos Group Inc.
#
# SPDX-License-Identifier: Apache-2.0

HTML_REPORT_FILES := public/runtime_extension_support.html public/client_extension_support.html public/extension_support.html
SHARED_DEPS := $(wildcard openxr_inventory/*.py) \
               $(wildcard runtimes/*.json) \
               $(wildcard clients/*.json) \
               openxr_inventory/templates/base.jinja2.html \
               openxr_inventory/templates/runtime_extension_support.jinja2.html \
               openxr_inventory/templates/client_extension_support.jinja2.html


all: $(HTML_REPORT_FILES)
.PHONY: all

public:
	mkdir -p $@

public/runtime_extension_support.html: extension_support_report.py public $(SHARED_DEPS)
	python3 $<

public/client_extension_support.html: extension_support_report.py public $(SHARED_DEPS)
	python3 $<

public/extension_support.html: openxr_inventory/templates/extension_support.html public
	cp $< $@
