"""
place_rocks.py — Geologically-driven rock placement for Blender

Geological model (Mars talus / regolith):
  - Terrain is classified per-vertex by slope angle into three zones:
      flat    ( 0–8°)  : aeolian lag — sparse, tiny rocks only
      talus   (8–30°)  : scree / rockfall accumulation — densest coverage
      outcrop (>30°)   : steep faces shed material downslope; clusters at foot
  - Rocks are placed in clusters, each representing a discrete geological
    "event" (rockfall, ejecta lobe, exposed outcrop).
  - Within a cluster: Gaussian scatter, log-normal size distribution,
    one dominant rock type with minority contamination, shared colour tint.
  - Each rock is ray-cast onto the terrain surface and aligned to the
    local surface normal with a random spin around that normal.

Usage: run from Blender's Scripting workspace.
Requires objects: "Grid" (terrain mesh), collection "rocks" (source assets).
"""

import bpy
import math
import random
import re
import colorsys

from mathutils import Vector, Quaternion

# ── CONFIG ────────────────────────────────────────────────────────────────────

RANDOM_SEED    = 42
TARGET_ROCKS   = 200_000   # total rocks to place
CLUSTER_COUNT  = 600       # number of geological events to simulate

# Object-space scale bounds — tune these to your scene units
SIZE_MIN = 0.00005         # smallest pebble
SIZE_MAX = 0.002           # largest boulder

# Slope thresholds (degrees from vertical)
SLOPE_FLAT_MAX  = 8        # below this → flat plain
SLOPE_TALUS_MAX = 30       # 8–30° → talus / scree; above → steep face

# Cluster scatter radius (scene units)
CLUSTER_RADIUS_MIN = 0.3
CLUSTER_RADIUS_MAX = 6.0

# Per-cluster colour jitter (HSV offsets from a Martian ochre base)
BASE_RGB        = (0.55, 0.43, 0.30)   # warm iron-oxide ochre
HUE_JITTER      = 0.06    # ± hue shift
SAT_JITTER      = 0.18    # ± saturation shift
VAL_JITTER      = 0.22    # ± value shift

# Log-normal spread of rock sizes within a cluster (higher = more variation)
SIZE_LOG_STD = 0.55

# ── TERRAIN ANALYSIS ─────────────────────────────────────────────────────────

def analyse_terrain(terrain_obj):
    """
    Walk every vertex and record world-space position, surface normal,
    and slope angle (0° = flat, 90° = vertical cliff).

    Returns three parallel lists: positions, normals, slopes.
    """
    mesh = terrain_obj.data
    mat  = terrain_obj.matrix_world
    mat3 = mat.to_3x3()

    mesh.calc_normals_split()

    positions, normals, slopes = [], [], []
    up = Vector((0.0, 0.0, 1.0))

    for v in mesh.vertices:
        world_pos = mat @ v.co
        world_nor = (mat3 @ v.normal).normalized()

        # Slope = angle between the surface normal and the global up-axis
        dot       = max(-1.0, min(1.0, world_nor.dot(up)))
        slope_deg = math.degrees(math.acos(dot))

        positions.append(world_pos.copy())
        normals.append(world_nor.copy())
        slopes.append(slope_deg)

    return positions, normals, slopes


# ── GEOLOGICAL ZONE CLASSIFIER ────────────────────────────────────────────────

def zone_of(slope_deg):
    """
    Classify a slope into a geological zone and return:
      (weight, zone_name, size_range, count_range, radius_range)

    Weight is used for weighted-random cluster seed selection so that
    talus zones get proportionally more cluster centres.
    """
    if slope_deg < SLOPE_FLAT_MAX:
        # Aeolian lag / flat regolith: very few rocks, all small
        return (
            0.10, "flat",
            (SIZE_MIN,       SIZE_MIN * 6),   # size range
            (10,  60),                         # rocks per cluster
            (CLUSTER_RADIUS_MIN,
             CLUSTER_RADIUS_MAX * 0.35),
        )
    elif slope_deg < SLOPE_TALUS_MAX:
        # Talus / scree: highest rock density, full size range
        return (
            1.00, "talus",
            (SIZE_MIN * 2,   SIZE_MAX * 0.6),
            (80,  350),
            (CLUSTER_RADIUS_MIN * 1.5,
             CLUSTER_RADIUS_MAX),
        )
    else:
        # Steep outcrop / cliff face: moderate density, larger blocks
        # (material that hasn't slid away yet, or recent rockfall lobe)
        return (
            0.35, "outcrop",
            (SIZE_MIN * 5,   SIZE_MAX),
            (30,  150),
            (CLUSTER_RADIUS_MIN,
             CLUSTER_RADIUS_MAX * 0.55),
        )


# ── CLUSTER GENERATION ────────────────────────────────────────────────────────

def generate_clusters(positions, normals, slopes, n_clusters):
    """
    Weighted-random sample of terrain vertices → cluster descriptors.

    Each cluster represents one geological deposition event.
    """
    weights = [zone_of(s)[0] for s in slopes]
    indices = random.choices(range(len(positions)), weights=weights, k=n_clusters)

    clusters = []
    for idx in indices:
        slope = slopes[idx]
        weight, zone, size_range, count_range, radius_range = zone_of(slope)

        # Each cluster gets a fixed colour seed so all rocks in it share a tint
        colour_seed = random.random()

        clusters.append({
            "center"      : positions[idx],
            "normal"      : normals[idx],
            "zone"        : zone,
            "size_range"  : size_range,
            "count"       : random.randint(*count_range),
            "radius"      : random.uniform(*radius_range),
            "colour_seed" : colour_seed,
        })

    return clusters


# ── COLOUR HELPER ─────────────────────────────────────────────────────────────

def cluster_colour(colour_seed):
    """
    Derive a slightly-shifted RGBA from the Martian base colour using the
    cluster's fixed random seed.  Rocks sharing a cluster share a tint,
    giving the impression of a coherent geological unit.
    """
    rng = random.Random(int(colour_seed * 2**31))
    h0, s0, v0 = colorsys.rgb_to_hsv(*BASE_RGB)

    h = (h0 + rng.uniform(-HUE_JITTER, HUE_JITTER)) % 1.0
    s = max(0.0, min(1.0, s0 + rng.uniform(-SAT_JITTER, SAT_JITTER)))
    v = max(0.0, min(1.0, v0 + rng.uniform(-VAL_JITTER, VAL_JITTER)))

    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (r, g, b, 1.0)


# ── NORMAL-ALIGNED ROTATION ───────────────────────────────────────────────────

def rotation_on_normal(world_normal):
    """
    Build a rotation Euler that aligns the object's +Z to world_normal,
    then spins it randomly around that normal (random yaw).
    """
    z_axis = Vector((0.0, 0.0, 1.0))
    axis   = z_axis.cross(world_normal)

    if axis.length > 1e-6:
        axis.normalize()
        tilt_angle = z_axis.angle(world_normal)
        q_tilt = Quaternion(axis, tilt_angle)
    else:
        q_tilt = Quaternion()   # normal is already up — identity

    q_spin = Quaternion(world_normal, random.uniform(0.0, 2.0 * math.pi))
    return (q_spin @ q_tilt).to_euler()


# ── ROCK PLACEMENT ────────────────────────────────────────────────────────────

def place_rocks(clusters, stones, terrain_obj, target):
    """
    Iterate clusters and scatter rocks until `target` is reached.

    For each rock:
      1. Gaussian-scatter a 2-D offset around the cluster centre.
      2. Ray-cast straight down onto the terrain to find the exact surface hit.
      3. Align rock to hit normal + random spin.
      4. Log-normal size draw biased to the cluster's size range.
      5. Apply per-cluster colour via object.color.
    """
    collection = bpy.context.collection

    # Scale cluster counts so they sum to exactly TARGET_ROCKS
    total_wanted = sum(c["count"] for c in clusters)
    scale        = target / max(total_wanted, 1)

    # Pre-compute world→local matrices once (used for ray_cast which wants
    # coordinates in object local space)
    mat_inv  = terrain_obj.matrix_world.inverted()
    mat3_inv = terrain_obj.matrix_world.to_3x3().inverted()
    mat3     = terrain_obj.matrix_world.to_3x3()

    placed = 0

    for cluster in clusters:
        if placed >= target:
            break

        cx, cy, cz  = cluster["center"]
        radius      = cluster["radius"]
        size_lo, size_hi = cluster["size_range"]
        zone        = cluster["zone"]
        colour      = cluster_colour(cluster["colour_seed"])
        count       = max(1, int(cluster["count"] * scale))

        # One dominant rock type per cluster; 20 % chance of contamination
        dominant = stones[random.randrange(len(stones))]
        pool = [dominant] * 4 + stones   # 4:1 bias toward dominant type

        # Log-normal centre point = geometric mean of the cluster's size range
        size_log_mean = (math.log(size_lo) + math.log(size_hi)) / 2.0

        for _ in range(count):
            if placed >= target:
                break

            # ── 1. Scatter position ──────────────────────────────────────
            # Gaussian with σ = 40 % of radius gives a natural dropoff
            ox = random.gauss(0.0, radius * 0.4)
            oy = random.gauss(0.0, radius * 0.4)
            rx, ry = cx + ox, cy + oy

            # ── 2. Ray-cast onto terrain surface ────────────────────────
            ray_origin_world = Vector((rx, ry, cz + 100.0))
            ray_dir_world    = Vector((0.0, 0.0, -1.0))

            hit, hit_loc_local, hit_nor_local, _ = terrain_obj.ray_cast(
                mat_inv  @ ray_origin_world,
                mat3_inv @ ray_dir_world,
            )

            if not hit:
                # Scattered outside mesh bounds — skip rather than float
                continue

            world_loc = terrain_obj.matrix_world @ hit_loc_local
            world_nor = (mat3 @ hit_nor_local).normalized()

            # ── 3. Pick and copy rock ────────────────────────────────────
            rock     = pool[random.randrange(len(pool))]
            new_rock = rock.copy()
            new_rock.data = rock.data.copy()

            # ── 4. Log-normal size ───────────────────────────────────────
            s = math.exp(random.gauss(size_log_mean, SIZE_LOG_STD))
            s = max(SIZE_MIN, min(SIZE_MAX, s))

            new_rock.scale    = (s, s, s)
            new_rock.location = world_loc

            # ── 5. Surface-normal alignment ──────────────────────────────
            new_rock.rotation_euler = rotation_on_normal(world_nor)

            # ── 6. Per-cluster colour ────────────────────────────────────
            # Visible when the material's shader uses an Object Info ▸ Color node
            new_rock.color = colour

            new_rock.name = f"{rock.name}_{placed}_generated"
            collection.objects.link(new_rock)
            placed += 1

    return placed


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    random.seed(RANDOM_SEED)

    # ── Gather terrain ───────────────────────────────────────────────────────
    terrain = bpy.data.objects.get("Grid")
    if terrain is None:
        raise RuntimeError("No object named 'Grid' found in the scene.")

    # ── Gather source rocks ──────────────────────────────────────────────────
    rocks_col = bpy.data.collections.get("rocks")
    if rocks_col is None:
        raise RuntimeError("No collection named 'rocks' found.")

    stones = [
        obj for obj in rocks_col.objects
        if not re.match(r"^.*_generated", obj.name)
    ]
    if not stones:
        raise RuntimeError("No source rock assets found in 'rocks' collection.")

    print(f"Rock assets   : {len(stones)}")

    # ── Terrain analysis ─────────────────────────────────────────────────────
    print("Analysing terrain slopes…")
    positions, normals, slopes = analyse_terrain(terrain)
    print(f"Terrain verts : {len(positions)}")

    flat_ct   = sum(1 for s in slopes if s < SLOPE_FLAT_MAX)
    talus_ct  = sum(1 for s in slopes if SLOPE_FLAT_MAX <= s < SLOPE_TALUS_MAX)
    steep_ct  = sum(1 for s in slopes if s >= SLOPE_TALUS_MAX)
    total_v   = len(slopes)
    print(f"  flat    {flat_ct:>6} verts ({100*flat_ct/total_v:.1f}%)")
    print(f"  talus   {talus_ct:>6} verts ({100*talus_ct/total_v:.1f}%)")
    print(f"  outcrop {steep_ct:>6} verts ({100*steep_ct/total_v:.1f}%)")

    # ── Cluster generation ───────────────────────────────────────────────────
    print(f"\nGenerating {CLUSTER_COUNT} geological clusters…")
    clusters = generate_clusters(positions, normals, slopes, CLUSTER_COUNT)

    zone_summary = {}
    for c in clusters:
        zone_summary[c["zone"]] = zone_summary.get(c["zone"], 0) + 1
    print(f"  Cluster zones: {zone_summary}")

    # ── Place rocks ──────────────────────────────────────────────────────────
    print(f"\nPlacing rocks (target {TARGET_ROCKS:,})…")
    placed = place_rocks(clusters, stones, terrain, TARGET_ROCKS)
    print(f"Done — placed {placed:,} rocks")


main()
