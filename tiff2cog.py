import os
import glob
from rio_cogeo.cogeo import cog_translate
from rio_cogeo.profiles import cog_profiles
from tqdm import tqdm
def batch_convert_to_cog(input_dir, output_dir):

    os.makedirs(output_dir, exist_ok=True)
    files = glob.glob(os.path.join(input_dir, "*.tiff"))
    dst_profile = cog_profiles.get("deflate")

    for fullpath in tqdm(files):
        fn = os.path.basename(fullpath)
        # fn_no_ext = os.path.splitext(fn)[0]
        # output_filename = f"{filename_no_ext}_COG.tif"
        output_path = os.path.join(output_dir, fn)

        cog_translate(
            fullpath,
            output_path,
            dst_profile,
            in_memory=True,
            quiet=True,
            overview_resampling="nearest", 
            nodata=float('nan'),
        )


if __name__ == "__main__":
    INPUT_FOLDER = "/Volumes/DATA/BathyUnet++_bathymetry/raw_test"   
    OUTPUT_FOLDER = "/Volumes/DATA/BathyUnet++_bathymetry/cog_test" 

    batch_convert_to_cog(INPUT_FOLDER, OUTPUT_FOLDER)