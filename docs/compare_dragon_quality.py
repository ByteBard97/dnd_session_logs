#!/usr/bin/env python3
"""
Convert SVGs back to PNG at 300 DPI and create before/after comparisons
"""
from pathlib import Path
from PIL import Image
import subprocess
import numpy as np

def svg_to_png_300dpi(svg_path: Path, png_path: Path, size_inches: float = 3.5):
    """
    Convert SVG to PNG at 300 DPI using Inkscape or cairosvg

    Args:
        svg_path: Path to input SVG
        png_path: Path to output PNG
        size_inches: Physical size in inches (3.5" at 300 DPI = 1050px)
    """
    # Calculate pixel dimensions for 300 DPI
    size_px = int(size_inches * 300)

    # Try different renderers in order of preference
    success = False

    # Method 1: Try Inkscape (best quality)
    try:
        subprocess.run([
            'inkscape',
            str(svg_path),
            f'--export-width={size_px}',
            f'--export-height={size_px}',
            '--export-dpi=300',
            f'--export-filename={png_path}'
        ], check=True, capture_output=True)
        success = True
        print(f"    ✓ Rendered with Inkscape at {size_px}x{size_px}px (300 DPI)")
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Method 2: Try rsvg-convert (good quality, fast)
    if not success:
        try:
            subprocess.run([
                'rsvg-convert',
                '-w', str(size_px),
                '-h', str(size_px),
                '-d', '300',
                '-p', '300',
                '-o', str(png_path),
                str(svg_path)
            ], check=True, capture_output=True)
            success = True
            print(f"    ✓ Rendered with rsvg-convert at {size_px}x{size_px}px (300 DPI)")
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    # Method 3: Try cairosvg (Python fallback)
    if not success:
        try:
            import cairosvg
            cairosvg.svg2png(
                url=str(svg_path),
                write_to=str(png_path),
                output_width=size_px,
                output_height=size_px,
                dpi=300
            )
            success = True
            print(f"    ✓ Rendered with cairosvg at {size_px}x{size_px}px (300 DPI)")
        except ImportError:
            print("    ⚠️  cairosvg not installed. Install with: pip install cairosvg")
        except Exception as e:
            print(f"    ⚠️  cairosvg error: {e}")

    if not success:
        print("    ❌ No SVG renderer available. Please install one of:")
        print("       - Inkscape: sudo apt-get install inkscape")
        print("       - rsvg: sudo apt-get install librsvg2-bin")
        print("       - cairosvg: pip install cairosvg")
        return False

    return True

def create_comparison_image(original_path: Path, svg_rendered_path: Path, output_path: Path):
    """Create a side-by-side comparison image"""

    # Load images
    original = Image.open(original_path).convert('RGBA')
    rendered = Image.open(svg_rendered_path).convert('RGBA')

    # Resize original to match rendered size for fair comparison
    target_size = rendered.size[0]
    original_resized = original.copy()
    original_resized.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)

    # Create side-by-side canvas
    canvas_width = target_size * 2 + 30  # 30px gap
    canvas_height = target_size + 100  # Extra space for labels

    # Create white background
    canvas = Image.new('RGBA', (canvas_width, canvas_height), (255, 255, 255, 255))

    # Paste images
    canvas.paste(original_resized, (0, 50))
    canvas.paste(rendered, (target_size + 30, 50))

    # Add labels using PIL's basic text (no fancy fonts)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(canvas)

    # Try to use a better font if available
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font = None
        small_font = None

    # Add text labels
    if font:
        draw.text((target_size//2, 10), "ORIGINAL PNG", fill=(0, 0, 0), font=font, anchor="mt")
        draw.text((target_size + 30 + target_size//2, 10), "SVG → PNG (300 DPI)", fill=(0, 0, 0), font=font, anchor="mt")

        # Add file info
        orig_size = original_path.stat().st_size / 1024
        # Find the actual SVG file (it's in the parent directory)
        svg_path = svg_rendered_path.parent.parent / f"{original_path.stem}.svg"
        if svg_path.exists():
            svg_size = svg_path.stat().st_size / 1024
        else:
            svg_size = 0

        draw.text((target_size//2, target_size + 70), f"{orig_size:.1f} KB", fill=(128, 128, 128), font=small_font, anchor="mt")
        draw.text((target_size + 30 + target_size//2, target_size + 70), f"SVG: {svg_size:.1f} KB", fill=(128, 128, 128), font=small_font, anchor="mt")

    canvas.save(output_path, quality=95)
    print(f"    ✓ Comparison saved: {output_path.name}")

def process_comparisons():
    """Main process to create all comparisons"""

    print("Dragon Quality Comparison Tool")
    print("=" * 50)

    # Find SVG directories
    svg_dirs = [
        Path('dragon_svgs'),  # Ultra-compressed
        Path('dragon_svgs_balanced')  # Balanced quality
    ]

    for svg_dir in svg_dirs:
        if not svg_dir.exists():
            print(f"⚠️  {svg_dir} not found, skipping...")
            continue

        print(f"\nProcessing SVGs from: {svg_dir}")
        print("-" * 40)

        # Create output directory
        out_dir = svg_dir / 'comparisons'
        out_dir.mkdir(exist_ok=True)

        # Process each SVG
        svg_files = sorted(svg_dir.glob('*.svg'))

        for svg_file in svg_files:
            print(f"\n{svg_file.name}:")

            # Find original PNG
            original_png = Path(svg_file.stem + '.png')
            if not original_png.exists():
                print(f"    ⚠️  Original {original_png} not found")
                continue

            # Convert SVG to PNG at 300 DPI
            rendered_png = out_dir / f"{svg_file.stem}_rendered.png"
            if svg_to_png_300dpi(svg_file, rendered_png):

                # Create comparison image
                comparison_png = out_dir / f"{svg_file.stem}_comparison.png"
                create_comparison_image(original_png, rendered_png, comparison_png)

                # Report file sizes
                orig_kb = original_png.stat().st_size / 1024
                svg_kb = svg_file.stat().st_size / 1024
                print(f"    Original PNG: {orig_kb:.1f} KB")
                print(f"    SVG file: {svg_kb:.1f} KB ({(svg_kb/orig_kb)*100:.1f}% of original)")

    print("\n" + "=" * 50)
    print("Comparisons complete!")
    print("\nView comparison images in:")
    for svg_dir in svg_dirs:
        comp_dir = svg_dir / 'comparisons'
        if comp_dir.exists():
            print(f"  - {comp_dir}/")

    # Check if we need to install renderers
    print("\nNote: For best quality rendering, install:")
    print("  sudo apt-get install inkscape librsvg2-bin")
    print("  pip install cairosvg")

def check_dependencies():
    """Check which SVG renderers are available"""
    print("\nChecking SVG rendering tools...")

    tools = {
        'inkscape': 'inkscape --version',
        'rsvg-convert': 'rsvg-convert --version',
    }

    available = []
    for tool, cmd in tools.items():
        try:
            subprocess.run(cmd.split(), capture_output=True, check=True)
            print(f"  ✓ {tool} is available")
            available.append(tool)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"  ✗ {tool} not found")

    try:
        import cairosvg
        print(f"  ✓ cairosvg is available")
        available.append('cairosvg')
    except ImportError:
        print(f"  ✗ cairosvg not found")

    if not available:
        print("\n⚠️  No SVG renderers found! Please install at least one:")
        print("  - Inkscape (best): sudo apt-get install inkscape")
        print("  - RSVG (fast): sudo apt-get install librsvg2-bin")
        print("  - CairoSVG (Python): pip install cairosvg")
        return False

    return True

if __name__ == "__main__":
    if check_dependencies():
        process_comparisons()
    else:
        print("\nPlease install a renderer first, then run this script again.")