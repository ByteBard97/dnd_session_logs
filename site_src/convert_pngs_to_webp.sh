#!/bin/bash
#
# Convert all PNG files to WebP format using ImageMagick
# Usage: ./convert_pngs_to_webp.sh [directory] [quality]
#

set -e  # Exit on any error

# Configuration
DEFAULT_DIR="/home/geoff/projects/native-plant-planner-mockup/generated_assets/"
DEFAULT_QUALITY=85

# Get directory from argument or use default
INPUT_DIR="${1:-$DEFAULT_DIR}"
QUALITY="${2:-$DEFAULT_QUALITY}"
WEBP_OPTIONS="-quality $QUALITY -define webp:lossless=false"

# Check if directory exists
if [[ ! -d "$INPUT_DIR" ]]; then
    echo "❌ Directory not found: $INPUT_DIR"
    exit 1
fi

# Check if ImageMagick is available
if ! command -v convert &> /dev/null; then
    echo "❌ ImageMagick 'convert' command not found!"
    echo "   Install with: sudo apt-get install imagemagick"
    exit 1
fi

# Find all PNG files
PNG_FILES=($(find "$INPUT_DIR" -name "*.png" -type f))
TOTAL_COUNT=${#PNG_FILES[@]}

if [[ $TOTAL_COUNT -eq 0 ]]; then
    echo "ℹ️  No PNG files found in: $INPUT_DIR"
    exit 0
fi

echo "🔄 Converting $TOTAL_COUNT PNG files to WebP..."
echo "📁 Directory: $INPUT_DIR"
echo "⚙️  Quality: $QUALITY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Track statistics
CONVERTED=0
SKIPPED=0
FAILED=0
TOTAL_SIZE_BEFORE=0
TOTAL_SIZE_AFTER=0

for PNG_FILE in "${PNG_FILES[@]}"; do
    # Get file info
    BASENAME=$(basename "$PNG_FILE" .png)
    WEBP_FILE="${PNG_FILE%.png}.webp"
    
    # Skip if WebP already exists and is newer
    if [[ -f "$WEBP_FILE" ]] && [[ "$WEBP_FILE" -nt "$PNG_FILE" ]]; then
        echo "⏭️  Skipping $BASENAME (WebP exists and is newer)"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi
    
    # Get original file size
    if [[ -f "$PNG_FILE" ]]; then
        PNG_SIZE=$(stat -c%s "$PNG_FILE")
        TOTAL_SIZE_BEFORE=$((TOTAL_SIZE_BEFORE + PNG_SIZE))
    else
        PNG_SIZE=0
    fi
    
    # Convert PNG to WebP
    echo -n "🔄 Converting $BASENAME..."
    
    if convert "$PNG_FILE" $WEBP_OPTIONS "$WEBP_FILE" 2>/dev/null; then
        # Get new file size
        WEBP_SIZE=$(stat -c%s "$WEBP_FILE")
        TOTAL_SIZE_AFTER=$((TOTAL_SIZE_AFTER + WEBP_SIZE))
        
        # Calculate compression ratio
        if [[ $PNG_SIZE -gt 0 ]]; then
            COMPRESSION_RATIO=$((100 - (WEBP_SIZE * 100 / PNG_SIZE)))
            SIZE_MB=$(echo "scale=1; $PNG_SIZE / 1048576" | bc -l 2>/dev/null || echo "0")
            NEW_SIZE_MB=$(echo "scale=1; $WEBP_SIZE / 1048576" | bc -l 2>/dev/null || echo "0")
            echo " ✅ ${SIZE_MB}MB → ${NEW_SIZE_MB}MB (-${COMPRESSION_RATIO}%)"
        else
            echo " ✅ Converted"
        fi
        
        CONVERTED=$((CONVERTED + 1))
    else
        echo " ❌ FAILED"
        FAILED=$((FAILED + 1))
        
        # Remove failed WebP file
        [[ -f "$WEBP_FILE" ]] && rm -f "$WEBP_FILE"
    fi
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Conversion Summary:"
echo "   ✅ Converted: $CONVERTED files"
echo "   ⏭️  Skipped:   $SKIPPED files" 
echo "   ❌ Failed:    $FAILED files"
echo "   📁 Total:     $TOTAL_COUNT files"

# Show size savings if we have valid numbers
if [[ $TOTAL_SIZE_BEFORE -gt 0 ]] && [[ $TOTAL_SIZE_AFTER -gt 0 ]]; then
    TOTAL_SAVINGS=$((TOTAL_SIZE_BEFORE - TOTAL_SIZE_AFTER))
    TOTAL_COMPRESSION=$((100 - (TOTAL_SIZE_AFTER * 100 / TOTAL_SIZE_BEFORE)))
    
    SIZE_BEFORE_MB=$(echo "scale=1; $TOTAL_SIZE_BEFORE / 1048576" | bc -l 2>/dev/null || echo "0")
    SIZE_AFTER_MB=$(echo "scale=1; $TOTAL_SIZE_AFTER / 1048576" | bc -l 2>/dev/null || echo "0")
    SAVINGS_MB=$(echo "scale=1; $TOTAL_SAVINGS / 1048576" | bc -l 2>/dev/null || echo "0")
    
    echo ""
    echo "💾 Size Reduction:"
    echo "   Before: ${SIZE_BEFORE_MB} MB"
    echo "   After:  ${SIZE_AFTER_MB} MB" 
    echo "   Saved:  ${SAVINGS_MB} MB (-${TOTAL_COMPRESSION}%)"
fi

echo ""
if [[ $FAILED -eq 0 ]]; then
    echo "🎉 All conversions completed successfully!"
else
    echo "⚠️  Some conversions failed. Check ImageMagick installation and file permissions."
fi

# Optional: Remove original PNGs (commented out for safety)
# echo ""
# read -p "🗑️  Remove original PNG files? (y/N): " -n 1 -r
# echo
# if [[ $REPLY =~ ^[Yy]$ ]]; then
#     for PNG_FILE in "${PNG_FILES[@]}"; do
#         WEBP_FILE="${PNG_FILE%.png}.webp"
#         if [[ -f "$WEBP_FILE" ]]; then
#             rm "$PNG_FILE"
#             echo "🗑️  Removed: $(basename "$PNG_FILE")"
#         fi
#     done
#     echo "✅ Original PNG files removed"
# fi
