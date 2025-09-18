#!/usr/bin/env python3
"""
Fix SVG viewBox issues in generated files
"""
from pathlib import Path
from lxml import etree
import re

def fix_svg_viewbox(svg_path: Path, target_size: int):
    """Fix the viewBox attribute in SVG files"""
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(str(svg_path), parser)
    root = tree.getroot()

    if not root.tag.endswith('svg'):
        print(f"  ⚠️  Not an SVG file: {svg_path}")
        return False

    # Set the correct viewBox based on the target size
    root.set('viewBox', f'0 0 {target_size} {target_size}')

    # Remove width/height attributes to make it scalable
    root.attrib.pop('width', None)
    root.attrib.pop('height', None)

    # Save the fixed SVG
    tree.write(str(svg_path), pretty_print=True, xml_declaration=True, encoding='utf-8')
    return True

def process_directory(dir_path: Path, target_size: int):
    """Process all SVGs in a directory"""
    if not dir_path.exists():
        print(f"⚠️  Directory not found: {dir_path}")
        return

    print(f"\nProcessing: {dir_path}")
    print(f"Setting viewBox to: 0 0 {target_size} {target_size}")

    svg_files = sorted(dir_path.glob('*.svg'))
    for svg_file in svg_files:
        if fix_svg_viewbox(svg_file, target_size):
            print(f"  ✓ Fixed: {svg_file.name}")
        else:
            print(f"  ✗ Failed: {svg_file.name}")

def main():
    print("SVG ViewBox Fixer")
    print("=" * 50)

    # Fix each directory with the appropriate size
    directories = [
        (Path('dragon_svgs'), 128),  # Ultra compressed - 128px
        (Path('dragon_svgs_balanced'), 512),  # Balanced - 512px
        (Path('dragon_svgs_optimal'), 560),  # Optimal - 560px
        (Path('dragon_svgs_highquality'), 640),  # High quality - 640px
    ]

    for dir_path, size in directories:
        process_directory(dir_path, size)

    print("\n" + "=" * 50)
    print("ViewBox fixes complete!")
    print("\nNow re-render the PNGs with the comparison script.")

if __name__ == "__main__":
    main()