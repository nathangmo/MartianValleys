import rasterio
import numpy as np
from rasterio.windows import Window

x1, y1, x2, y2 = 1200, 5050, 1698, 5548

with rasterio.open("data/raw/new/DTEEC_060706_2195_060416_2195_A01.IMG") as src:
    window = Window(x1, y1, x2 - x1, y2 - y1)
    patch = src.read(1, window=window)
    nodata = src.nodata
    transform = src.window_transform(window)

    # Replace nodata with nan
    patch = patch.astype(np.float32)
    patch[patch == nodata] = np.nan

    print(f"Patch shape: {patch.shape}")
    print(f"Elevation range: {np.nanmin(patch):.2f} to {np.nanmax(patch):.2f} m")
    print(f"NaN pixels: {np.isnan(patch).sum()}")

    # Save as GeoTIFF for later use
    profile = src.profile.copy()
    profile.update(
    driver='GTiff',
    width=x2-x1,
    height=y2-y1,
    transform=transform,
    dtype='float32'
)
    with rasterio.open("data/processed/patch_01.tif", "w", **profile) as dst:
        dst.write(patch, 1)

print("Saved to data/processed/patch_01.tif")