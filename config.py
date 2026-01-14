import os
import re
from pathlib import Path
from collections import defaultdict


def load_dataset_from_directory(data_dir="./data"):
    """
    format: depth_{site}_{date}_{model}_mask_ODW.tiff
    example: depth_Oahu_20240115_BathyUnetPlusPlus_scSE_mask_ODW.tiff
    """
    dataset = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    
    pattern = r"depth_(.+?)_(\d{8})_(.+?)_mask_ODW\.tiff"
    
    data_path = Path(data_dir)
    if not data_path.exists():
        return {}
    
    for tif_file in data_path.glob("*.tiff"):
        match = re.match(pattern, tif_file.name)
        if match:
            site_raw, date_raw, model_raw = match.groups()
            
            site = site_raw.replace("_", " ")
            
            # YYYYMMDD -> YYYY-MM-DD
            date = f"{date_raw[:4]}-{date_raw[4:6]}-{date_raw[6:8]}"
        
            model = model_raw.replace("_", " ")
            
            dataset[site][date][model]["tif_path"] = str(tif_file)
    
    return {k: dict(v) for k, v in dataset.items()}


DATASET = load_dataset_from_directory()
