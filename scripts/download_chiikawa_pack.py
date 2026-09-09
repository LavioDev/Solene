#!/usr/bin/env python3
"""
Solène Chiikawa Sticker Pack Downloader & Importer
--------------------------------------------------
Usage:
  1. Download an entire Line Store sticker set by URL or ID:
     python scripts/download_chiikawa_pack.py --line-id 23746 --pack-name chiikawa_vol1

  2. Import and optimize scattered local images from a folder:
     python scripts/download_chiikawa_pack.py --local-dir "C:/path/to/my/chiikawa_images" --pack-name chiikawa

  3. Generate or refresh manifest.json for existing stickers:
     python scripts/download_chiikawa_pack.py --refresh-manifest
"""

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

DEFAULT_TARGET_DIR = Path(__file__).resolve().parent.parent / "frontend" / "public" / "stickers" / "chiikawa"


def sanitize_filename(name: str) -> str:
    s = re.sub(r"[^\w\-_.]", "_", name)
    return s.strip("_")


def optimize_and_save_image(src_path: Path, dest_path: Path, max_size: int = 320) -> None:
    """Optimize image and convert to WebP or copy PNG with transparency."""
    if HAS_PIL:
        try:
            with Image.open(src_path) as img:
                img = img.convert("RGBA")
                # Resize if larger than max_size while maintaining aspect ratio
                if img.width > max_size or img.height > max_size:
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                # Save as WebP with lossless/high quality
                dest_webp = dest_path.with_suffix(".webp")
                img.save(dest_webp, format="WEBP", quality=90, method=6)
                return
        except Exception as e:
            print(f"PIL conversion error for {src_path.name}: {e}. Falling back to copy.")
    
    # Fallback if PIL not installed: simple copy
    with open(src_path, "rb") as fsrc, open(dest_path, "wb") as fdst:
        fdst.write(fsrc.read())


def download_url(url: str, headers: Optional[Dict[str, str]] = None) -> bytes:
    req = urllib.request.Request(
        url,
        headers=headers or {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()


def fetch_line_pack(line_product_id: str, dest_dir: Path) -> List[Dict]:
    """Scrape and batch-download all stickers in a Line Store sticker pack."""
    print(f"[*] Fetching Line Store pack ID: {line_product_id}...")
    url = f"https://store.line.me/stickershop/product/{line_product_id}/en"
    try:
        html = download_url(url).decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"[!] Failed to fetch product page: {e}")
        return []

    # Find pack title
    title_match = re.search(r'<h3 class="mdCMN08Ttl"[^>]*>(.*?)</h3>', html, re.DOTALL)
    pack_title = title_match.group(1).strip() if title_match else f"Line Pack {line_product_id}"
    print(f"[*] Pack Title: {pack_title}")

    # Extract all sticker image URLs
    # Pattern looks like: https://stickershop.line-scdn.net/stickershop/v1/sticker/12345/android/sticker.png
    # or inside style="background-image:url(...)"
    found_ids = list(set(re.findall(r'/stickershop/v1/sticker/(\d+)/', html)))
    if not found_ids:
        # Fallback to data-preview or preview images
        found_ids = list(set(re.findall(r'"id"\s*:\s*"(\d+)"', html)))

    print(f"[*] Found {len(found_ids)} stickers in pack.")
    if not found_ids:
        print("[!] No sticker IDs found. Line Store page layout may have changed.")
        return []

    dest_dir.mkdir(parents=True, exist_ok=True)
    results = []

    for idx, sid in enumerate(found_ids, start=1):
        # Line high-res sticker URL pattern
        img_url = f"https://stickershop.line-scdn.net/stickershop/v1/sticker/{sid}/iPhone/sticker@2x.png"
        try:
            raw_bytes = download_url(img_url)
        except Exception:
            # Try android URL fallback
            try:
                img_url = f"https://stickershop.line-scdn.net/stickershop/v1/sticker/{sid}/android/sticker.png"
                raw_bytes = download_url(img_url)
            except Exception as e:
                print(f"[!] Skipping sticker {sid}: {e}")
                continue

        temp_png = dest_dir / f"temp_{sid}.png"
        with open(temp_png, "wb") as f:
            f.write(raw_bytes)

        final_filename = f"chiikawa_{idx:02d}.webp" if HAS_PIL else f"chiikawa_{idx:02d}.png"
        final_path = dest_dir / final_filename

        optimize_and_save_image(temp_png, final_path)
        if temp_png.exists():
            temp_png.unlink()

        # Simple character classifier based on index or title
        category = "chiikawa"
        if idx % 3 == 0:
            category = "usagi"
        elif idx % 2 == 0:
            category = "hachiware"

        results.append({
            "id": f"line_{sid}",
            "filename": final_filename,
            "url": f"/stickers/chiikawa/{final_filename}",
            "name": f"Chiikawa #{idx}",
            "category": category,
        })
        print(f"  [+] Saved ({idx}/{len(found_ids)}): {final_filename}")

    return results


def import_local_folder(src_folder: Path, dest_dir: Path) -> List[Dict]:
    """Import and optimize user's scattered local images into the stickers library."""
    print(f"[*] Importing images from: {src_folder}...")
    if not src_folder.exists() or not src_folder.is_dir():
        print(f"[!] Directory not found: {src_folder}")
        return []

    dest_dir.mkdir(parents=True, exist_ok=True)
    valid_exts = {".png", ".webp", ".jpg", ".jpeg", ".gif"}
    image_files = [f for f in src_folder.iterdir() if f.is_file() and f.suffix.lower() in valid_exts]

    print(f"[*] Found {len(image_files)} image files.")
    results = []

    for idx, file_path in enumerate(sorted(image_files), start=1):
        stem_clean = sanitize_filename(file_path.stem)
        final_filename = f"{stem_clean}_{idx:02d}.webp" if HAS_PIL else f"{stem_clean}_{idx:02d}{file_path.suffix.lower()}"
        final_path = dest_dir / final_filename

        optimize_and_save_image(file_path, final_path)

        # Categorize by filename if contains keyword
        name_lower = file_path.stem.lower()
        if "hachi" in name_lower:
            category = "hachiware"
        elif "usagi" in name_lower or "tho" in name_lower:
            category = "usagi"
        elif "momonga" in name_lower:
            category = "momonga"
        elif "kuri" in name_lower:
            category = "kurimanju"
        else:
            category = "chiikawa"

        results.append({
            "id": f"local_{idx:02d}",
            "filename": final_filename,
            "url": f"/stickers/chiikawa/{final_filename}",
            "name": file_path.stem.replace("_", " ").replace("-", " ").title(),
            "category": category,
        })
        print(f"  [+] Imported ({idx}/{len(image_files)}): {final_filename}")

    return results


def refresh_manifest(dest_dir: Path) -> None:
    """Scan existing sticker directory and generate manifest.json."""
    if not dest_dir.exists():
        print(f"[!] Directory does not exist: {dest_dir}")
        return

    valid_exts = {".webp", ".png", ".svg", ".jpg", ".jpeg", ".gif"}
    files = [f for f in sorted(dest_dir.iterdir()) if f.is_file() and f.suffix.lower() in valid_exts]

    items = []
    for idx, f in enumerate(files, start=1):
        name_lower = f.stem.lower()
        if "hachi" in name_lower:
            category = "hachiware"
        elif "usagi" in name_lower:
            category = "usagi"
        elif "momonga" in name_lower:
            category = "momonga"
        elif "kuri" in name_lower:
            category = "kurimanju"
        elif "rakko" in name_lower:
            category = "rakko"
        else:
            category = "chiikawa"

        clean_title = f.stem.replace("_", " ").replace("-", " ").title()
        items.append({
            "id": f"stk_{idx:02d}",
            "filename": f.name,
            "url": f"/stickers/chiikawa/{f.name}",
            "name": clean_title,
            "category": category,
        })

    manifest = {
        "pack_id": "chiikawa",
        "pack_name": "Chiikawa & Friends",
        "total": len(items),
        "categories": [
            {"key": "all", "name": "All"},
            {"key": "chiikawa", "name": "Chiikawa"},
            {"key": "hachiware", "name": "Hachiware"},
            {"key": "usagi", "name": "Usagi"},
            {"key": "others", "name": "Others"},
        ],
        "stickers": items,
    }

    manifest_path = dest_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"[OK] Successfully wrote {len(items)} stickers to {manifest_path}")


def main():
    parser = argparse.ArgumentParser(description="Chiikawa sticker pack downloader and importer for Solène.")
    parser.add_argument("--line-id", type=str, help="Line store sticker pack ID or URL")
    parser.add_argument("--local-dir", type=str, help="Path to local directory with scattered image files")
    parser.add_argument("--dest", type=str, default=str(DEFAULT_TARGET_DIR), help="Destination sticker directory")
    parser.add_argument("--refresh-manifest", action="store_true", help="Refresh manifest.json for existing stickers")

    args = parser.parse_args()
    dest_path = Path(args.dest)

    if args.line_id:
        # If full URL passed, extract numeric ID
        line_id = args.line_id
        match = re.search(r"product/(\d+)", line_id)
        if match:
            line_id = match.group(1)

        stickers = fetch_line_pack(line_id, dest_path)
        if stickers:
            refresh_manifest(dest_path)
    elif args.local_dir:
        src_path = Path(args.local_dir)
        stickers = import_local_folder(src_path, dest_path)
        if stickers:
            refresh_manifest(dest_path)
    elif args.refresh_manifest:
        refresh_manifest(dest_path)
    else:
        print("[*] No action specified. Running manifest refresh on default directory...")
        refresh_manifest(dest_path)


if __name__ == "__main__":
    main()
