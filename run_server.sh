#!/bin/bash
echo "Activating conda environment: dnd_docs"
source $(conda info --base)/etc/profile.d/conda.sh
conda activate dnd_docs
echo "Starting MkDocs server..."
python -m mkdocs serve
