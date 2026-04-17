from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import rasterio


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/inspect_dtm.py <path_to_dtm>")
        sys.exit(1)

    dtm_path = Path(sys.argv[1])
    if not dtm_path.exists():
        raise FileNotFoundError(f"File not found: {dtm_path}")

    with rasterio.open(dtm_path) as src:
        dem = src.read(1)
        transform = src.transform
        nodata = src.nodata
        width = src.width
        height = src.height

    valid = dem if nodata is None else dem[dem != nodata]
    valid = valid[np.isfinite(valid)]

    if valid.size == 0:
        raise ValueError("No valid elevation values found.")

    pixel_x = transform.a
    pixel_y = abs(transform.e)

    print(f"File: {dtm_path}")
    print(f"Shape: {height} x {width}")
    print(f"Pixel size: {pixel_x:.6f} m x {pixel_y:.6f} m")
    print(f"Min elevation: {valid.min():.3f} m")
    print(f"Max elevation: {valid.max():.3f} m")
    print(f"Elevation range: {valid.max() - valid.min():.3f} m")
    print(f"NoData: {nodata}")

    plt.figure(figsize=(8, 8))
    plt.imshow(dem, cmap="terrain")
    plt.colorbar(label="Elevation")
    plt.title(dtm_path.name)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()