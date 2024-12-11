"""Create barrel meshes"""

import trimesh
from neurocollage.mesh_helper import MeshHelper

if __name__ == "__main__":
    region = "SSp-bfd"
    atlas = {
        "atlas": "/gpfs/bbp.cscs.ch/project/proj100/atlas/mouse/atlas-release-mouse-barrels-density-mod",
        "structure": "region_structure.yaml",
    }
    mesh_helper = MeshHelper(atlas, region)
    mesh = mesh_helper.get_pia_mesh()
    mesh.export("pia_mesh.obj")

    barrels = [
        "A1",
        "A2",
        "A3",
        "Alpha",
        "B1",
        "B2",
        "B3",
        "B4",
        "Beta",
        "C1",
        "C2",
        "C3",
        "C4",
        "C5",
        "C6",
        "D1",
        "D2",
        "D3",
        "D4",
        "D5",
        "D6",
        "D7",
        "D8",
        "Delta",
        "E1",
        "E2",
        "E3",
        "E4",
        "E5",
        "E6",
        "E7",
        "E8",
        "Gamma",
    ]
    all_meshes = []
    for barrel in barrels:
        print(barrel)
        mesh = mesh_helper.get_boundary_mesh(subregion=region + "-" + barrel)
        mesh.export(f"barrels/barrel_{barrel}.obj", include_color=False, include_texture=False)
        mesh.vertices = mesh.vertices * 25.0
        all_meshes.append(mesh)
    trimesh.util.concatenate(all_meshes).export(
        "all_barrels.obj", include_color=False, include_texture=False
    )
