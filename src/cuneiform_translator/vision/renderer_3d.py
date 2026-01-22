"""
3D visualization and rendering utilities for cuneiform tablets.

Provides tools to visualize PLY models, render depth maps,
and create publication-quality 3D renderings.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class TabletRenderer:
    """Render 3D tablet models to images."""

    def __init__(self, resolution: Tuple[int, int] = (1024, 768)):
        """
        Initialize renderer.

        Args:
            resolution: Output resolution (width, height)
        """
        self.resolution = resolution

    def render_depth_shaded(
        self,
        model_3d,  # PLYModel instance
        output_path: Path,
        colormap: str = "viridis",
    ) -> bool:
        """
        Render model with depth shading.

        Args:
            model_3d: PLYModel instance
            output_path: Output image file
            colormap: Matplotlib colormap name

        Returns:
            True if successful
        """
        try:
            import cv2
            import matplotlib.pyplot as plt

            depth_map = model_3d.extract_depth_map(
                resolution=max(self.resolution), method="height"
            )

            if depth_map is None:
                return False

            # Resize to target resolution
            depth_map_resized = cv2.resize(
                depth_map,
                self.resolution,
                interpolation=cv2.INTER_LINEAR,
            )

            # Apply colormap
            cmap = plt.get_cmap(colormap)
            colored = cmap(depth_map_resized / 255.0)
            colored_uint8 = (colored[:, :, :3] * 255).astype(np.uint8)
            colored_bgr = cv2.cvtColor(colored_uint8, cv2.COLOR_RGB2BGR)

            # Save
            cv2.imwrite(str(output_path), colored_bgr)
            logger.info(f"Saved depth-shaded rendering to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Rendering failed: {e}")
            return False

    def render_normal_mapped(
        self,
        model_3d,
        output_path: Path,
    ) -> bool:
        """
        Render with normal mapping (simulated lighting).

        Args:
            model_3d: PLYModel instance
            output_path: Output image file

        Returns:
            True if successful
        """
        try:
            import cv2

            if model_3d.vertices is None:
                return False

            # Compute normals for vertices
            normals = np.zeros_like(model_3d.vertices)

            if model_3d.faces:
                for face in model_3d.faces:
                    if len(face) >= 3:
                        v0 = model_3d.vertices[face[0]]
                        v1 = model_3d.vertices[face[1]]
                        v2 = model_3d.vertices[face[2]]

                        edge1 = v1 - v0
                        edge2 = v2 - v0
                        face_normal = np.cross(edge1, edge2)
                        face_normal = face_normal / (np.linalg.norm(face_normal) + 1e-8)

                        for vertex_idx in face[:3]:
                            normals[vertex_idx] += face_normal

            # Normalize
            normals = normals / (np.linalg.norm(normals, axis=1, keepdims=True) + 1e-8)

            # Light direction
            light_dir = np.array([0.5, 0.5, 1.0])
            light_dir = light_dir / np.linalg.norm(light_dir)

            # Compute shading
            shading = np.clip(np.dot(normals, light_dir), 0, 1)

            # Create image (project to 2D)
            min_corner, max_corner = model_3d.compute_bounds()
            shading_map = np.zeros(self.resolution, dtype=np.float32)

            for i, vertex in enumerate(model_3d.vertices):
                x_norm = (vertex[0] - min_corner[0]) / (max_corner[0] - min_corner[0])
                y_norm = (vertex[1] - min_corner[1]) / (max_corner[1] - min_corner[1])

                px = int(x_norm * (self.resolution[0] - 1))
                py = int(y_norm * (self.resolution[1] - 1))

                if 0 <= px < self.resolution[0] and 0 <= py < self.resolution[1]:
                    shading_map[py, px] = max(shading_map[py, px], shading[i])

            # Convert to image
            shading_uint8 = (shading_map * 255).astype(np.uint8)
            shading_bgr = cv2.cvtColor(shading_uint8, cv2.COLOR_GRAY2BGR)

            cv2.imwrite(str(output_path), shading_bgr)
            logger.info(f"Saved normal-mapped rendering to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Normal mapping failed: {e}")
            return False

    def render_composite(
        self,
        model_3d,
        photo_path: Path,
        output_path: Path,
        blend_alpha: float = 0.3,
    ) -> bool:
        """
        Composite 3D rendering with photograph.

        Args:
            model_3d: PLYModel instance
            photo_path: Original tablet photograph
            output_path: Output composite image
            blend_alpha: Blend weight for 3D layer

        Returns:
            True if successful
        """
        try:
            import cv2

            # Load photo
            photo = cv2.imread(str(photo_path))
            if photo is None:
                logger.error(f"Cannot load photo: {photo_path}")
                return False

            # Render depth map
            depth_map = model_3d.extract_depth_map(
                resolution=max(self.resolution), method="height"
            )
            if depth_map is None:
                return False

            # Resize
            depth_resized = cv2.resize(depth_map, self.resolution[::-1])

            # Create colored depth
            depth_3channel = cv2.cvtColor(depth_resized, cv2.COLOR_GRAY2BGR)

            # Blend
            composite = cv2.addWeighted(photo, 1 - blend_alpha, depth_3channel, blend_alpha, 0)

            cv2.imwrite(str(output_path), composite)
            logger.info(f"Saved composite rendering to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Composite rendering failed: {e}")
            return False

    def render_comparison(
        self,
        model_3d,
        photo_path: Path,
        output_dir: Path,
    ) -> bool:
        """
        Create side-by-side comparison of photo and 3D rendering.

        Args:
            model_3d: PLYModel instance
            photo_path: Original photograph
            output_dir: Output directory

        Returns:
            True if successful
        """
        try:
            import cv2

            output_dir.mkdir(parents=True, exist_ok=True)

            # Load photo
            photo = cv2.imread(str(photo_path))
            if photo is None:
                return False

            # Render depth
            depth_map = model_3d.extract_depth_map(max(self.resolution))
            if depth_map is None:
                return False

            depth_resized = cv2.resize(depth_map, (photo.shape[1], photo.shape[0]))
            depth_3channel = cv2.cvtColor(depth_resized, cv2.COLOR_GRAY2BGR)

            # Create comparison
            comparison = np.hstack([photo, depth_3channel])

            # Add labels
            cv2.putText(
                comparison,
                "Original Photo",
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.5,
                (0, 255, 0),
                2,
            )
            cv2.putText(
                comparison,
                "3D Depth Map",
                (photo.shape[1] + 50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.5,
                (0, 255, 0),
                2,
            )

            # Save
            output_path = output_dir / f"{photo_path.stem}_comparison.jpg"
            cv2.imwrite(str(output_path), comparison)
            logger.info(f"Saved comparison to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Comparison rendering failed: {e}")
            return False


def main():
    """CLI for 3D visualization."""
    import argparse

    from .model_3d import PLYModel

    parser = argparse.ArgumentParser(description="3D tablet rendering")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Depth shading
    depth_parser = subparsers.add_parser(
        "depth-shaded", help="Render with depth shading"
    )
    depth_parser.add_argument("--ply", type=Path, required=True, help="PLY file")
    depth_parser.add_argument("--output", type=Path, required=True, help="Output image")
    depth_parser.add_argument("--colormap", type=str, default="viridis")
    depth_parser.add_argument("--resolution", type=int, default=640)

    # Normal mapping
    normal_parser = subparsers.add_parser("normal-map", help="Render normal mapped")
    normal_parser.add_argument("--ply", type=Path, required=True, help="PLY file")
    normal_parser.add_argument("--output", type=Path, required=True, help="Output image")
    normal_parser.add_argument("--resolution", type=int, default=640)

    # Composite
    comp_parser = subparsers.add_parser("composite", help="Blend with photograph")
    comp_parser.add_argument("--ply", type=Path, required=True, help="PLY file")
    comp_parser.add_argument("--photo", type=Path, required=True, help="Photo file")
    comp_parser.add_argument("--output", type=Path, required=True, help="Output image")
    comp_parser.add_argument(
        "--alpha", type=float, default=0.3, help="3D blend weight"
    )

    # Comparison
    cmp_parser = subparsers.add_parser("compare", help="Create comparison image")
    cmp_parser.add_argument("--ply", type=Path, required=True, help="PLY file")
    cmp_parser.add_argument("--photo", type=Path, required=True, help="Photo file")
    cmp_parser.add_argument(
        "--output-dir", type=Path, required=True, help="Output directory"
    )

    args = parser.parse_args()

    model = PLYModel(args.ply)
    if not model.load():
        print("Failed to load PLY file")
        return

    model.normalize(scale=1.0)
    renderer = TabletRenderer()

    if args.command == "depth-shaded":
        renderer.render_depth_shaded(model, args.output, args.colormap)

    elif args.command == "normal-map":
        renderer.render_normal_mapped(model, args.output)

    elif args.command == "composite":
        renderer.render_composite(model, args.photo, args.output, args.alpha)

    elif args.command == "compare":
        renderer.render_comparison(model, args.photo, args.output_dir)


if __name__ == "__main__":
    main()
