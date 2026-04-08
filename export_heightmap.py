import rasterio
import numpy as np
from rasterio.windows import Window
from PIL import Image

x1, y1, x2, y2 = 1526, 5266, 2024, 5764

with rasterio.open("data/raw/new/DTEEC_060706_2195_060416_2195_A01.IMG") as src:
    window = Window(x1, y1, x2 - x1, y2 - y1)
    patch = src.read(1, window=window)
    nodata = src.nodata
    transform = src.window_transform(window)

    patch = patch.astype(np.float32)
    patch[patch == nodata] = np.nan

    print(f"Patch shape: {patch.shape}")
    print(f"Elevation range: {np.nanmin(patch):.2f} to {np.nanmax(patch):.2f} m")
    print(f"NaN pixels: {np.isnan(patch).sum()}")

    elev_min = np.nanmin(patch)
    elev_max = np.nanmax(patch)
    elev_range = elev_max - elev_min

    normalized = (patch - elev_min) / elev_range
    heightmap = (normalized * 65535).astype(np.uint16)

    img = Image.fromarray(heightmap.astype(np.int32), mode='I')
    img.save("data/processed/patch_02_heightmap.png")

    profile = src.profile.copy()
    profile.update(driver='GTiff', width=x2-x1, height=y2-y1, transform=transform, dtype='float32')
    with rasterio.open("data/processed/patch_02.tif", "w", **profile) as dst:
        dst.write(patch, 1)

print(f"Elevation range: {elev_range:.2f}m")
print("Saved patch_02")