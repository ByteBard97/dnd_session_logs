#!/bin/bash

# This script builds the LaTeX flyer PDF for the Odyssey of the Dragonlords campaign.
# It compiles the document using lualatex.

echo "--- Starting OODL Flyer Build ---"

# Change to the flyer directory
cd "$(dirname "$0")"

# Compile the LaTeX document using lualatex
# The -output-directory flag tells lualatex where to put the generated files.
echo "Compiling oodl_flyer.tex..."
lualatex -jobname=oodl_flyer oodl_flyer.tex

# Check for the output file and report status
if [ -f "oodl_flyer.pdf" ]; then
  echo "SUCCESS: oodl_flyer.pdf has been created successfully."
  echo "Converting PDF to JPG..."
  pdftoppm -jpeg oodl_flyer.pdf oodl_flyer-image
else
  echo "FAILURE: Could not create oodl_flyer.pdf. Please check the logs above for errors."
  exit 1
fi

echo "--- Build Process Complete ---" 