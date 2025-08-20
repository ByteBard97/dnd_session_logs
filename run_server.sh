#!/bin/bash
echo "Activating conda environment: dnd_docs"
source $(conda info --base)/etc/profile.d/conda.sh
conda activate dnd_docs

#echo "Running navigation updater..."
#python3 navigation_updater.py

echo "Starting MkDocs server..."
python -m mkdocs serve
