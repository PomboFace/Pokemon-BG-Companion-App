"""Run this after adding or removing chip images: python make_chips_list.py
Writes chips/chips.json, which the app reads to know which Pokemon can be searched."""
import json, os
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chips")
files = sorted(f for f in os.listdir(d)
               if f.lower().endswith((".png", ".webp", ".jpg", ".jpeg")) and f[:1].isdigit())
with open(os.path.join(d, "chips.json"), "w") as out:
    json.dump(files, out, indent=1)
print(len(files), "chips listed in chips/chips.json")
