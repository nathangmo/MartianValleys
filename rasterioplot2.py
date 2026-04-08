import rasterio
import numpy as np
import matplotlib.pyplot as plt

with rasterio.open("data/processed/patch_01.tif") as src:
    patch = src.read(1)

plt.figure(figsize=(8, 8))
plt.imshow(patch, cmap='terrain')
plt.colorbar(label='Elevation (m)')
plt.title('Patch 01 - 499x499m')
plt.savefig('data/processed/patch_01_preview.png', dpi=150)
plt.show()