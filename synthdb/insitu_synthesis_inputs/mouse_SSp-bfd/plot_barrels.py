import trimesh
import pyglet
from pathlib import Path


if __name__ == "__main__":
    meshes = []
    for barrel in Path("barrels").iterdir():
        mesh = trimesh.load_mesh(barrel)
        mesh.visual.face_colors = [100, 100, 100, 100]
        meshes.append(mesh)

    scene = trimesh.Scene(meshes)
    scene.show(start_loop=False)
    pyglet.app.run()
