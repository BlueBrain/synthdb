"""Make neurondb.xml for mouse granule."""
from pathlib import Path

from morph_tool.morphdb import MorphDB

if __name__ == "__main__":
    db = MorphDB()
    path = Path("/gpfs/bbp.cscs.ch/project/proj81/InputData/Morphologies/Neurons/Mouse/CBX/Granule")
    for i, morph in enumerate(path.rglob("*.h5")):
        db.df.loc[i, "name"] = morph.stem
        db.df.loc[i, "mtype"] = "Granule"
        db.df.loc[i, "mtype_no_subtype"] = "Granule"
        db.df.loc[i, "msubtype"] = ""
        db.df.loc[i, "use_axon"] = False
        db.df.loc[i, "use_dendrites"] = True
        db.df.loc[i, "axon_inputs"] = ""
        db.df.loc[i, "dendrite_repair"] = ""
        db.df.loc[i, "axon_repair"] = ""
        db.df.loc[i, "basal_dendrite_repair"] = ""
        db.df.loc[i, "tuft_dendrite_repair"] = ""
        db.df.loc[i, "oblique_dendrite_repair"] = ""
        db.df.loc[i, "unravel"] = ""
        db.df.loc[i, "use_for_stats"] = ""
        db.df.loc[i, "path"] = str(morph)
        print(morph)
    print(db.df)
    MorphDB._sanitize_df_types(db.df)
    db.write("neurondb.xml")
