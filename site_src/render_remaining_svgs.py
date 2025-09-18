#!/usr/bin/env python3
"""
Render remaining SVGs to PNG for comparison
"""
from pathlib import Path
import subprocess

def svg_to_png(svg_path: Path, png_path: Path):
    """Convert SVG to PNG using available renderer"""
    # Try Inkscape first
    try:
        subprocess.run([
            'inkscape',
            str(svg_path),
            '--export-width=1050',
            '--export-height=1050',
            f'--export-filename={png_path}'
        ], check=True, capture_output=True)
        return True
    except:
        pass

    # Try rsvg-convert
    try:
        subprocess.run([
            'rsvg-convert',
            '-w', '1050',
            '-h', '1050',
            '-o', str(png_path),
            str(svg_path)
        ], check=True, capture_output=True)
        return True
    except:
        return False

def main():
    out_dir = Path('all_dragon_comparisons')

    # Render optimal SVGs (560px, 16 colors, ~140KB)
    optimal_dir = Path('dragon_svgs_optimal')
    if optimal_dir.exists():
        print("Rendering optimal SVGs...")
        for svg_file in sorted(optimal_dir.glob('*.svg')):
            out_png = out_dir / f"{svg_file.stem}_03_optimal_560px_16colors_140KB.png"
            if svg_to_png(svg_file, out_png):
                print(f"  ✓ {out_png.name}")

    # Render high quality SVGs (640px, 24 colors, ~300KB)
    hq_dir = Path('dragon_svgs_highquality')
    if hq_dir.exists():
        print("Rendering high quality SVGs...")
        for svg_file in sorted(hq_dir.glob('*.svg')):
            out_png = out_dir / f"{svg_file.stem}_04_highquality_640px_24colors_300KB.png"
            if svg_to_png(svg_file, out_png):
                print(f"  ✓ {out_png.name}")

    print("\nAll conversions complete!")
    print(f"Files saved to: {out_dir}/")

    # List all files for each dragon
    print("\nFiles per dragon:")
    for dragon_num in ['01', '02', '03', '04']:
        files = sorted(out_dir.glob(f'dragons{dragon_num}_*.png'))
        if files:
            print(f"\nDragon {dragon_num}:")
            for f in files:
                size_kb = f.stat().st_size / 1024
                # Extract quality level from filename
                parts = f.stem.split('_')
                if len(parts) >= 3:
                    quality = parts[2]
                    print(f"  {quality:15} - {size_kb:7.1f} KB")

if __name__ == "__main__":
    main()