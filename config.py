import os
import re
from pathlib import Path
from collections import defaultdict
import glob


def load_dataset_from_directory(data_dir="./data"):
    """
    format: depth_{site}_{date}_{model}_mask_ODW.tiff
    example: depth_Oahu_20240115_BathyUnetPlusPlus_scSE_mask_ODW.tiff
    """
    dataset = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    
    pattern = r"depth_(.+?)_(\d{8})_(.+?)_mask_ODW\.tiff"
    
    for tif_file in glob.glob(os.path.join(data_dir, "*.tiff")):
        match = re.match(pattern, os.path.basename(tif_file))
        if match:
            site_raw, date_raw, model_raw = match.groups()
            
            site = site_raw.replace("_", " ")
            
            # YYYYMMDD -> YYYY-MM-DD
            date = f"{date_raw[:4]}-{date_raw[4:6]}-{date_raw[6:8]}"
        
            model = model_raw.replace("_", " ")
            
            dataset[site][date][model]["tif_path"] = tif_file
    
    return {k: dict(v) for k, v in dataset.items()}


DATASET = load_dataset_from_directory()
