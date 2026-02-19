#!/bin/bash

# OSINT Eye - Example Usage Script

echo "=== OSINT Eye Example Usage ==="
echo

# Set up environment
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

echo "1. Fetching Instagram data for natgeo (5 posts)..."
python src/main.py fetch --platform instagram --username natgeo --max 5

echo
echo "2. Analyzing the fetched data..."
python src/main.py analyze --platform instagram --username natgeo

echo
echo "3. Generating HTML report..."
python src/main.py report --platform instagram --username natgeo --format html

echo
echo "4. Fetching Twitter data for nasa (5 tweets)..."
python src/main.py fetch --platform twitter --username nasa --max 5

echo
echo "5. Analyzing Twitter data..."
python src/main.py analyze --platform twitter --username nasa

echo
echo "6. Generating Markdown report for Twitter..."
python src/main.py report --platform twitter --username nasa --format markdown

echo
echo "=== Example completed! Check the data/ and reports/ directories ==="