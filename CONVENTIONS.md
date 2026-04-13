# Project Conventions

This document pins the conventions that all code, scripts, and assets in this
repository must follow. Any deviation requires an explicit update here first.

---

## Coordinate Frame

- **Z-up, right-handed, X-forward**
- X axis: forward (rover heading / scene north)
- Y axis: left
- Z axis: up (away from terrain)
- Applies to: Blender scenes, exported meshes, camera poses, Gazebo worlds

## Scale

- **1 Blender unit = 1 metre**
- All distances, elevations, and displacements stored in SI metres unless the
  file extension or variable name explicitly states otherwise (e.g. `_px` for
  pixels, `_deg` for degrees).

## Camera Convention

- **OpenCV** — image origin at top-left, X right, Y down, Z into the scene
- Intrinsic matrix K follows the standard OpenCV layout:

  ```
  K = [[fx,  0, cx],
       [ 0, fy, cy],
       [ 0,  0,  1]]
  ```

- Extrinsics: world-to-camera transform `[R | t]` such that
  `x_cam = R @ x_world + t`
- This convention is used for both aerial and rover cameras.

## Sample Naming

- Each generated sample lives in its own subdirectory:
  `outputs/samples/sample_XXXXX/`
  where `XXXXX` is a zero-padded five-digit integer (e.g. `sample_00001`).
- Within each sample directory the layout is fixed — see `configs/export.yaml`
  for filenames.

## Branch / File Naming

- Python modules: `snake_case`
- Config keys: `snake_case`
- Blender collections and objects: `PascalCase`
- Constants in Python: `UPPER_SNAKE_CASE`

## Out of Scope

The following are explicitly **out of scope for WP1** and must not be added:

- Neural network architecture or training code
- DEM completion or inpainting logic
- Depth estimation models
- Cross-attention or any learned fusion mechanism
