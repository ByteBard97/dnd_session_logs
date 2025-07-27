#!/bin/bash

# This script builds the LaTeX flyer PDF.
# It navigates to the correct directory, cleans up old files,
# and compiles the document using lualatex.

echo "--- Starting Flyer Build ---"

# Navigate to the flyer directory from the script's location
#cd "$(dirname "$0")/flyer" || { echo "Error: Could not find the 'flyer' directory."; exit 1; }

#echo "Changed directory to: $(pwd)"

# Clean up old build files to ensure a fresh compilation
#echo "Cleaning up old auxiliary files (flyer.aux, flyer.log)..."
#rm -f flyer.aux flyer.log

# Compile the LaTeX document using lualatex
echo "Compiling flyer.tex..."
lualatex lmotd_flyer.tex
pdftoppm -png lmotd_flyer.pdf lmotd_flyer-image

# Check for the output file and report status
if [ -f "lmotd_flyer.pdf" ]; then
  echo "SUCCESS: lmotd_flyer.pdf has been created successfully."
else
  echo "FAILURE: Could not create lmotd_flyer.pdf. Please check the logs above for errors."
  exit 1
fi

echo "--- Build Process Complete ---" 