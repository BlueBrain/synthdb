"""Make a release with modified cells."""
from pathlib import Path

from morph_tool.morphdb import MorphDB

if __name__ == "__main__":
    orig_morpho_path = "/gpfs/bbp.cscs.ch/project/proj143/entities/morphologies/20230628/"
    morpho_path = Path("morphologies")
    mtypes = {
        "BasketCell": "CBXmo_BC",
        "StellateCell": "CBXmo_StC",
        "PurkinjeCell": "CBXpu_PuC",
        "GranuleCell": "CBXgr_GrC",
        "GolgiCell": "CBXgr_GoC",
    }
    layers = {
        "BasketCell": "CBXmo",
        "StellateCell": "CBXmo",
        "PurkinjeCell": "CBXpu",
        "GranuleCell": "CBXgr",
        "GolgiCell": "CBXgr",
    }
    db = MorphDB()
    for i, cell in enumerate(morpho_path.iterdir()):
        if cell.suffix == ".swc":
            db.df.loc[i, "name"] = cell.stem
            db.df.loc[i, "layer"] = layers[cell.stem]
            db.df.loc[i, "mtype_no_subtype"] = mtypes[cell.stem]
            db.df.loc[i, "msubtype"] = ""
            db.df.loc[i, "use_axon"] = False
            db.df.loc[i, "use_dendrites"] = True
    db.df[db.df.isna()] = None
    db.write(morpho_path / "neurondb.xml")
    print(db.df)
