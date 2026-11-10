"""Builds a small ready-to-upload copy of the project in ./deploy
Usage:  python make_chips_list.py     (if you changed the chips)
        python optimize_images.py     (add --quantize for even smaller PNGs)
Then upload the 'deploy' folder to Netlify. Your originals are never touched.
Needs Pillow:  pip install pillow"""
import os, shutil, sys
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "deploy")
MAX = {"chips": 384, "trainers": 256, "badges": 128}      # longest side in px (they display at ~70-130px)
SKIP = {"deploy", ".git", "node_modules", "__pycache__", "make_chips_list.py", "optimize_images.py", "README.md"}
QUANT = "--quantize" in sys.argv

def size(path):
    return sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(path) for f in fs)

shutil.rmtree(OUT, ignore_errors=True)
BEFORE = size(ROOT)
for d, dirs, files in os.walk(ROOT):
    dirs[:] = [x for x in dirs if x not in SKIP]
    rel = os.path.relpath(d, ROOT)
    top = rel.split(os.sep)[0]
    os.makedirs(os.path.join(OUT, rel), exist_ok=True)
    for f in files:
        if f in SKIP:
            continue
        src, dst = os.path.join(d, f), os.path.join(OUT, rel, f)
        ext = f.lower().rsplit(".", 1)[-1]
        if top in MAX and ext in ("png", "jpg", "jpeg", "webp"):
            im = Image.open(src)
            im.thumbnail((MAX[top], MAX[top]), Image.LANCZOS)
            if ext == "png":
                if QUANT:
                    im = im.convert("RGBA").quantize(256, method=Image.FASTOCTREE)
                im.save(dst, optimize=True)
            else:
                im.save(dst, quality=85)
        else:
            shutil.copy2(src, dst)
print(f"before: {BEFORE/1e6:.1f} MB   after: {size(OUT)/1e6:.1f} MB   (upload the deploy folder)")
