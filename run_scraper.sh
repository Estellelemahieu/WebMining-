#!/usr/bin/env bash
set -euo pipefail

# Helper script to set up a virtual environment, install dependencies, run the scraper,
# and print a short preview of the output CSV.

# Create and activate venv
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

# Upgrade pip and install packages
python -m pip install --upgrade pip
pip install requests beautifulsoup4 pandas

# Run the scraper (full run that writes books.csv)
python3 "Assignment 1/book_scraper.py"

# Show a preview of the generated CSV
if [ -f books.csv ]; then
  echo "\nPreview (first 12 lines of books.csv):"
  head -n 12 books.csv || true
else
  echo "books.csv not found. If the script failed, try running with --test to see parsing output."
fi
