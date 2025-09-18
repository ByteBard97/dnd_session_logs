#!/bin/bash
echo "Activating conda environment: dnd_docs"
source $(conda info --base)/etc/profile.d/conda.sh
conda activate dnd_docs

#echo "Running navigation updater..."
#python3 navigation_updater.py

echo "Building site..."
python -m mkdocs build --clean

echo "Copying additional assets and HTML files..."

# Create assets directory if it doesn't exist
mkdir -p docs/assets

# Copy WEBP dragon images to docs/assets
echo "  Copying dragon WEBP files..."
cp site_src/assets/dragons*.webp docs/assets/ 2>/dev/null || echo "    Warning: No dragon WEBP files found in site_src/assets/"

# Copy HTML utility apps to docs root
echo "  Copying HTML utility apps..."
cp site_src/thylean-fishing-app.html docs/ 2>/dev/null || echo "    Warning: thylean-fishing-app.html not found"
cp site_src/dnd-los-calculato.html docs/ 2>/dev/null || echo "    Warning: dnd-los-calculato.html not found"

echo "Additional files copied successfully!"
