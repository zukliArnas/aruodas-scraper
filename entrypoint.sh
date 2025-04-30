#!/bin/sh

# Run script through xvfb for headful mode support
xvfb-run --auto-servernum python -u aruodas_scraper.py "$@"
