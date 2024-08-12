import os
import trimesh
from scipy.spatial import ConvexHull


def compute_volume(mesh):
    return mesh.volume


def convex_hull_simplification(mesh):
    points = mesh.vertices
    hull = ConvexHull(points)

    # 使用原始点集和凸包算法生成的面索引来创建简化的网格
    simplified_mesh = trimesh.Trimesh(vertices=points, faces=hull.simplices)

    return simplified_mesh


def compare_meshes(original_mesh, simplified_mesh):
    original_vertices = len(original_mesh.vertices)
    original_faces = len(original_mesh.faces)
    original_volume = compute_volume(original_mesh)

    simplified_vertices = len(simplified_mesh.vertices)
    simplified_faces = len(simplified_mesh.faces)
    simplified_volume = compute_volume(simplified_mesh)

    comparison = {
        "original": {
            "vertices": original_vertices,
            "faces": original_faces,
            "volume": original_volume,
        },
        "simplified": {
            "vertices": simplified_vertices,
            "faces": simplified_faces,
            "volume": simplified_volume,
        },
    }

    return comparison


def process_stl_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".stl") or filename.endswith(".STL"):
            file_path = os.path.join(directory, filename)
            original_mesh = trimesh.load(file_path)

            # Perform convex hull simplification
            simplified_mesh = convex_hull_simplification(original_mesh)

            # Compare original and simplified meshes
            comparison = compare_meshes(original_mesh, simplified_mesh)

            # Print results
            print(f"File: {filename}")
            print(
                f"Original - Vertices: {comparison['original']['vertices']}, "
                f"Faces: {comparison['original']['faces']}, "
                f"Volume: {comparison['original']['volume']}"
            )
            print(
                f"Simplified - Vertices: {comparison['simplified']['vertices']}, "
                f"Faces: {comparison['simplified']['faces']}, "
                f"Volume: {comparison['simplified']['volume']}"
            )
            print("-" * 50)

            # Optionally save the simplified mesh
            simplified_path = os.path.join(directory, f"simplified_{filename}")
            simplified_mesh.export(simplified_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Simplify meshes using convex hulls")
    parser.add_argument(
        "-in", "--directory", type=str, help="Directory containing STL files"
    )
    args = parser.parse_args()
    process_stl_files(args.directory)
