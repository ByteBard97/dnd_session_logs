#!/usr/bin/env python3
from __future__ import annotations
import re, os, json, hashlib
from pathlib import Path
from typing import Optional
from PIL import Image
from tqdm import tqdm
import vtracer
from lxml import etree
import numpy as np

# Directories
IN_DIR  = Path("new_assets")
OUT_DIR = Path("svgs")
TMP_DIR = Path("tmp_landscape")

OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

# Enhanced category mapping for landscape elements
LANDSCAPE_CATEGORY_MAP = {
    # Hardscape
    "deck": "hardscape-deck",
    "patio": "hardscape-patio",
    "walkway": "hardscape-path",
    "path": "hardscape-path",
    "paver": "hardscape-patio",

    # Natural features
    "boulder": "furniture-boulder",
    "boulders": "furniture-boulder",
    "pond": "water-feature",
    "water": "water-feature",

    # Planting areas
    "planting": "planting-bed",
    "bed": "planting-bed",
    "gravel": "groundcover-gravel",

    # Edging
    "edging": "hardscape-edging",
    "metal": "hardscape-edging",
}

def guess_landscape_category(filename: str) -> str:
    """Categorize landscape elements based on filename"""
    name = filename.lower()
    tokens = re.split(r'[\W_]+', name)
    scores = {}

    for t in tokens:
        if t in LANDSCAPE_CATEGORY_MAP:
            cat = LANDSCAPE_CATEGORY_MAP[t]
            scores[cat] = scores.get(cat, 0) + 1

    if not scores:
        return "landscape-unknown"

    # Pick the category with max votes
    return sorted(scores.items(), key=lambda x: (-x[1], x[0]))[0][0]

def hash_bytes(b: bytes) -> str:
    return hashlib.sha1(b).hexdigest()[:8]

def preprocess_landscape_png(in_path: Path, out_path: Path, white_thresh=240, colors=3, resize_to=400):
    """
    Preprocess landscape PNG for cleaner SVG output:
    1. Make near-white pixels transparent
    2. Resize if too large
    3. Quantize to fewer colors for cleaner vectors
    """
    img = Image.open(in_path).convert("RGBA")

    # Resize if too large
    if img.width > resize_to or img.height > resize_to:
        img.thumbnail((resize_to, resize_to), Image.Resampling.LANCZOS)

    # Convert to numpy for processing
    arr = np.array(img)
    r, g, b, a = arr[...,0], arr[...,1], arr[...,2], arr[...,3]

    # Make near-white pixels transparent
    mask_white = (r >= white_thresh) & (g >= white_thresh) & (b >= white_thresh)
    arr[...,3] = np.where(mask_white, 0, a)

    # Convert back to PIL
    img2 = Image.fromarray(arr, mode="RGBA")

    # Quantize to reduce colors
    if colors < 256:
        img2 = img2.quantize(colors=colors).convert("RGBA")

    img2.save(out_path)
    print(f"  Preprocessed: {in_path.name} -> {out_path.name} ({img.size} -> {img2.size})")

def vectorize_png_to_svg(png_file: Path, out_svg: Path):
    """Run VTracer with aggressive simplification for clean, small SVGs"""
    vtracer.convert_image_to_svg_py(
        str(png_file),
        str(out_svg),
        colormode='color',
        hierarchical='stacked',
        mode='spline',
        filter_speckle=16,          # remove many tiny specks
        color_precision=2,          # aggressive color quantization
        layer_difference=32,        # merge similar colors more
        corner_threshold=120,       # much smoother curves
        length_threshold=12.0,      # drop more small segments
        path_precision=1            # much less precise paths
    )

def _get_fill(node):
    """Extract fill color from SVG node"""
    fill = (node.attrib.get('fill') or '').strip().lower()
    if not fill:
        style = node.attrib.get('style') or ''
        m = re.search(r'fill\\s*:\\s*([^;]+)', style, re.I)
        fill = (m.group(1).strip().lower() if m else '')
    return fill

def embed_landscape_metadata(svg_path: Path, title: str, source_png: str, category: str, view_w: int, view_h: int):
    """Add metadata and clean up the SVG"""
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(str(svg_path), parser)
    root = tree.getroot()

    if not root.tag.endswith('svg'):
        return

    # Use real viewBox
    root.attrib.pop('width', None)
    root.attrib.pop('height', None)
    root.set('viewBox', f'0 0 {view_w} {view_h}')

    # Remove white background elements
    vw, vh = float(view_w), float(view_h)
    for node in list(root.iter()):
        tag = etree.QName(node).localname
        fill = _get_fill(node)
        is_white = fill in ('#fff','#ffffff','#fefefe','rgb(255,255,255)','white')
        if not is_white:
            continue
        if tag == 'rect':
            x = float(node.attrib.get('x','0') or 0)
            y = float(node.attrib.get('y','0') or 0)
            w = float(node.attrib.get('width', '0') or 0)
            h = float(node.attrib.get('height','0') or 0)
            if abs(x) < 1 and abs(y) < 1 and w >= vw*0.98 and h >= vh*0.98:
                print(f"  Removing white background rect: {w}x{h}")
                node.getparent().remove(node)
        elif tag in ('path','polygon'):
            parent = node.getparent()
            if parent is not None and list(parent).index(node) == 0:
                print(f"  Removing white background {tag}")
                parent.remove(node)

    # Add title
    for t in root.findall('{http://www.w3.org/2000/svg}title'):
        root.remove(t)
    title_el = etree.Element('title')
    title_el.text = title
    root.insert(0, title_el)

    # Add metadata
    meta = etree.Element('metadata')
    meta.text = json.dumps({
        "source_png": source_png,
        "category": category,
        "viewBox": [0, 0, view_w, view_h],
        "type": "landscape-element"
    })
    root.insert(1, meta)

    tree.write(str(svg_path), pretty_print=True, xml_declaration=True, encoding='utf-8')

def process_landscape_image(png_path: Path):
    """Process a single pre-split landscape asset"""
    category = guess_landscape_category(png_path.name)
    print(f"Processing {png_path.name} -> category: {category}")

    # Ensure category subfolder
    cat_dir = OUT_DIR / category
    cat_dir.mkdir(parents=True, exist_ok=True)

    # Preprocess the PNG
    pre_png = TMP_DIR / f"{png_path.stem}_pre.png"
    preprocess_landscape_png(png_path, pre_png, colors=3, resize_to=400)

    # Hash for stable naming
    with open(pre_png, 'rb') as f:
        h = hash_bytes(f.read())

    # Get preprocessed dimensions
    with Image.open(pre_png) as img:
        tw, th = img.size

    # Generate SVG
    out_svg = cat_dir / f"{category}_{png_path.stem}_{h}.svg"
    print(f"  Converting to SVG ({tw}x{th}) -> {out_svg.name}")
    vectorize_png_to_svg(pre_png, out_svg)

    # Add metadata
    title = f"{category} • {png_path.stem}"
    embed_landscape_metadata(out_svg, title, str(png_path.name), category, tw, th)

def main():
    """Process all landscape assets in new_assets folder"""
    files = sorted([p for p in IN_DIR.iterdir() if p.suffix.lower() in ('.png', '.jpg', '.jpeg')])
    if not files:
        print(f"No images found in {IN_DIR}")
        return

    print(f"Found {len(files)} landscape assets to process")
    for p in tqdm(files, desc="Converting landscape assets"):
        try:
            process_landscape_image(p)
        except Exception as e:
            print(f"[WARN] Failed on {p.name}: {e}")

    # Clean up temp files
    import shutil
    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)
        print(f"Cleaned up {TMP_DIR}")

if __name__ == "__main__":
    main()