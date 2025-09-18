#!/bin/bash

# Dragon PNG to SVG Converter Script
# Provides multiple conversion methods for best results

echo "Dragon PNG to SVG Converter"
echo "=========================="
echo ""

# Check for required tools
check_tools() {
    local has_tools=false

    if command -v potrace &> /dev/null; then
        echo "✓ Potrace found"
        has_tools=true
    else
        echo "✗ Potrace not found (install with: sudo apt-get install potrace)"
    fi

    if command -v vtracer &> /dev/null; then
        echo "✓ VTracer found"
        has_tools=true
    else
        echo "✗ VTracer not found (install with: cargo install vtracer)"
    fi

    if command -v convert &> /dev/null; then
        echo "✓ ImageMagick found"
    else
        echo "✗ ImageMagick not found (install with: sudo apt-get install imagemagick)"
        has_tools=false
    fi

    echo ""

    if [ "$has_tools" = false ]; then
        echo "Please install required tools first."
        echo ""
        echo "Recommended installation:"
        echo "  # For potrace (basic, free):"
        echo "  sudo apt-get install potrace imagemagick"
        echo ""
        echo "  # For vtracer (better quality):"
        echo "  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
        echo "  cargo install vtracer"
        echo ""
        echo "  # Or use web services:"
        echo "  - https://vectorizer.ai (AI-powered, best quality)"
        echo "  - https://svgcode.app (free web app)"
        echo "  - https://www.autotracer.org (free online)"
        exit 1
    fi
}

# Method 1: Using Potrace (black & white)
convert_with_potrace() {
    local input=$1
    local output="${input%.png}_potrace.svg"

    echo "Converting $input with Potrace (B&W)..."

    # Convert to PBM and then to SVG
    # Adjust threshold for better results (0-100, lower = more black)
    convert "$input" -resize 512x512 -threshold 50% -negate temp.pbm
    potrace temp.pbm -s -o "$output" --turdsize 10 --alphamax 1.0
    rm temp.pbm

    echo "  Created: $output"
}

# Method 2: Using Potrace with color quantization
convert_with_potrace_color() {
    local input=$1
    local output="${input%.png}_potrace_color.svg"

    echo "Converting $input with Potrace (Color layers)..."

    # Reduce colors first for simpler output
    convert "$input" -resize 512x512 -colors 8 -posterize 4 temp_color.png

    # Create multiple layers for different colors
    # This is a simplified version - full implementation would extract each color
    convert temp_color.png -threshold 30% -negate temp1.pbm
    potrace temp1.pbm -s -o temp1.svg --turdsize 10

    convert temp_color.png -threshold 60% -negate temp2.pbm
    potrace temp2.pbm -s -o temp2.svg --turdsize 10

    # Combine SVGs (simplified - would need proper SVG manipulation)
    echo '<?xml version="1.0" standalone="no"?>' > "$output"
    echo '<svg xmlns="http://www.w3.org/2000/svg">' >> "$output"
    cat temp1.svg | grep -v '<?xml' | grep -v '<svg' | grep -v '</svg>' >> "$output"
    cat temp2.svg | grep -v '<?xml' | grep -v '<svg' | grep -v '</svg>' >> "$output"
    echo '</svg>' >> "$output"

    rm temp_color.png temp*.pbm temp*.svg 2>/dev/null

    echo "  Created: $output"
}

# Method 3: Using VTracer (if available)
convert_with_vtracer() {
    local input=$1
    local output="${input%.png}_vtracer.svg"

    if command -v vtracer &> /dev/null; then
        echo "Converting $input with VTracer (Best quality)..."

        # VTracer options:
        # --colormode: color (default), binary, grayscale
        # --hierarchical: stacked (default), cutout
        # --filter_speckle: remove small specs (default: 4)
        # --color_precision: 1-8, lower = simpler (default: 6)
        # --corner_threshold: higher = more corners (default: 60)

        vtracer --input "$input" \
                --output "$output" \
                --colormode color \
                --color_precision 4 \
                --filter_speckle 10 \
                --gradient_step 20 \
                --corner_threshold 60

        echo "  Created: $output"
    else
        echo "VTracer not installed, skipping..."
    fi
}

# Optimize SVG size
optimize_svg() {
    local svg=$1

    if command -v svgo &> /dev/null; then
        echo "  Optimizing $svg with SVGO..."
        svgo "$svg" -o "${svg%.svg}_optimized.svg"
    else
        echo "  SVGO not found (install with: npm install -g svgo)"
    fi
}

# Main conversion process
main() {
    check_tools

    echo "Select conversion method:"
    echo "1) Potrace (B&W, smallest files)"
    echo "2) Potrace (Color layers, medium complexity)"
    echo "3) VTracer (Best quality, color support)"
    echo "4) All methods (compare results)"
    echo ""
    read -p "Choice (1-4): " choice

    for png in dragons0*.png; do
        if [ -f "$png" ]; then
            echo ""
            echo "Processing: $png"
            echo "-------------------"

            case $choice in
                1)
                    convert_with_potrace "$png"
                    ;;
                2)
                    convert_with_potrace_color "$png"
                    ;;
                3)
                    convert_with_vtracer "$png"
                    ;;
                4)
                    convert_with_potrace "$png"
                    convert_with_potrace_color "$png"
                    convert_with_vtracer "$png"
                    ;;
                *)
                    echo "Invalid choice"
                    exit 1
                    ;;
            esac
        fi
    done

    echo ""
    echo "Conversion complete!"
    echo ""
    echo "File sizes:"
    ls -lh dragons*.svg 2>/dev/null

    echo ""
    echo "For best results, consider:"
    echo "- Using online AI services like vectorizer.ai for complex images"
    echo "- Installing SVGO for file size optimization: npm install -g svgo"
    echo "- Adjusting threshold and color settings in the script"
}

# Run main function
main