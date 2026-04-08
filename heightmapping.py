import rasterio
import numpy as np
from PIL import Image

with rasterio.open("data/processed/patch_01.tif") as src:
    patch = src.read(1).astype(np.float32)

elev_min = np.nanmin(patch)
elev_max = np.nanmax(patch)
elev_range = elev_max - elev_min

# Normalize to 0-65535
normalized = (patch - elev_min) / elev_range
heightmap_16bit = (normalized * 65535).astype(np.uint16)

img = Image.fromarray(heightmap_16bit, mode='I;16')
img.save("data/processed/patch_01_heightmap.png")

print(f"Elevation min: {elev_min:.2f}m")
print(f"Elevation max: {elev_max:.2f}m")
print(f"Elevation range: {elev_range:.2f}m")
print("Saved heightmap")
