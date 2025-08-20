#!/bin/bash

# D&D Image to WebP Converter
# Converts all non-WebP images to WebP format while preserving alpha channels
# Skips existing WebP files and handles filename conflicts

# Check if ImageMagick is installed and determine command
MAGICK_CMD=""
if command -v magick &> /dev/null; then
    MAGICK_CMD="magick"
elif command -v convert &> /dev/null; then
    MAGICK_CMD="convert"
else
    echo "Error: ImageMagick is not installed."
    echo "Install it with: sudo apt install imagemagick"
    exit 1
fi

echo "Using ImageMagick command: $MAGICK_CMD"

# Set the directory to process (current directory by default)
DIRECTORY="${1:-.}"

# Supported input formats
EXTENSIONS=("jpg" "jpeg" "png" "gif" "bmp" "tiff" "tif" "svg" "ico")

# Function to get unique filename if conflict exists
get_unique_filename() {
    local base_name="$1"
    local extension="$2"
    local counter=1
    local new_name="${base_name}.${extension}"
    
    while [[ -f "$new_name" ]]; do
        new_name="${base_name}_$(printf "%02d" $counter).${extension}"
        ((counter++))
    done
    
    echo "$new_name"
}

# Counter for processed files
converted_count=0
skipped_count=0
total_files=0

echo "Starting image conversion to WebP format..."
echo "Processing directory: $(realpath "$DIRECTORY")"
echo

# Process each supported file extension
for ext in "${EXTENSIONS[@]}"; do
    # Find files with current extension (case insensitive)
    while IFS= read -r -d '' file; do
        ((total_files++))
        
        # Get filename without extension
        basename=$(basename "$file")
        filename="${basename%.*}"
        directory=$(dirname "$file")
        
        # Skip if already WebP
        if [[ "${basename,,}" == *.webp ]]; then
            echo "Skipping (already WebP): $basename"
            ((skipped_count++))
            continue
        fi
        
        # Determine output filename
        output_base="$directory/$filename"
        output_file=$(get_unique_filename "$output_base" "webp")
        
        echo -n "Converting: $basename -> $(basename "$output_file")... "
        
        # Convert to WebP with ImageMagick
        # -quality 85: Good balance of quality and file size
        # -define webp:alpha-quality=100: Preserve alpha channel quality for tokens
        if $MAGICK_CMD "$file" -quality 85 -define webp:alpha-quality=100 "$output_file" 2>/dev/null; then
            echo "✓ Done"
            ((converted_count++))
        else
            echo "✗ Failed"
        fi
        
    done < <(find "$DIRECTORY" -maxdepth 1 -type f -iname "*.${ext}" -print0)
done

# Also check for WebP files to count them as skipped
while IFS= read -r -d '' file; do
    ((total_files++))
    ((skipped_count++))
done < <(find "$DIRECTORY" -maxdepth 1 -type f -iname "*.webp" -print0)

echo
echo "Conversion complete!"
echo "Total files found: $total_files"
echo "Files converted: $converted_count"
echo "Files skipped: $skipped_count"

if [[ $converted_count -gt 0 ]]; then
    echo
    echo "Note: Original files were preserved. You can delete them manually if desired."
fi