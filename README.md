MartianValleys/
├── README.md
├── pyproject.toml
├── configs/
│   ├── terrain/
│   │   ├── hirise_base.yaml
│   │   ├── rocky_dense.yaml
│   │   └── rocky_sparse.yaml
│   ├── sensors/
│   │   ├── aerial_nominal.yaml
│   │   └── rover_stereo_nominal.yaml
│   ├── rendering/
│   │   ├── debug.yaml
│   │   └── dataset.yaml
│   └── export/
│       └── gazebo.yaml
├── src/
│   ├── terrain/
│   │   ├── hirise_loader.py
│   │   ├── mesh_builder.py
│   │   ├── rock_placement.py
│   │   └── materials.py
│   ├── scene/
│   │   ├── blender_scene.py
│   │   ├── lighting.py
│   │   └── frames.py
│   ├── sensors/
│   │   ├── aerial_camera.py
│   │   ├── stereo_camera.py
│   │   └── camera_utils.py
│   ├── render/
│   │   ├── render_rgb.py
│   │   ├── render_depth.py
│   │   └── render_sample.py
│   ├── export/
│   │   ├── usd_export.py
│   │   ├── gazebo_export.py
│   │   └── metadata_export.py
│   ├── dataset/
│   │   ├── sample_schema.py
│   │   ├── writer.py
│   │   └── validation.py
│   └── cli/
│       ├── build_scene.py
│       ├── render_sample.py
│       └── batch_generate.py
├── scripts/
│   ├── test_one_sample.sh
│   └── export_to_gazebo.sh
└── outputs/

