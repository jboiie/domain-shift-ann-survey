import glob
import sys
from PIL import Image

d = sys.argv[1] if len(sys.argv) > 1 else "ref/pages"
for f in sorted(glob.glob(f"{d}/*.emf")):
    im = Image.open(f)
    im.load(dpi=110)
    im.convert("RGB").save(f[:-4] + ".png")
print("converted", len(glob.glob(f"{d}/*.png")))
