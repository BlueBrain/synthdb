"""Create the pia mesh for O1 atlas."""
import os

import trimesh
from neurocollage.mesh_helper import MeshHelper

if __name__ == "__main__":
    os.system("brainbuilder atlases -n 2,1 " "-t 100,100 -d 10 -o atlas column -a 200")

    mesh_helper = MeshHelper({"atlas": "atlas", "structure": "region_structure.yaml"}, "O0")
    mesh = mesh_helper.get_boundary_mesh()
    mesh.export("boundary_mesh.obj")
    mesh = mesh_helper.get_pia_mesh()
    mesh.apply_translation([0, 2, 0])
    mesh.export("pia_mesh.obj")

    sphere = trimesh.creation.icosphere(subdivisions=2, radius=1)
    sphere.apply_translation([20, 5, 15])
    sphere.export("sphere.obj")
