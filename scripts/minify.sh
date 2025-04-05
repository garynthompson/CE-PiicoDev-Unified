#!/bin/bash

# To be manually called for minification
# Assumes uv for packaging and calling from root project folder.

uv run pyminify \
 --remove-literal-statements \
 PiicoDev_Unified/__init__.py > min/PiicoDev_Unified.py

uv run pyminify \
 --remove-literal-statements \
 --remove-unused-platforms \
 --platform-test-key "_PLATFORM_BUILD" \
 --platform-preserve-value "microbit" \
 PiicoDev_Unified/__init__.py > min/PiicoDev_Unified_microbit.py

uv run pyminify \
 --remove-literal-statements \
 --remove-unused-platforms \
 --platform-test-key "_PLATFORM_BUILD" \
 --platform-preserve-value "micropython" \
 PiicoDev_Unified/__init__.py > min/PiicoDev_Unified_micropython.py

