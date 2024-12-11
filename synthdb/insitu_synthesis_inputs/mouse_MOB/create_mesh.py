"""Create the pia mesh for O1 atlas."""
from pathlib import Path

import pandas
import trimesh
from neurocollage.mesh_helper import MeshHelper

if __name__ == "__main__":
    glomeruli_data = pandas.read_csv(
        "/gpfs/bbp.cscs.ch/project/proj144/home/lyvonnet/Micro_circuit/Circuit/2024.01.08_light/bioname/glomeruli.csv",  # noqa
        index_col="glom_id",
    )
    mesh_helper = MeshHelper(
        {
            "atlas": "/gpfs/bbp.cscs.ch/project/proj144/home/lyvonnet/entities/atlas/2023.10.19/",
            "structure": "region_structure.yaml",
        },
        "O0",
    )

    # mesh for top boundary
    mesh = mesh_helper.get_pia_mesh()
    mesh.export("pia_mesh.obj")

    # mesh for basals of mTC
    meshes = mesh_helper.get_layer_meshes()
    meshes[0].export("MOBgl.obj")

    # glomeruli meshes
    Path("glomeruli").mkdir(exist_ok=True)
    spheres = []
    for index, row in glomeruli_data.iterrows():
        indx = f"{index:03d}"
        glomerulus_name = "glomeruli_{}".format(indx)
        sphere = trimesh.creation.icosphere(subdivisions=2, radius=2)
        pos = mesh_helper.positions_to_indices(row[["x", "y", "z"]])
        sphere.apply_translation(pos)
        sphere.export("glomeruli/{}.obj".format(glomerulus_name))
        spheres.append(sphere)

    # data = meshes + spheres
    # mesh_helper.render(data=data)
    # mesh_helper.show()
