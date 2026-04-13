# MartianValleys — WP1: Synthetic Data Pipeline

## Scope

Build a reproducible pipeline that converts HiRISE-based terrain plus
procedural rock augmentation into synthetic paired aerial and rover
observations, with configurable nominal sensors, basic appearance modeling,
structured sample export, and initial simulator interoperability.

This repository covers **WP1 only**. Network training, DEM completion,
depth estimation, and cross-attention fusion are explicitly out of scope.

---

## WP1 Deliverables

| ID | Deliverable | Status |
|----|-------------|--------|
| D1 | Reproducible terrain scene generation (HiRISE import, metric mesh, rock placement, terrain metadata) | In progress |
| D2 | Basic Mars-like appearance (materials, lighting) | Pending |
| D3 | Nominal aerial and rover sensor models from config | Pending |
| D4 | One complete synthetic sample on disk | Pending |
| D5 | Small batch generation from CLI | Pending |
| D6 | Export sanity check for Gazebo | Pending |

---

## Repository Layout

```
configs/          YAML configuration files (terrain, sensors, rendering, export)
data/
  raw/            Raw HiRISE DTM files — NOT tracked in git
  processed/      Intermediate rasters — NOT tracked in git
outputs/
  samples/        Generated sample directories (sample_XXXXX/) — NOT tracked in git
scripts/          Stand-alone CLI utilities (inspect_dtm, etc.)
src/
  terrain/        HiRISE loader, rock placement
  scene/          Blender scene assembly
  sensors/        Camera model utilities
  dataset/        GT DEM rasterization, sample writer
  utils/          Shared helpers
tests/            Unit and integration tests
CONVENTIONS.md    Coordinate frame, scale, camera convention, naming rules
```

---

## Quick Start

### Prerequisites

```bash
pip install -r requirements.txt
```

Blender scripts require Blender >= 3.6 with its bundled Python.

### Inspect the raw DTM

```bash
python scripts/inspect_dtm.py data/raw/new/DTEEC_060706_2195_060416_2195_A01.IMG
```

---

## Key Conventions

See `CONVENTIONS.md` for the full specification. Summary:

- **Coordinate frame**: Z-up, right-handed, X-forward
- **Scale**: 1 Blender unit = 1 metre
- **Camera**: OpenCV convention
- **Sample naming**: `sample_XXXXX` (zero-padded five-digit index)

---

## Open Decisions

The following have not yet been resolved and are flagged in the config files:

- Aerial camera model: nadir orthophoto vs. perspective UAV
- GT DEM rock policy: bare terrain vs. full surface height map
