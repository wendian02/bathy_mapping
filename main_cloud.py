import streamlit as st
import leafmap.foliumap as leafmap
from config import DATASET
import os

st.set_page_config(layout="wide")

st.sidebar.title("Setting")
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
col1, col2 = st.columns([4, 1])

selected_cmap = st.sidebar.selectbox(
    "colormap",
    ["jet_r", "ocean", "terrain_r", "viridis", "plasma", "inferno", "magma", "gist_earth"],
    index=0
)
min_val, max_val = st.sidebar.slider(
    "depth range",
    min_value=0.0, 
    max_value=50.0, 
    value=(0.0, 15.0), 
    step=0.1
)
opacity = st.sidebar.slider("opacity", 0.0, 1.0, 1.0)

st.sidebar.info("If the map is not loading, please change the endpoint")

titiler_endpoint = st.sidebar.selectbox(
    "titiler endpoint",
    [
        "https://titiler.xyz",
        "https://giswqs-titiler-endpoint.hf.space",
    ],
    index=0
)

m = leafmap.Map(draw_control=False)

# m.add_basemap("CartoDB.DarkMatter") # built-in tile layers
# m.add_basemap("OpenStreetMap")
# m.add_basemap("Esri.WorldImagery")

m.add_tile_layer(
    url="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
    name="Google Hybrid",
    attribution="Google",
    shown=False
)
m.add_tile_layer(
    url="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
    name="Google Maps",
    attribution="Google",
    shown=False
)
m.add_tile_layer(
    url="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
    name="Google Satellite",
    attribution="Google",
    shown=False
)


m.add_tile_layer(
    url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    name="Esri.WorldImagery",
    attribution="Esri",
    shown=False
)


# diff endpoints has different args, and cause different problems
m.add_cog_layer(
        url=tif_path,
        name="Depth",
        palette=selected_cmap,
        opacity=opacity,
        nodata=float('nan'),
        rescale=f"{min_val},{max_val}",
        titiler_endpoint=titiler_endpoint,
    )
    
m.add_colormap(
    cmap=selected_cmap,
    vmin=min_val,
    vmax=max_val,
    width=2,
    height=0.1,
    position="bottomleft"
)

from folium import LatLngPopup
lat_lng_popup = LatLngPopup()
lat_lng_popup.add_to(m)


with col1:
    st.subheader("Bathymetry Map")
    m.to_streamlit(height=700)


with col2:
    st.subheader(f" {selected_site}")
    st.info(f"📅 {selected_date}")
    st.info(f"🌐 {selected_model}")
    st.info(f"🔗 [Dataset link](https://huggingface.co/datasets/wendian02/bathyunet/tree/main)")
    # st.info(f"🔗 [Model](todo)")
    
    st.divider()
    st.subheader("Query Depth")
    st.info("💡 Click on map to get coordinates, then paste here")

    query_lat = st.number_input("Latitude", value=0.0, format="%.5f")
    query_lon = st.number_input("Longitude", value=0.0, format="%.5f")


    if st.button("Get Depth"):
        try:
            import rasterio
            from rasterio.transform import rowcol
            import requests
            from io import BytesIO
            
            with st.spinner("Fetching depth..."):
                response = requests.get(tif_path)
                with rasterio.open(BytesIO(response.content)) as src:
                    row, col = rowcol(src.transform, query_lon, query_lat)
                    if 0 <= row < src.height and 0 <= col < src.width:
                        depth = src.read(1)[row, col]
                        if depth != src.nodata:
                            st.success(f"**Depth: {depth:.2f} m**")
                        else:
                            st.warning("No data at this location")
                    else:
                        st.error("Coordinates outside image bounds")
        except Exception as e:
            st.error(f"Error: {str(e)}")
