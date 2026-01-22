"""
3D model processing for cuneiform tablets.

Supports loading PLY files (from GigaMesh or other sources),
extracting depth maps, and generating synthetic training data
through rendering and augmentation.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class PLYModel:
    """Load and process PLY (polygon) 3D models."""

    def __init__(self, filepath: Path):
        """
        Load PLY file.

        Args:
            filepath: Path to .ply file
        """
        self.filepath = Path(filepath)
        self.vertices = None
        self.faces = None
        self.normals = None
        self.colors = None

    def load(self) -> bool:
        """
        Load PLY file with vertex and face data.

        Returns:
            True if successful
        """
        if not self.filepath.exists():
            logger.error(f"PLY file not found: {self.filepath}")
            return False

        try:
            import struct

            with open(self.filepath, "rb") as f:
                # Read header
                header_lines = []
                line = f.readline().decode("utf-8").strip()

                if line != "ply":
                    logger.error("Not a valid PLY file (missing 'ply' header)")
                    return False

                vertex_count = 0
                face_count = 0
                vertex_properties = []
                is_binary = False
                byte_order = "little"

                while True:
                    line = f.readline().decode("utf-8").strip()
                    header_lines.append(line)

                    if line.startswith("format"):
                        if "binary_little_endian" in line:
                            is_binary = True
                            byte_order = "little"
                        elif "binary_big_endian" in line:
                            is_binary = True
                            byte_order = "big"
                    elif line.startswith("element vertex"):
                        vertex_count = int(line.split()[-1])
                    elif line.startswith("element face"):
                        face_count = int(line.split()[-1])
                    elif line.startswith("property"):
                        if header_lines[-2].startswith("element vertex"):
                            vertex_properties.append(line.split()[1])
                    elif line == "end_header":
                        break

                # Read vertex data
                if vertex_count > 0:
                    vertices = []

                    for _ in range(vertex_count):
                        if is_binary:
                            # Read binary vertex (x, y, z as floats)
                            data = f.read(12)
                            x, y, z = struct.unpack(
                                f"{'<' if byte_order == 'little' else '>'}3f", data
                            )
                            vertices.append([x, y, z])

                            # Skip additional properties if they exist
                            for prop in vertex_properties[3:]:
                                if prop in ["nx", "ny", "nz"]:
                                    f.read(4)
                                elif prop in ["red", "green", "blue"]:
                                    f.read(1)
                        else:
                            # ASCII format
                            line = f.readline().decode("utf-8").strip()
                            parts = line.split()
                            vertices.append([float(p) for p in parts[:3]])

                    self.vertices = np.array(vertices, dtype=np.float32)
                    logger.info(f"Loaded {len(vertices)} vertices")

                # Read face data
                if face_count > 0:
                    faces = []

                    for _ in range(face_count):
                        if is_binary:
                            count = struct.unpack(
                                f"{'<' if byte_order == 'little' else '>'}B",
                                f.read(1),
                            )[0]
                            indices = struct.unpack(
                                f"{'<' if byte_order == 'little' else '>'}{'I' * count}",
                                f.read(count * 4),
                            )
                            faces.append(indices)
                        else:
                            line = f.readline().decode("utf-8").strip()
                            parts = line.split()
                            count = int(parts[0])
                            indices = [int(p) for p in parts[1 : count + 1]]
                            faces.append(indices)

                    self.faces = faces
                    logger.info(f"Loaded {len(faces)} faces")

                return True

        except Exception as e:
            logger.error(f"Failed to load PLY file: {e}")
            return False

    def compute_bounds(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute bounding box of model.

        Returns:
            (min_corner, max_corner)
        """
        if self.vertices is None:
            return None, None

        min_corner = self.vertices.min(axis=0)
        max_corner = self.vertices.max(axis=0)

        logger.info(f"Model bounds: {min_corner} to {max_corner}")
        return min_corner, max_corner

    def normalize(self, scale: float = 1.0) -> bool:
        """
        Normalize model to [-scale, scale] range.

        Args:
            scale: Target scale

        Returns:
            True if successful
        """
        if self.vertices is None:
            logger.error("No vertices loaded")
            return False

        # Center at origin
        center = self.vertices.mean(axis=0)
        self.vertices -= center

        # Scale to [-scale, scale]
        max_extent = np.abs(self.vertices).max()
        if max_extent > 0:
            self.vertices *= (scale / max_extent)

        logger.info("Model normalized")
        return True

    def extract_depth_map(
        self,
        resolution: int = 640,
        method: str = "height",
    ) -> Optional[np.ndarray]:
        """
        Extract depth map from 3D model.

        Args:
            resolution: Output resolution
            method: Depth computation method ('height', 'distance', 'normal')

        Returns:
            Depth map as numpy array [0, 255]
        """
        if self.vertices is None:
            logger.error("No vertices loaded")
            return None

        try:
            # Get bounds
            min_corner, max_corner = self.compute_bounds()

            # Create depth map
            depth_map = np.zeros((resolution, resolution), dtype=np.float32)

            # Project vertices to 2D grid
            for vertex in self.vertices:
                # Normalize to [0, 1]
                x_norm = (vertex[0] - min_corner[0]) / (max_corner[0] - min_corner[0])
                y_norm = (vertex[1] - min_corner[1]) / (max_corner[1] - min_corner[1])

                # Convert to pixel coordinates
                px = int(x_norm * (resolution - 1))
                py = int(y_norm * (resolution - 1))

                if 0 <= px < resolution and 0 <= py < resolution:
                    if method == "height":
                        # Use Z coordinate as depth
                        depth = (vertex[2] - min_corner[2]) / (
                            max_corner[2] - min_corner[2]
                        )
                    elif method == "distance":
                        # Use distance from origin
                        depth = np.linalg.norm(vertex) / np.linalg.norm(max_corner)
                    else:
                        depth = 0.5

                    # Take max depth at each pixel (orthographic projection)
                    depth_map[py, px] = max(depth_map[py, px], depth)

            # Convert to uint8 [0, 255]
            depth_map_uint8 = (depth_map * 255).astype(np.uint8)

            logger.info(f"Extracted {resolution}x{resolution} depth map")
            return depth_map_uint8

        except Exception as e:
            logger.error(f"Failed to extract depth map: {e}")
            return None

    def get_statistics(self) -> dict:
        """Get model statistics."""
        if self.vertices is None:
            return {}

        stats = {
            "vertex_count": len(self.vertices),
            "face_count": len(self.faces) if self.faces else 0,
            "bounds": self.compute_bounds(),
            "center": self.vertices.mean(axis=0).tolist(),
            "extent": float(np.linalg.norm(self.vertices.max(axis=0) - self.vertices.min(axis=0))),
        }
        return stats


class DepthAugmentationPipeline:
    """Generate training data from 3D models using depth rendering."""

    def __init__(self, output_dir: Path = Path("data/augmented")):
        """Initialize augmentation pipeline."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def augment_from_3d(
        self,
        ply_path: Path,
        base_image: np.ndarray,
        resolution: int = 640,
        variations: int = 5,
    ) -> list[np.ndarray]:
        """
        Generate augmented images from 3D model.

        Args:
            ply_path: Path to PLY file
            base_image: Original 2D tablet image
            resolution: Depth map resolution
            variations: Number of variations to generate

        Returns:
            List of augmented images
        """
        # Load 3D model
        model = PLYModel(ply_path)
        if not model.load():
            logger.error(f"Failed to load 3D model: {ply_path}")
            return []

        model.normalize(scale=1.0)

        # Generate depth map
        depth_map = model.extract_depth_map(resolution)
        if depth_map is None:
            return []

        augmented = [base_image]

        try:
            import cv2

            # Depth overlay with various opacity levels
            for alpha in np.linspace(0.1, 0.5, variations - 1):
                # Resize depth map to match base image
                depth_resized = cv2.resize(
                    depth_map,
                    (base_image.shape[1], base_image.shape[0]),
                    interpolation=cv2.INTER_LINEAR,
                )

                # Create depth image (grayscale)
                if len(base_image.shape) == 3:
                    depth_3channel = cv2.cvtColor(depth_resized, cv2.COLOR_GRAY2BGR)
                else:
                    depth_3channel = depth_resized

                # Blend
                augmented_img = cv2.addWeighted(
                    base_image, 1 - alpha, depth_3channel, alpha, 0
                )
                augmented.append(augmented_img)

            logger.info(f"Generated {len(augmented)} augmented variations")
            return augmented

        except Exception as e:
            logger.error(f"Augmentation failed: {e}")
            return []

    def create_augmented_dataset(
        self,
        input_dir: Path,
        ply_dir: Path,
        output_dir: Path,
        variations: int = 3,
    ) -> dict:
        """
        Create augmented training dataset from images and 3D models.

        Args:
            input_dir: Directory with original images
            ply_dir: Directory with PLY files
            output_dir: Output directory for augmented images
            variations: Augmentation variations per image

        Returns:
            Summary statistics
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        summary = {
            "input_images": 0,
            "augmented_images": 0,
            "3d_models_used": 0,
            "failed_augmentations": 0,
        }

        try:
            import cv2
        except ImportError:
            logger.error("OpenCV required for augmentation")
            return summary

        # Process each image
        for image_file in sorted(input_dir.glob("*.jpg")) + sorted(
            input_dir.glob("*.png")
        ):
            summary["input_images"] += 1

            # Load image
            img = cv2.imread(str(image_file))
            if img is None:
                logger.warning(f"Cannot read image: {image_file}")
                summary["failed_augmentations"] += 1
                continue

            # Find matching PLY file
            ply_file = ply_dir / f"{image_file.stem}.ply"
            if not ply_file.exists():
                logger.debug(f"No 3D model for {image_file.stem}")
                # Save original
                cv2.imwrite(str(output_dir / f"{image_file.stem}_aug_0.jpg"), img)
                summary["augmented_images"] += 1
                continue

            summary["3d_models_used"] += 1

            # Generate augmentations
            augmented = self.augment_from_3d(ply_file, img, variations=variations)

            for i, aug_img in enumerate(augmented):
                output_path = output_dir / f"{image_file.stem}_aug_{i}.jpg"
                cv2.imwrite(str(output_path), aug_img)
                summary["augmented_images"] += 1

        logger.info(f"Augmentation complete: {summary['augmented_images']} images created")
        return summary


def main():
    """CLI for 3D model processing."""
    import argparse

    parser = argparse.ArgumentParser(description="3D model processing for tablets")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Load and inspect command
    inspect_parser = subparsers.add_parser("inspect", help="Inspect PLY file")
    inspect_parser.add_argument("--ply", type=Path, required=True, help="PLY file")

    # Extract depth map command
    depth_parser = subparsers.add_parser("depth", help="Extract depth map")
    depth_parser.add_argument("--ply", type=Path, required=True, help="PLY file")
    depth_parser.add_argument(
        "--output", type=Path, required=True, help="Output image file"
    )
    depth_parser.add_argument(
        "--resolution", type=int, default=640, help="Output resolution"
    )

    # Augmentation command
    aug_parser = subparsers.add_parser("augment", help="Augment dataset with 3D models")
    aug_parser.add_argument(
        "--images", type=Path, required=True, help="Input images directory"
    )
    aug_parser.add_argument(
        "--ply-dir", type=Path, required=True, help="PLY files directory"
    )
    aug_parser.add_argument(
        "--output", type=Path, required=True, help="Output augmented images directory"
    )
    aug_parser.add_argument(
        "--variations", type=int, default=3, help="Augmentations per image"
    )

    args = parser.parse_args()

    if args.command == "inspect":
        model = PLYModel(args.ply)
        if model.load():
            stats = model.get_statistics()
            print("\n=== PLY File Statistics ===")
            for key, value in stats.items():
                print(f"{key}: {value}")

    elif args.command == "depth":
        model = PLYModel(args.ply)
        if model.load():
            depth_map = model.extract_depth_map(args.resolution)
            if depth_map is not None:
                try:
                    import cv2

                    cv2.imwrite(str(args.output), depth_map)
                    print(f"✓ Depth map saved to {args.output}")
                except ImportError:
                    print("OpenCV required to save images")

    elif args.command == "augment":
        pipeline = DepthAugmentationPipeline(args.output)
        summary = pipeline.create_augmented_dataset(
            args.images, args.ply_dir, args.output, args.variations
        )
        print("\n=== Augmentation Summary ===")
        for key, value in summary.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
