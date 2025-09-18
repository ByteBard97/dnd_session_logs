#!/usr/bin/env python3
from __future__ import annotations
import re, os, json, hashlib, tempfile
from pathlib import Path
from typing import List, Tuple, Optional
from PIL import Image
from tqdm import tqdm
import vtracer
from lxml import etree
import numpy as np

IN_DIR  = Path("generated_assets")
OUT_DIR = Path("svgs")
TMP_DIR = Path("tmp_splits")  # for cropped PNG tiles

OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

# ---- heuristics -------------------------------------------------------------

CATEGORY_MAP = {
    # tokens -> canonical category
    "broadleaf": "tree-broadleaf",
    "conifer": "tree-conifer",
    "spruce": "tree-conifer",
    "pine": "tree-conifer",
    "shrub": "shrub",
    "groundcover": "groundcover",
    "ground": "groundcover",
    "flower": "flower",
    "flowering": "flower",
    "bloom": "flower",
    "grass": "ornamental-grass",
    "ornament": "ornamental-grass",
    "tuft": "perennial-tuft",
    "tufted": "perennial-tuft",
    "rosette": "perennial-tuft",
    "sedge": "perennial-tuft",
    "sedgeperennial": "perennial-tuft",
    "clump": "perennial-tuft",
    "perennial": "perennial-tuft",
    "herbaceous": "perennial-tuft",
    "mounded": "perennial-tuft",
}

def guess_category(filename: str) -> str:
    name = filename.lower()
    tokens = re.split(r'[\W_]+', name)
    scores = {}
    for t in tokens:
        if t in CATEGORY_MAP:
            cat = CATEGORY_MAP[t]
            scores[cat] = scores.get(cat, 0) + 1
    if not scores:
        return "unknown"
    # pick the category with max votes
    return sorted(scores.items(), key=lambda x: (-x[1], x[0]))[0][0]

def is_probable_mj_grid(img: Image.Image) -> bool:
    # Heuristic: MJ 4-up grids are square and fairly large (≥1400 px).
    w, h = img.size
    return (w == h) and (w >= 1400)

def split_into_quadrants(img: Image.Image) -> List[Tuple[Image.Image, Tuple[int,int,int,int]]]:
    w, h = img.size
    half = w // 2
    boxes = [
        (0,   0,    half, half),  # TL
        (half,0,    w,    half),  # TR
        (0,   half, half, h   ),  # BL
        (half,half, w,    h   ),  # BR
    ]
    tiles = []
    for box in boxes:
        tiles.append((img.crop(box), box))
    return tiles

def hash_bytes(b: bytes) -> str:
    return hashlib.sha1(b).hexdigest()[:8]

# ---- PNG preprocessing for simpler SVGs ------------------------------------

def preprocess_png(in_path: Path, out_path: Path, white_thresh=240, colors=4, resize_to=512):
    """
    Preprocess PNG to reduce SVG complexity:
    1. Make near-white pixels transparent
    2. Resize to smaller dimensions
    3. Quantize to fewer colors
    4. Apply slight blur to smooth details
    """
    img = Image.open(in_path).convert("RGBA")

    # Resize to reduce detail
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

    # Quantize to reduce colors (this dramatically reduces SVG complexity)
    if colors < 256:
        img2 = img2.quantize(colors=colors).convert("RGBA")

    img2.save(out_path)
    print(f"  Preprocessed: {in_path.name} -> {out_path.name} ({img.size} -> {img2.size})")

# ---- SVG post-process -------------------------------------------------------

def _get_fill(node):
    # check inline fill attr
    fill = (node.attrib.get('fill') or '').strip().lower()
    if not fill:
        # check style attr
        style = node.attrib.get('style') or ''
        m = re.search(r'fill\s*:\s*([^;]+)', style, re.I)
        fill = (m.group(1).strip().lower() if m else '')
    return fill

def embed_metadata(svg_path: Path, title: str, source_png: str, category: str, view_w: int, view_h: int):
    """
    Add <title> and <metadata> to the top-level <svg>. Use real viewBox and remove white background.
    """
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(str(svg_path), parser)
    root = tree.getroot()

    # normalize namespace
    if not root.tag.endswith('svg'):
        return

    # Use real viewBox that matches the raster tile - this is critical!
    root.attrib.pop('width', None)
    root.attrib.pop('height', None)
    root.set('viewBox', f'0 0 {view_w} {view_h}')

    # Remove full-canvas white background rect/path if present
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
            # heuristic: huge white shape often first child; drop if it's the first child
            parent = node.getparent()
            if parent is not None and list(parent).index(node) == 0:
                print(f"  Removing white background {tag}")
                parent.remove(node)

    # Insert/replace <title>
    # Remove existing title elements
    for t in root.findall('{http://www.w3.org/2000/svg}title'):
        root.remove(t)
    title_el = etree.Element('title')
    title_el.text = title
    root.insert(0, title_el)

    # Insert metadata element
    meta = etree.Element('metadata')
    meta.text = json.dumps({"source_png": source_png, "category": category, "viewBox":[0,0,view_w,view_h]})
    root.insert(1, meta)

    tree.write(str(svg_path), pretty_print=True, xml_declaration=True, encoding='utf-8')

# ---- Vectorize pipeline -----------------------------------------------------

def vectorize_png_to_svg(png_file: Path, out_svg: Path):
    # Run VTracer with AGGRESSIVE simplification for clean, small SVGs
    vtracer.convert_image_to_svg_py(
        str(png_file),
        str(out_svg),
        colormode='color',          # good for multi-flat-color symbols
        hierarchical='stacked',     # keep layers stacked
        mode='spline',              # smoother curves
        filter_speckle=16,          # remove many tiny specks (was 4)
        color_precision=2,          # aggressive color quantization (was 6)
        layer_difference=32,        # merge similar colors more (was 16)
        corner_threshold=120,       # much smoother curves (was 60)
        length_threshold=12.0,      # drop more small segments (was 4.0)
        path_precision=1            # much less precise paths (was 3)
    )

def process_image(png_path: Path):
    category = guess_category(png_path.name)
    print(f"Processing {png_path.name} -> category: {category}")

    img = Image.open(png_path).convert('RGBA')
    tiles = []

    if is_probable_mj_grid(img):
        print(f"  Detected as MJ grid ({img.size[0]}x{img.size[1]}), splitting into 4 tiles...")
        for idx, (tile, box) in enumerate(split_into_quadrants(img), start=1):
            tmp_tile = TMP_DIR / f"{png_path.stem}_tile{idx}.png"
            tile.save(tmp_tile)
            tiles.append((tmp_tile, idx))
    else:
        # Single image; keep as-is
        print(f"  Single image ({img.size[0]}x{img.size[1]})")
        tmp_tile = TMP_DIR / f"{png_path.stem}_tile1.png"
        img.save(tmp_tile)
        tiles.append((tmp_tile, 1))

    # Ensure category subfolder
    cat_dir = OUT_DIR / category
    cat_dir.mkdir(parents=True, exist_ok=True)

    for tmp_png, idx in tiles:
        # Preprocess the PNG to reduce complexity
        pre_png = TMP_DIR / f"{png_path.stem}_tile{idx}_pre.png"
        preprocess_png(tmp_png, pre_png, colors=2, resize_to=256)

        # hash to keep names stable even if files repeat
        with open(pre_png, 'rb') as f:
            h = hash_bytes(f.read())

        # Get the preprocessed tile dimensions (these will be smaller)
        with Image.open(pre_png) as timg:
            tw, th = timg.size

        out_svg = cat_dir / f"{category}_{png_path.stem}_v{idx}_{h}.svg"
        print(f"  Converting tile {idx} ({tw}x{th}) -> {out_svg.name}")
        vectorize_png_to_svg(pre_png, out_svg)
        title = f"{category} • {png_path.stem} • v{idx}"
        embed_metadata(out_svg, title, str(png_path.name), category, tw, th)

def main():
    files = sorted([p for p in IN_DIR.iterdir() if p.suffix.lower() in ('.png', '.jpg', '.jpeg')])
    if not files:
        print(f"No images found in {IN_DIR}")
        return
    print(f"Found {len(files)} images to process")
    for p in tqdm(files, desc="Vectorizing"):
        try:
            process_image(p)
        except Exception as e:
            print(f"[WARN] Failed on {p.name}: {e}")

if __name__ == "__main__":
    main()