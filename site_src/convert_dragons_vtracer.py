#!/usr/bin/env python3
"""
Dragon PNG to SVG converter using VTracer with aggressive optimization
Goal: Get SVG files under 100KB each from ~1.2MB PNGs
"""
from pathlib import Path
from PIL import Image
import vtracer
from lxml import etree
import numpy as np
import json
import re

# Dragon-specific aggressive settings for minimal file size
def preprocess_dragon_png(in_path: Path, out_path: Path):
    """
    Aggressively simplify PNG for tiny SVG output:
    - Resize to very small size (128px)
    - Use only 2-3 colors
    - Remove white/near-white backgrounds
    """
    img = Image.open(in_path).convert("RGBA")

    # Aggressive resize - dragons will still be recognizable at 128px
    target_size = 128
    img.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)

    # Convert to numpy for processing
    arr = np.array(img)
    r, g, b, a = arr[...,0], arr[...,1], arr[...,2], arr[...,3]

    # Make white/light pixels transparent (threshold 230)
    mask_white = (r >= 230) & (g >= 230) & (b >= 230)
    arr[...,3] = np.where(mask_white, 0, a)

    # Convert back to PIL
    img2 = Image.fromarray(arr, mode="RGBA")

    # Extreme quantization - just 2 colors for minimal SVG complexity
    img2 = img2.quantize(colors=2, dither=Image.Dither.NONE).convert("RGBA")

    img2.save(out_path)
    return img2.size

def vectorize_dragon(png_file: Path, out_svg: Path):
    """Run VTracer with EXTREME simplification for tiny SVGs"""
    vtracer.convert_image_to_svg_py(
        str(png_file),
        str(out_svg),
        colormode='binary',         # Just black & white for smallest files
        hierarchical='stacked',
        mode='polygon',             # Polygons instead of splines (smaller)
        filter_speckle=32,          # Remove ALL small details
        color_precision=1,          # Minimum color precision
        layer_difference=64,        # Maximum merging
        corner_threshold=180,       # Super smooth, minimal points
        length_threshold=20.0,      # Drop all small segments
        path_precision=1            # Minimum precision
    )

def optimize_svg(svg_path: Path):
    """Remove unnecessary elements and optimize SVG structure"""
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(str(svg_path), parser)
    root = tree.getroot()

    if not root.tag.endswith('svg'):
        return

    # Remove width/height, keep viewBox only
    root.attrib.pop('width', None)
    root.attrib.pop('height', None)

    # Remove white backgrounds
    for node in list(root.iter()):
        tag = etree.QName(node).localname
        fill = (node.attrib.get('fill') or '').strip().lower()
        if not fill:
            style = node.attrib.get('style') or ''
            m = re.search(r'fill\s*:\s*([^;]+)', style, re.I)
            fill = (m.group(1).strip().lower() if m else '')

        # Remove white/light elements
        if fill in ('#fff','#ffffff','#fefefe','#fdfdfd','rgb(255,255,255)','white'):
            parent = node.getparent()
            if parent is not None:
                parent.remove(node)

    # Add title
    title = f"Dragon {svg_path.stem}"
    title_el = etree.Element('title')
    title_el.text = title
    root.insert(0, title_el)

    # Write optimized SVG
    tree.write(str(svg_path), pretty_print=False, xml_declaration=True, encoding='utf-8')

def process_dragons():
    """Process all dragon PNGs with aggressive optimization"""
    dragon_files = sorted(Path('.').glob('dragons*.png'))

    if not dragon_files:
        print("No dragon files found!")
        return

    print(f"Found {len(dragon_files)} dragon images")
    print("Using EXTREME optimization for minimal file sizes")
    print("-" * 50)

    # Create output directory
    out_dir = Path('dragon_svgs')
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

        # Preprocess PNG
        tmp_png = tmp_dir / f"{dragon_png.stem}_processed.png"
        new_size = preprocess_dragon_png(dragon_png, tmp_png)
        print(f"  Preprocessed to: {new_size[0]}x{new_size[1]} px")

        # Convert to SVG
        out_svg = out_dir / f"{dragon_png.stem}.svg"
        vectorize_dragon(tmp_png, out_svg)

        # Optimize SVG
        optimize_svg(out_svg)

        # Check final size
        svg_size = out_svg.stat().st_size
        print(f"  Final SVG: {svg_size / 1024:.1f} KB")
        print(f"  Reduction: {(1 - svg_size/orig_size) * 100:.1f}%")

        results.append({
            'file': dragon_png.name,
            'original_kb': round(orig_size / 1024, 1),
            'svg_kb': round(svg_size / 1024, 1),
            'reduction_pct': round((1 - svg_size/orig_size) * 100, 1)
        })

    # Clean up temp files
    import shutil
    shutil.rmtree(tmp_dir)

    # Print summary
    print("\n" + "=" * 50)
    print("CONVERSION SUMMARY")
    print("=" * 50)
    total_orig = sum(r['original_kb'] for r in results)
    total_svg = sum(r['svg_kb'] for r in results)

    for r in results:
        print(f"{r['file']:20} {r['original_kb']:7.1f} KB -> {r['svg_kb']:6.1f} KB ({r['reduction_pct']:5.1f}% smaller)")

    print("-" * 50)
    print(f"{'TOTAL':20} {total_orig:7.1f} KB -> {total_svg:6.1f} KB ({(1-total_svg/total_orig)*100:5.1f}% smaller)")
    print(f"\nAll SVGs saved to: {out_dir}")

    # Try even more aggressive settings if files are still too large
    if any(r['svg_kb'] > 100 for r in results):
        print("\n⚠️  Some files are still over 100KB. Consider:")
        print("  - Using an online service like vectorizer.ai")
        print("  - Further reducing the preprocessing size (currently 128px)")
        print("  - Using just 1 color instead of 2")

if __name__ == "__main__":
    process_dragons()