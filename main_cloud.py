import streamlit as st
import folium
from streamlit_folium import st_folium
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from config import DATASET
import os
import base64
from io import BytesIO
from PIL import Image


st.set_page_config(layout="wide")
st.title("BathyUNet++ map")


st.sidebar.title("setting")
selected_site = st.sidebar.selectbox(
    "select site",
    options=list(DATASET.keys())
)
site_info = DATASET[selected_site]

selected_date = st.sidebar.selectbox(
    "select date",
    options=list(site_info.keys())
)

selected_model = st.sidebar.selectbox(
    "select model",
    options=list(site_info[selected_date].keys())
)

tif_path = site_info[selected_date][selected_model]["tif_path"]
st.sidebar.info(f"📅 Date: {selected_date}")
st.sidebar.info(f"🤖 Model: {selected_model}")

selected_cmap = st.sidebar.selectbox(
    "colormap",
    ["jet", "blues","viridis", "plasma", "inferno", "magma", "terrain", "gist_earth", "ocean"],
    index=0
)
min_val, max_val = st.sidebar.slider(
    "depth range",
    min_value=0.0, 
    max_value=50.0, 
    value=(0.0, 30.0), 
    step=0.5
)
opacity = st.sidebar.slider("opacity", 0.0, 1.0, 1.0)



with rasterio.open(tif_path) as src:
    data = src.read(1)
    bounds = src.bounds
    
    data_masked = np.ma.masked_invalid(data)
    data_masked = np.ma.masked_where((data_masked < min_val) | (data_masked > max_val), data_masked)
    
    norm_data = (data_masked - min_val) / (max_val - min_val)
    norm_data = np.clip(norm_data, 0, 1)
    
    cmap_obj = matplotlib.colormaps.get_cmap(selected_cmap)
    colored_data = cmap_obj(norm_data)
    colored_data[..., 3] = np.where(data_masked.mask, 0, opacity)
    
    img = Image.fromarray((colored_data * 255).astype(np.uint8), mode='RGBA')
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    center_lat = (bounds.bottom + bounds.top) / 2
    center_lon = (bounds.left + bounds.right) / 2
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
    
    folium.raster_layers.ImageOverlay(
        image=f"data:image/png;base64,{img_str}",
        bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
        opacity=opacity,
        name="depth"
    ).add_to(m)
    
    folium.LayerControl().add_to(m)
    
    
    st_folium(m, width=None, height=500)
