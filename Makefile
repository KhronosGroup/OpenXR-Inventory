#!/usr/bin/env make -f
# Copyright 2022, The Khronos Group Inc.
#
# SPDX-License-Identifier: Apache-2.0

HTML_REPORT_FILES := public/extension_support.html
SHARED_DEPS := $(wildcard openxr_inventory/*.py) \
               $(wildcard runtimes/*.json) \
               openxr_inventory/templates/base.jinja2.html


all: $(HTML_REPORT_FILES)
.PHONY: all

public:
	mkdir -p $@

$(HTML_REPORT_FILES): public/%.html : %_report.py openxr_inventory/templates/%.jinja2.html public $(SHARED_DEPS)
	python3 $<
