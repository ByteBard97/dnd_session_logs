#!/usr/bin/env python3
"""
Dragon PNG to SVG converter - High Quality version
Target: ~125KB per SVG with maximum quality
"""
from pathlib import Path
from PIL import Image
import vtracer
from lxml import etree
import numpy as np
import json
import re

def preprocess_dragon_png(in_path: Path, out_path: Path):
    """
    High quality preprocessing for ~125KB target:
    - Larger size: 640px for better detail
    - More colors: 24 for rich color palette
    - Minimal transparency removal (only pure white)
    """
    img = Image.open(in_path).convert("RGBA")

    # Larger size for more detail
    target_size = 640
    img.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)

    # Convert to numpy for processing
    arr = np.array(img)
    r, g, b, a = arr[...,0], arr[...,1], arr[...,2], arr[...,3]

    # Only remove pure white pixels (threshold 253)
    mask_white = (r >= 253) & (g >= 253) & (b >= 253)
    arr[...,3] = np.where(mask_white, 0, a)

    # Convert back to PIL
    img2 = Image.fromarray(arr, mode="RGBA")

    # High color count for rich detail
    img2 = img2.quantize(colors=24, dither=Image.Dither.FLOYDSTEINBERG).convert("RGBA")

    img2.save(out_path)
    return img2.size

def vectorize_dragon_highquality(png_file: Path, out_svg: Path):
    """Run VTracer with high quality settings for ~125KB target"""
    vtracer.convert_image_to_svg_py(
        str(png_file),
        str(out_svg),
        colormode='color',          # Full color
        hierarchical='stacked',     # Proper layering
        mode='spline',              # Smooth curves
        filter_speckle=2,           # Keep most detail (minimal filtering)
        color_precision=6,          # High color precision (default/max)
        layer_difference=8,         # Less aggressive merging
        corner_threshold=40,        # More corners for accurate shapes
        length_threshold=2.0,       # Keep smaller segments
        path_precision=3            # Maximum path precision
    )

def optimize_svg_minimal(svg_path: Path):
    """Minimal optimization to preserve quality"""
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(str(svg_path), parser)
    root = tree.getroot()

    if not root.tag.endswith('svg'):
        return

    # Remove width/height, keep viewBox only
    root.attrib.pop('width', None)
    root.attrib.pop('height', None)

    # Only remove obvious white background rectangles
    for node in list(root.iter()):
        tag = etree.QName(node).localname
        if tag == 'rect':
            fill = (node.attrib.get('fill') or '').strip().lower()
            if fill in ('#fff', '#ffffff', 'white'):
                # Check if it's a full-canvas rect
                try:
                    x = float(node.attrib.get('x', '0') or 0)
                    y = float(node.attrib.get('y', '0') or 0)
                    if abs(x) < 1 and abs(y) < 1:
                        parent = node.getparent()
                        if parent is not None:
                            parent.remove(node)
                except ValueError:
                    pass

    # Add descriptive title
    title_el = etree.Element('title')
    title_el.text = f"Dragon {svg_path.stem} (High Quality)"
    root.insert(0, title_el)

    # Add metadata
    meta = etree.Element('metadata')
    meta.text = json.dumps({
        "type": "dragon",
        "quality": "high",
        "target_size": "125KB",
        "colors": 24,
        "resolution": "640px"
    })
    root.insert(1, meta)

    # Write with pretty print for readability
    tree.write(str(svg_path), pretty_print=True, xml_declaration=True, encoding='utf-8')

def process_dragons_highquality():
    """Process dragon PNGs with high quality settings for ~125KB target"""
    dragon_files = sorted(Path('.').glob('dragons*.png'))

    if not dragon_files:
        print("No dragon files found!")
        return

    print(f"Found {len(dragon_files)} dragon images")
    print("Using HIGH QUALITY settings targeting ~125KB per file")
    print("Settings: 640px, 24 colors, maximum precision")
    print("-" * 50)

    # Create output directory
    out_dir = Path('dragon_svgs_highquality')
    out_dir.mkdir(exist_ok=True)

    # Create temp directory for preprocessed PNGs
    tmp_dir = Path('tmp_dragons')
    tmp_dir.mkdir(exist_ok=True)

    results = []

    for dragon_png in dragon_files:
        print(f"\nProcessing: {dragon_png.name}")

        # Get original size
        orig_size = dragon_png.stat().st_size
        print(f"  Original PNG: {orig_size / 1024:.1f} KB")

        # Preprocess PNG with high quality settings
        tmp_png = tmp_dir / f"{dragon_png.stem}_processed.png"
        new_size = preprocess_dragon_png(dragon_png, tmp_png)
        print(f"  Preprocessed to: {new_size[0]}x{new_size[1]} px with 24 colors")

        # Convert to SVG with high quality settings
        out_svg = out_dir / f"{dragon_png.stem}.svg"
        print("  Converting with maximum quality settings...")
        vectorize_dragon_highquality(tmp_png, out_svg)

        # Minimal optimization
        optimize_svg_minimal(out_svg)

        # Check final size
        svg_size = out_svg.stat().st_size
        print(f"  Final SVG: {svg_size / 1024:.1f} KB")

        # Quality assessment
        if svg_size < 80_000:
            quality = "Good quality"
            recommendation = "Could increase colors/resolution"
        elif svg_size < 125_000:
            quality = "Excellent quality"
            recommendation = "Perfect balance"
        elif svg_size < 150_000:
            quality = "Premium quality"
            recommendation = "Slightly over target"
        else:
            quality = "Maximum quality"
            recommendation = "Consider reducing if needed"

        print(f"  Quality: {quality} - {recommendation}")
        print(f"  Reduction: {(1 - svg_size/orig_size) * 100:.1f}%")

        results.append({
            'file': dragon_png.name,
            'original_kb': round(orig_size / 1024, 1),
            'svg_kb': round(svg_size / 1024, 1),
            'quality': quality,
            'recommendation': recommendation,
            'reduction_pct': round((1 - svg_size/orig_size) * 100, 1)
        })

    # Clean up temp files
    import shutil
    shutil.rmtree(tmp_dir)

    # Print summary
    print("\n" + "=" * 50)
    print("CONVERSION SUMMARY - HIGH QUALITY")
    print("=" * 50)
    total_orig = sum(r['original_kb'] for r in results)
    total_svg = sum(r['svg_kb'] for r in results)

    for r in results:
        print(f"{r['file']:20} {r['original_kb']:7.1f} KB -> {r['svg_kb']:6.1f} KB")
        print(f"  └─ {r['quality']:20} ({r['recommendation']})")

    print("-" * 50)
    print(f"{'TOTAL':20} {total_orig:7.1f} KB -> {total_svg:6.1f} KB ({(1-total_svg/total_orig)*100:5.1f}% smaller)")
    print(f"\nTarget: ~125KB per file")
    avg_size = total_svg / len(results)
    print(f"Average size achieved: {avg_size:.1f} KB")

    if avg_size < 100:
        print("\n💡 To get closer to 125KB target, you could try:")
        print("  - Increase resolution to 768px or 800px")
        print("  - Use 32 colors instead of 24")
        print("  - Set filter_speckle to 1 (keep all detail)")
        print("  - Set corner_threshold to 30 (more accurate corners)")
    elif avg_size > 150:
        print("\n💡 To reduce file size, you could try:")
        print("  - Reduce to 20 colors")
        print("  - Set color_precision to 5")
        print("  - Increase filter_speckle to 3")

    print(f"\nAll high quality SVGs saved to: {out_dir}/")
    print("\nRun compare_dragon_quality.py to see visual comparisons")

if __name__ == "__main__":
    process_dragons_highquality()