"""Create the pia mesh for O1 atlas."""

from pathlib import Path

import pandas
import trimesh
from neurocollage.mesh_helper import MeshHelper

if __name__ == "__main__":
    glomeruli_data = pandas.read_csv(
        "/gpfs/bbp.cscs.ch/project/proj144/Circuits/atlas_based/2024.09.12/bioname/glomeruli.csv",
        index_col="glom_id",
    )
    mesh_helper = MeshHelper(
        {
            "atlas": "/gpfs/bbp.cscs.ch/project/proj144/entities/atlas/whole_region/2024.11.05",
            "structure": "region_structure.yaml",
        },
        "MOB",
    )

    # mesh for top boundary
    mesh = mesh_helper.get_boundary_mesh()  # better this version, prob due to wrong depths values
    mesh.export("pia_mesh.obj")
    mesh.vertices = mesh.vertices * 25.0
    mesh.export("pia_mesh_viz.obj", include_color=False, include_texture=False)

    # mesh for basals of mTC
    meshes = mesh_helper.get_layer_meshes()
    meshes[0].export("MOBgl.obj")
    meshes[0].vertices = meshes[0].vertices * 25.0
    meshes[0].export("MOBgl_viz.obj", include_color=False, include_texture=False)

    # glomeruli meshes
    Path("glomeruli").mkdir(exist_ok=True)
    spheres = []
    for index, row in glomeruli_data.iterrows():
        indx = f"{index:03d}"
        glomerulus_name = "glomeruli_{}".format(indx)
        print(row["radius"], mesh_helper.brain_regions.voxel_dimensions[0])
        sphere = trimesh.creation.icosphere(
            subdivisions=2, radius=row["radius"] / mesh_helper.brain_regions.voxel_dimensions[0]
        )
        pos = mesh_helper.positions_to_indices(row[["x", "y", "z"]])
        sphere.apply_translation(pos)
        sphere.export("glomeruli/{}.obj".format(glomerulus_name))
        sphere.vertices = sphere.vertices * 25.0
        spheres.append(sphere)

    trimesh.util.concatenate(spheres).export(
        "all_gloms.obj", include_color=False, include_texture=False
    )
