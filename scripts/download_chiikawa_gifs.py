#!/usr/bin/env python3
"""
Download transparent Chiikawa animated GIFs and add them to Solene sticker manifest.
"""
import urllib.request
import urllib.parse
import json
import os
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TARGET_DIR = Path(__file__).resolve().parent.parent / "frontend" / "public" / "stickers" / "chiikawa"
GIFS_DIR = TARGET_DIR / "gifs"
MANIFEST_FILE = TARGET_DIR / "manifest.json"

GIPHY_API_KEY = "Gc7131jiJuvI7IdN0HZ1D7nh0ow5BU6g"

def sanitize_name(s: str) -> str:
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", " ", s).strip()
    return s

def fetch_giphy_stickers(query: str, limit: int = 30):
    url = f"https://api.giphy.com/v1/stickers/search?api_key={GIPHY_API_KEY}&q={urllib.parse.quote(query)}&limit={limit}&rating=g"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        res = urllib.request.urlopen(req, timeout=15)
        data = json.loads(res.read().decode("utf-8"))
        return data.get("data", [])
    except Exception as e:
        print(f"[!] Error querying Giphy for '{query}': {e}")
        return []

def main():
    GIFS_DIR.mkdir(parents=True, exist_ok=True)
    
    queries = ["chiikawa", "hachiware", "usagi chiikawa", "ちいかわ"]
    seen_ids = set()
    gif_items = []
    
    print("[*] Searching Giphy for transparent animated Chiikawa stickers...")
    for q in queries:
        items = fetch_giphy_stickers(q, limit=20)
        for item in items:
            gid = item.get("id")
            if not gid or gid in seen_ids:
                continue
            seen_ids.add(gid)
            
            raw_title = item.get("title", "")
            title = sanitize_name(raw_title.replace("Sticker by nagano", "").replace("Sticker", "").strip())
            if not title or len(title) < 2:
                title = f"Chiikawa Gif {len(gif_items) + 1}"
            
            # Category detection
            lower = title.lower() + " " + raw_title.lower()
            if "hachi" in lower:
                cat = "hachiware"
            elif "usagi" in lower or "rabbit" in lower:
                cat = "usagi"
            elif "chiikawa" in lower:
                cat = "chiikawa"
            else:
                cat = "gif"
                
            # Prefer fixed_height (lighter, ~100-200kb) or original
            images = item.get("images", {})
            gif_url = images.get("fixed_height", {}).get("url") or images.get("original", {}).get("url")
            if not gif_url:
                continue
                
            gif_items.append({
                "giphy_id": gid,
                "title": title,
                "category": cat,
                "url": gif_url
            })
            if len(gif_items) >= 28:
                break
        if len(gif_items) >= 28:
            break

    print(f"[*] Found {len(gif_items)} unique animated stickers. Downloading...")
    downloaded = []
    for idx, it in enumerate(gif_items, start=1):
        filename = f"chiikawa_anim_{idx:02d}.gif"
        dest_path = GIFS_DIR / filename
        rel_url = f"/stickers/chiikawa/gifs/{filename}"
        
        try:
            req = urllib.request.Request(it["url"], headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
            with open(dest_path, "wb") as f:
                f.write(data)
                
            kb = round(len(data) / 1024, 1)
            print(f" [OK] Saved {filename} ({kb} KB) - {it['title']}")
            
            downloaded.append({
                "id": f"gif_{idx:02d}",
                "filename": filename,
                "url": rel_url,
                "name": it["title"],
                "category": "gif"
            })
        except Exception as e:
            print(f" [!] Failed to download {it['title']}: {e}")

    # Update manifest.json
    if MANIFEST_FILE.exists():
        with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    else:
        manifest = {"pack_id": "chiikawa", "pack_name": "Chiikawa & Friends", "categories": [], "stickers": []}

    # Ensure 'gif' is in categories
    existing_cat_keys = [c["key"] for c in manifest.get("categories", [])]
    if "gif" not in existing_cat_keys:
        # Insert 'gif' right after 'all'
        cats = manifest.get("categories", [])
        if cats and cats[0]["key"] == "all":
            cats.insert(1, {"key": "gif", "name": "GIF (Động)"})
        else:
            cats.append({"key": "gif", "name": "GIF (Động)"})
        manifest["categories"] = cats

    # Remove any old gif entries and append new ones
    current_stickers = [s for s in manifest.get("stickers", []) if not s.get("id", "").startswith("gif_")]
    current_stickers.extend(downloaded)
    manifest["stickers"] = current_stickers
    manifest["total"] = len(current_stickers)

    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"[OK] Manifest updated with {len(downloaded)} animated GIF stickers! Total stickers in pack: {manifest['total']}")

if __name__ == "__main__":
    main()
