#!/usr/bin/env python3
"""Bake EXIF orientation into the pixel data for all BTFP photos.

GL flagged twisting-mirabel.png as rotated 90 degrees in the browser.
Root cause: image file has an EXIF orientation tag the browser ignores
(common with iPhone photos saved as PNG). PIL.ImageOps.exif_transpose()
applies the rotation and removes the tag so all viewers display it the
same way.

Idempotent — files without an orientation tag are left untouched.
"""
from pathlib import Path
from PIL import Image, ImageOps

BTFP_DIR = Path(__file__).resolve().parent.parent.parent / "apps" / "locally_twisted" / "locally_twisted" / "public" / "images" / "btfp"

EXTS = {".jpg", ".jpeg", ".png"}


def main():
    if not BTFP_DIR.exists():
        print(f"missing: {BTFP_DIR}")
        return
    files = sorted(p for p in BTFP_DIR.rglob("*") if p.suffix.lower() in EXTS)
    print(f"Scanning {len(files)} files...\n")

    fixed_count = 0
    for f in files:
        rel = f.relative_to(BTFP_DIR)
        with Image.open(f) as img:
            before_size = img.size
            try:
                exif = img.getexif()
                orientation = exif.get(0x0112)
            except Exception:
                orientation = None
            transposed = ImageOps.exif_transpose(img)
            after_size = transposed.size
            changed = before_size != after_size or (orientation and orientation != 1)
            if changed:
                # Re-save in the original format. Strip EXIF so no future tool
                # can re-apply the (now-baked-in) rotation.
                save_kwargs = {}
                if f.suffix.lower() in {".jpg", ".jpeg"}:
                    save_kwargs["quality"] = 92
                    save_kwargs["optimize"] = True
                    save_kwargs["exif"] = b""
                elif f.suffix.lower() == ".png":
                    save_kwargs["optimize"] = True
                transposed.save(f, **save_kwargs)
                print(f"  FIXED  {rel}  (orientation={orientation}, {before_size} -> {after_size})")
                fixed_count += 1
            else:
                print(f"  ok     {rel}  ({before_size})")
    print(f"\nDone. {fixed_count} of {len(files)} files needed rotation baked in.")


if __name__ == "__main__":
    main()
