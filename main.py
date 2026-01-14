import streamlit as st
import leafmap.foliumap as leafmap
from config import DATASET
import os


st.set_page_config(layout="wide")
st.title("BathyUNet++ map")

if not DATASET:
    st.error("❌ No data files found! Check if data/ folder exists and contains .tiff files")
    st.info(f"Current working directory: {os.getcwd()}")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'data')
    st.info(f"Script directory: {script_dir}")
    st.info(f"Looking for data in: {data_dir}")
    if os.path.exists(data_dir):
        files = os.listdir(data_dir)
        st.info(f"Files in data/: {files}")
    else:
        st.warning("data/ folder not found")
    st.stop()

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
file_exists = os.path.exists(tif_path)
st.sidebar.info(f"📁 File exists: {'✅' if file_exists else '❌'}")
if not file_exists:
    st.sidebar.error(f"Path: {tif_path}")
    st.error(f"File not found: {tif_path}")

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


m = leafmap.Map()
m.add_raster(
        tif_path, 
        layer_name="depth", 
        colormap=selected_cmap, 
        vmin=min_val, 
        vmax=max_val,
        opacity=opacity
    )

m.add_colormap(
    cmap=selected_cmap,
    vmin=min_val,
    vmax=max_val,
    width=2,
    height=0.1,
    position="bottomleft"
)

m.to_streamlit(height=500)