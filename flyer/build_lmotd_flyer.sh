#!/bin/bash

# This script builds the LaTeX flyer PDF for the Lost Mine of the Drow campaign.
# It compiles the document using lualatex.

echo "--- Starting LMOTD Flyer Build ---"

# Change to the flyer directory
cd "$(dirname "$0")/lmotd_files"

# Compile the LaTeX document using lualatex
echo "Compiling lmotd_flyer.tex..."
lualatex -jobname=lmotd_flyer lmotd_flyer.tex

# Check for the output file and report status
if [ -f "lmotd_flyer.pdf" ]; then
  echo "SUCCESS: lmotd_flyer.pdf has been created successfully."
  echo "Converting PDF to JPG..."
  pdftoppm -jpeg -r 300 lmotd_flyer.pdf lmotd_flyer-image
else
  echo "FAILURE: Could not create lmotd_flyer.pdf. Please check the logs above for errors."
  exit 1
fi

echo "--- Build Process Complete ---" 