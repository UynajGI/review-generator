#!/usr/bin/env python3
"""DPI-based image sizing for ElegantNote documents.
Checks all \includegraphics in .tex files and fixes undersized images.

Usage: python scripts/dpi_check.py <tex_dir> <image_dir> [--device normal|pad|screen|kindle]
"""

import re, subprocess, math, sys, argparse
from pathlib import Path

DEVICE_LINE_WIDTH = {
    'normal': 6.3,   # A4, 16cm
    'pad': 4.7,      # iPad, 12cm
    'screen': 8.7,   # 4:3 PPT, 22cm
    'kindle': 2.8,   # Kindle, 7cm
}
DPI_MIN = 120
DPI_TARGET = 150


def get_dimensions(img_dir):
    dims = {}
    for img in Path(img_dir).iterdir():
        if img.suffix.lower() in ('.jpg', '.jpeg', '.png', '.pdf'):
            try:
                r = subprocess.run(['identify', '-format', '%w %h', str(img)],
                                   capture_output=True, text=True, timeout=5)
                if r.returncode == 0:
                    w, h = map(int, r.stdout.strip().split())
                    dims[img.name] = {'w': w, 'h': h, 'ratio': w / h}
                    dims[img.stem] = {'w': w, 'h': h, 'ratio': w / h}
            except Exception:
                pass
    return dims


def calc_scale(pixel_w, ratio, line_width):
    """Calculate optimal \linewidth scale for target DPI."""
    scale = math.floor(pixel_w / (DPI_MIN * line_width) * 100) / 100
    if ratio > 2.5:
        scale = min(0.95, max(0.25, scale))
    elif ratio > 1.5:
        scale = min(0.90, max(0.25, scale))
    elif ratio > 0.7:
        scale = min(0.85, max(0.25, scale))
    elif ratio > 0.4:
        scale = min(0.70, max(0.20, scale))
    else:
        return None  # height-constrained
    return scale


def main():
    parser = argparse.ArgumentParser(description='Fix image DPI in LaTeX docs')
    parser.add_argument('tex_dir', help='Directory with .tex files')
    parser.add_argument('image_dir', help='Directory with image files')
    parser.add_argument('--device', default='normal', choices=DEVICE_LINE_WIDTH.keys())
    parser.add_argument('--dry-run', action='store_true', help='Report only, no changes')
    args = parser.parse_args()

    line_w = DEVICE_LINE_WIDTH[args.device]
    dims = get_dimensions(args.image_dir)
    if not dims:
        print(f"No images found in {args.image_dir}")
        return

    updated = 0
    for sf in sorted(Path(args.tex_dir).glob('*.tex')):
        content = sf.read_text()
        changed = False

        for m in re.finditer(r'\\includegraphics\[([^\]]*)\]\{([^}]+)\}', content):
            fname = m.group(2).strip()
            old = m.group(0)
            if fname not in dims:
                continue

            info = dims[fname]
            w, h, ratio = info['w'], info['h'], info['ratio']

            # Fix missing extension
            new_fname = fname
            if '.' not in fname.split('/')[-1]:
                for ext in ['.jpg', '.jpeg', '.png', '.pdf']:
                    if fname + ext in dims:
                        new_fname = fname + ext
                        break

            cur_scale_match = re.search(r'width=([0-9.]+)\\linewidth', m.group(1))
            if cur_scale_match:
                cur_scale = float(cur_scale_match.group(1))
                cur_dpi = w / (line_w * cur_scale)
            else:
                cur_scale = None
                cur_dpi = None

            new_scale = calc_scale(w, ratio, line_w)
            if new_scale is None:
                new_size = 'height=0.75\\textheight,keepaspectratio'
            else:
                new_size = f'width={new_scale:.2f}\\linewidth'

            new = f'\\includegraphics[{new_size}]{{{new_fname}}}'
            if old != new:
                new_dpi = w / (line_w * new_scale) if new_scale else w / (line_w * 0.5)
                if args.dry_run:
                    dpi_str = f'{cur_dpi:.0f}' if cur_dpi else '?'
                    print(f'  {sf.name}: {new_fname[:30]}... {w}px DPI {dpi_str} -> {new_size}')
                content = content.replace(old, new)
                changed = True
                updated += 1

        if changed and not args.dry_run:
            sf.write_text(content)

    if args.dry_run:
        print(f'Dry run: {updated} images would be updated')
    else:
        print(f'Updated {updated} images')

    # Report
    dpi_vals = []
    for sf in sorted(Path(args.tex_dir).glob('*.tex')):
        for m in re.finditer(r'\\includegraphics\[([^\]]*)\]\{([^}]+)\}', sf.read_text()):
            f = m.group(2).strip()
            s = m.group(1)
            if f in dims:
                mm = re.search(r'width=([0-9.]+)\\linewidth', s)
                if mm:
                    dpi_vals.append(dims[f]['w'] / (line_w * float(mm.group(1))))

    if dpi_vals:
        print(f'DPI: {min(dpi_vals):.0f}-{max(dpi_vals):.0f}, avg {sum(dpi_vals)/len(dpi_vals):.0f}')
        below = sum(1 for d in dpi_vals if d < 120)
        print(f'Below {DPI_MIN} DPI: {below}' + (' ✅' if below == 0 else ''))


if __name__ == '__main__':
    main()
