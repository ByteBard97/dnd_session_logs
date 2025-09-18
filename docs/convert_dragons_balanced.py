#!/usr/bin/env python3
"""
Dragon PNG to SVG converter - Balanced quality version
Target: ~125KB per SVG (1/8 MB) with good visual quality
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
    Balanced preprocessing for good quality at reasonable size:
    - Resize to 512px (good detail retention)
    - Use 8-16 colors for decent color fidelity
    - Remove pure white backgrounds
    """
    img = Image.open(in_path).convert("RGBA")

    # Moderate resize - 512px preserves good detail
    target_size = 512
    img.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)

    # Convert to numpy for processing
    arr = np.array(img)
    r, g, b, a = arr[...,0], arr[...,1], arr[...,2], arr[...,3]

    # Make pure white pixels transparent (threshold 250 - only very white)
    mask_white = (r >= 250) & (g >= 250) & (b >= 250)
    arr[...,3] = np.where(mask_white, 0, a)

    # Convert back to PIL
    img2 = Image.fromarray(arr, mode="RGBA")

    # Moderate quantization - 12 colors for good quality
    img2 = img2.quantize(colors=12, dither=Image.Dither.FLOYDSTEINBERG).convert("RGBA")

    img2.save(out_path)
    return img2.size

def vectorize_dragon_balanced(png_file: Path, out_svg: Path):
    """Run VTracer with balanced settings for good quality at ~125KB"""
    vtracer.convert_image_to_svg_py(
        str(png_file),
        str(out_svg),
        colormode='color',          # Full color for quality
        hierarchical='stacked',     # Proper layering
        mode='spline',              # Smooth curves
        filter_speckle=4,           # Keep some detail (default)
        color_precision=4,          # Moderate color precision (was 6 default)
        layer_difference=16,        # Default merging
        corner_threshold=60,        # Default corners for good shapes
        length_threshold=4.0,       # Default segment handling
        path_precision=2            # Slightly reduced precision (was 3)
    )

def optimize_svg_moderate(svg_path: Path):
    """Light optimization without destroying quality"""
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(str(svg_path), parser)
    root = tree.getroot()

    if not root.tag.endswith('svg'):
        return

    # Remove width/height, keep viewBox only
    root.attrib.pop('width', None)
    root.attrib.pop('height', None)

    # Only remove pure white backgrounds
    for node in list(root.iter()):
        tag = etree.QName(node).localname
        fill = (node.attrib.get('fill') or '').strip().lower()
        if not fill:
            style = node.attrib.get('style') or ''
            m = re.search(r'fill\s*:\s*([^;]+)', style, re.I)
            fill = (m.group(1).strip().lower() if m else '')

        # Only remove pure white
        if fill in ('#fff','#ffffff','white'):
            # Check if it's likely a background (first child or rect)
            parent = node.getparent()
            if parent is not None and (tag == 'rect' or list(parent).index(node) == 0):
                parent.remove(node)

    # Add descriptive title
    title_el = etree.Element('title')
    title_el.text = f"Dragon {svg_path.stem}"
    root.insert(0, title_el)

    # Add metadata
    meta = etree.Element('metadata')
    meta.text = json.dumps({
        "type": "dragon",
        "quality": "balanced",
        "target_size": "125KB"
    })
    root.insert(1, meta)

    # Write with pretty print for readability (adds some size but worth it)
    tree.write(str(svg_path), pretty_print=True, xml_declaration=True, encoding='utf-8')

def process_dragons_balanced():
    """Process dragon PNGs with balanced quality/size tradeoff"""
    dragon_files = sorted(Path('.').glob('dragons*.png'))

    if not dragon_files:
        print("No dragon files found!")
        return

    print(f"Found {len(dragon_files)} dragon images")
    print("Using BALANCED settings for ~125KB target with good quality")
    print("-" * 50)

    # Create output directory
    out_dir = Path('dragon_svgs_balanced')
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

        # Preprocess PNG with balanced settings
        tmp_png = tmp_dir / f"{dragon_png.stem}_processed.png"
        new_size = preprocess_dragon_png(dragon_png, tmp_png)
        print(f"  Preprocessed to: {new_size[0]}x{new_size[1]} px with 12 colors")

        # Convert to SVG with balanced settings
        out_svg = out_dir / f"{dragon_png.stem}.svg"
        vectorize_dragon_balanced(tmp_png, out_svg)

        # Light optimization
        optimize_svg_moderate(out_svg)

        # Check final size
        svg_size = out_svg.stat().st_size
        print(f"  Final SVG: {svg_size / 1024:.1f} KB")

        # Quality assessment
        if svg_size < 50_000:
            quality = "May be too simplified"
        elif svg_size < 100_000:
            quality = "Good balance"
        elif svg_size < 150_000:
            quality = "Excellent quality"
        else:
            quality = "Very detailed"
        print(f"  Quality: {quality}")
        print(f"  Reduction: {(1 - svg_size/orig_size) * 100:.1f}%")

        results.append({
            'file': dragon_png.name,
            'original_kb': round(orig_size / 1024, 1),
            'svg_kb': round(svg_size / 1024, 1),
            'quality': quality,
            'reduction_pct': round((1 - svg_size/orig_size) * 100, 1)
        })

    # Clean up temp files
    import shutil
    shutil.rmtree(tmp_dir)

    # Print summary
    print("\n" + "=" * 50)
    print("CONVERSION SUMMARY - BALANCED QUALITY")
    print("=" * 50)
    total_orig = sum(r['original_kb'] for r in results)
    total_svg = sum(r['svg_kb'] for r in results)

    for r in results:
        print(f"{r['file']:20} {r['original_kb']:7.1f} KB -> {r['svg_kb']:6.1f} KB  {r['quality']:20}")

    print("-" * 50)
    print(f"{'TOTAL':20} {total_orig:7.1f} KB -> {total_svg:6.1f} KB ({(1-total_svg/total_orig)*100:5.1f}% smaller)")
    print(f"\nTarget was ~125KB per file (1/8 MB)")
    avg_size = total_svg / len(results)
    print(f"Average SVG size: {avg_size:.1f} KB")

    if avg_size < 100:
        print("\nℹ️  Files are smaller than target. You could increase quality by:")
        print("  - Increasing color_precision to 5 or 6")
        print("  - Increasing path_precision to 3")
        print("  - Using 16-24 colors in quantization")
    elif avg_size > 150:
        print("\nℹ️  Files are larger than target. You could reduce size by:")
        print("  - Decreasing color_precision to 3")
        print("  - Increasing filter_speckle to 8")
        print("  - Using 8 colors in quantization")

    print(f"\nAll SVGs saved to: {out_dir}")

if __name__ == "__main__":
    process_dragons_balanced()