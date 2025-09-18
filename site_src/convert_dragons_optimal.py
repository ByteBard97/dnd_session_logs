#!/usr/bin/env python3
"""
Dragon PNG to SVG converter - Optimal 125KB version
Target: Exactly ~125KB per SVG with best possible quality
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
    Optimal preprocessing for 125KB target:
    - Size: 560px (between 512 and 640)
    - Colors: 16 (between 12 and 24)
    """
    img = Image.open(in_path).convert("RGBA")

    # Optimal size for 125KB target
    target_size = 560
    img.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)

    # Convert to numpy for processing
    arr = np.array(img)
    r, g, b, a = arr[...,0], arr[...,1], arr[...,2], arr[...,3]

    # Remove near-white pixels (threshold 252)
    mask_white = (r >= 252) & (g >= 252) & (b >= 252)
    arr[...,3] = np.where(mask_white, 0, a)

    # Convert back to PIL
    img2 = Image.fromarray(arr, mode="RGBA")

    # Optimal color count for 125KB
    img2 = img2.quantize(colors=16, dither=Image.Dither.FLOYDSTEINBERG).convert("RGBA")

    img2.save(out_path)
    return img2.size

def vectorize_dragon_optimal(png_file: Path, out_svg: Path):
    """Run VTracer with optimal settings for 125KB target"""
    vtracer.convert_image_to_svg_py(
        str(png_file),
        str(out_svg),
        colormode='color',          # Full color
        hierarchical='stacked',     # Proper layering
        mode='spline',              # Smooth curves
        filter_speckle=3,           # Balanced detail filtering
        color_precision=5,          # Good color precision (between 4-6)
        layer_difference=12,        # Balanced merging
        corner_threshold=50,        # Balanced corners
        length_threshold=3.0,       # Balanced segment handling
        path_precision=3            # Good path precision
    )

def optimize_svg_balanced(svg_path: Path):
    """Balanced optimization for quality and size"""
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

        if fill in ('#fff', '#ffffff', '#fefefe', 'white'):
            if tag == 'rect':
                try:
                    x = float(node.attrib.get('x', '0') or 0)
                    y = float(node.attrib.get('y', '0') or 0)
                    if abs(x) < 1 and abs(y) < 1:
                        parent = node.getparent()
                        if parent is not None:
                            parent.remove(node)
                except ValueError:
                    pass

    # Add title
    title_el = etree.Element('title')
    title_el.text = f"Dragon {svg_path.stem} (Optimal)"
    root.insert(0, title_el)

    # Add metadata
    meta = etree.Element('metadata')
    meta.text = json.dumps({
        "type": "dragon",
        "quality": "optimal",
        "target_size": "125KB",
        "colors": 16,
        "resolution": "560px"
    })
    root.insert(1, meta)

    # Write with moderate pretty print
    tree.write(str(svg_path), pretty_print=True, xml_declaration=True, encoding='utf-8')

def process_dragons_optimal():
    """Process dragon PNGs with optimal settings for 125KB target"""
    dragon_files = sorted(Path('.').glob('dragons*.png'))

    if not dragon_files:
        print("No dragon files found!")
        return

    print(f"Found {len(dragon_files)} dragon images")
    print("Using OPTIMAL settings for ~125KB target")
    print("Settings: 560px, 16 colors, balanced precision")
    print("-" * 50)

    # Create output directory
    out_dir = Path('dragon_svgs_optimal')
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

        # Preprocess PNG with optimal settings
        tmp_png = tmp_dir / f"{dragon_png.stem}_processed.png"
        new_size = preprocess_dragon_png(dragon_png, tmp_png)
        print(f"  Preprocessed to: {new_size[0]}x{new_size[1]} px with 16 colors")

        # Convert to SVG with optimal settings
        out_svg = out_dir / f"{dragon_png.stem}.svg"
        vectorize_dragon_optimal(tmp_png, out_svg)

        # Balanced optimization
        optimize_svg_balanced(out_svg)

        # Check final size
        svg_size = out_svg.stat().st_size
        print(f"  Final SVG: {svg_size / 1024:.1f} KB")

        # Distance from target
        target_kb = 125
        diff_kb = abs(svg_size / 1024 - target_kb)

        if diff_kb < 10:
            assessment = "✓ Perfect! Very close to 125KB target"
        elif diff_kb < 25:
            assessment = "✓ Good - within acceptable range"
        elif svg_size / 1024 < target_kb:
            assessment = "↓ Below target but good quality"
        else:
            assessment = "↑ Above target but excellent quality"

        print(f"  Assessment: {assessment}")
        print(f"  Reduction: {(1 - svg_size/orig_size) * 100:.1f}%")

        results.append({
            'file': dragon_png.name,
            'original_kb': round(orig_size / 1024, 1),
            'svg_kb': round(svg_size / 1024, 1),
            'diff_from_target': round(diff_kb, 1),
            'assessment': assessment,
            'reduction_pct': round((1 - svg_size/orig_size) * 100, 1)
        })

    # Clean up temp files
    import shutil
    shutil.rmtree(tmp_dir)

    # Print summary
    print("\n" + "=" * 50)
    print("CONVERSION SUMMARY - OPTIMAL 125KB TARGET")
    print("=" * 50)
    total_orig = sum(r['original_kb'] for r in results)
    total_svg = sum(r['svg_kb'] for r in results)

    for r in results:
        diff_str = f"({r['diff_from_target']:.0f}KB from target)"
        print(f"{r['file']:20} {r['original_kb']:7.1f} KB -> {r['svg_kb']:6.1f} KB {diff_str:25}")

    print("-" * 50)
    print(f"{'TOTAL':20} {total_orig:7.1f} KB -> {total_svg:6.1f} KB ({(1-total_svg/total_orig)*100:5.1f}% smaller)")

    avg_size = total_svg / len(results)
    print(f"\nTarget: 125KB per file")
    print(f"Average achieved: {avg_size:.1f} KB")
    print(f"Difference from target: {abs(avg_size - 125):.1f} KB")

    # Assessment
    if abs(avg_size - 125) < 15:
        print("\n🎯 EXCELLENT! Files are very close to the 125KB target!")
    elif avg_size < 125:
        print("\n✓ Good result - files are under target with good quality")
        print("  If you want exactly 125KB, increase colors to 18 or size to 580px")
    else:
        print("\n✓ Files are slightly over target but have excellent quality")
        print("  If you need exactly 125KB, reduce colors to 14 or size to 540px")

    print(f"\nAll optimal SVGs saved to: {out_dir}/")

if __name__ == "__main__":
    process_dragons_optimal()