"""Create the boundary mesh for striatum region."""

from neurocollage.mesh_helper import MeshHelper

if __name__ == "__main__":
    atlas = "/gpfs/bbp.cscs.ch/project/proj145/home/arnaudon/synthesis_striatum_boundary/atlas"
    mesh_helper = MeshHelper(
        {"atlas": atlas, "structure": "region_structure.yaml"}, "STRd", hemisphere="left"
    )
    mesh = mesh_helper.get_boundary_mesh()
    mesh.export("striatum_boundary.obj")
