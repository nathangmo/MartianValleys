import rasterio
import numpy as np

with rasterio.open("data/raw/new/DTEEC_060706_2195_060416_2195_A01.IMG") as src:
    print("CRS:", src.crs)
    print("Resolution:", src.res)
    print("Shape:", src.shape)
    print("Bounds:", src.bounds)
    print("NoData:", src.nodata)

# import rasterio
# import numpy as np
# import matplotlib.pyplot as plt

# with rasterio.open("data/raw/new/DTEEC_060706_2195_060416_2195_A01.IMG") as src:
#     # Read downsampled for preview
#     data = src.read(1, out_shape=(512, 512))
#     nodata = src.nodata
#     data = np.where(data == nodata, np.nan, data)

# plt.figure(figsize=(10, 10))
# plt.imshow(data, cmap='gray')
# plt.colorbar(label='Elevation (m)')
# plt.title('HiRISE DTM Preview')
# plt.savefig('dtm_preview.png', dpi=150)
# plt.show()

# # Approximate preview coords of selected patch
# preview_x1, preview_y1 = 150, 550
# preview_x2, preview_y2 = 350, 750

# scale_x = 6824 / 512
# scale_y = 10086 / 512

# full_x1 = int(preview_x1 * scale_x)
# full_y1 = int(preview_y1 * scale_y)
# full_x2 = int(preview_x2 * scale_x)
# full_y2 = int(preview_y2 * scale_y)

# print(f"Full DTM crop: ({full_x1}, {full_y1}) to ({full_x2}, {full_y2})")
# print(f"Patch size: {full_x2-full_x1} x {full_y2-full_y1} pixels")
# print(f"Real world size: {(full_x2-full_x1)*1.0027:.0f} x {(full_y2-full_y1)*1.0027:.0f} meters")

import rasterio
import numpy as np
import matplotlib.pyplot as plt

with rasterio.open("data/raw/new/DTEEC_060706_2195_060416_2195_A01.IMG") as src:
    data = src.read(1, out_shape=(1024, 692))  # maintain aspect ratio
    nodata = src.nodata
    data = np.where(data == nodata, np.nan, data)

fig, ax = plt.subplots(figsize=(8, 12))
ax.imshow(data, cmap='terrain')
ax.set_title('HiRISE DTM - pick crop region')
# Draw a 500x500 pixel example box in the middle for scale reference
ax.add_patch(plt.Rectangle((180, 560), 50, 50, fill=False, edgecolor='red', linewidth=2))
ax.text(200, 395, '~500m', color='red', fontsize=10)
plt.savefig('dtm_pick2.png', dpi=150)
plt.show()

# Preview coords to full DTM pixel coords
preview_cx, preview_cy = 180, 560

scale_x = 6824 / 692
scale_y = 10086 / 1024

full_cx = int(preview_cx * scale_x)
full_cy = int(preview_cy * scale_y)

patch_size_px = int(500 / 1.0027)
half = patch_size_px // 2

x1 = full_cx - half
y1 = full_cy - half
x2 = full_cx + half
y2 = full_cy + half

print(f"Center in full DTM: ({full_cx}, {full_cy})")
print(f"Crop window: ({x1}, {y1}) to ({x2}, {y2})")
print(f"Real world: {(x2-x1)*1.0027:.0f} x {(y2-y1)*1.0027:.0f} meters")