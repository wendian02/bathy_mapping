import streamlit as st
import leafmap.foliumap as leafmap
from streamlit_folium import st_folium
from config import load_dataset_cloud
import os

st.set_page_config(layout="wide", page_title="BathyUNet++")
st.markdown("""
<style>
.leaflet-container { cursor: pointer !important; }
</style>
""", unsafe_allow_html=True)
DATASET = load_dataset_cloud()

st.sidebar.title("Setting")
selected_site = st.sidebar.selectbox(
    "Site",
    options=list(DATASET.keys())
)
site_info = DATASET[selected_site]

selected_date = st.sidebar.selectbox(
    "Date",
    options=list(site_info.keys())
)

selected_model = st.sidebar.selectbox(
    "Model",
    options=list(site_info[selected_date].keys())
)

tif_path = site_info[selected_date][selected_model]["tif_path"]
col1, col2 = st.columns([4, 1])

selected_cmap = st.sidebar.selectbox(
    "Colormap",
    ["jet_r", "ocean", "terrain_r", "viridis", "plasma", "inferno", "magma", "gist_earth"],
    index=0
)
min_val, max_val = st.sidebar.slider(
    "Depth Range",
    min_value=0.0,
    max_value=50.0,
    value=(0.0, 15.0),
    step=0.1
)
opacity = st.sidebar.slider("Opacity", 0.0, 1.0, 1.0)

selected_basemap = st.sidebar.selectbox(
    "Basemap",
    ["Google Hybrid", "Google Maps", "Google Satellite", "Esri World Imagery", "OpenStreetMap"],
    index=0
)

titiler_endpoint = "http://165.22.229.35/titiler"

m = leafmap.Map(draw_control=False)

import folium
m.get_root().html.add_child(folium.Element("""
<style>.leaflet-container { cursor: pointer !important; }</style>
"""))

basemaps = {
    "Google Hybrid": ("https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", "Google"),
    "Google Maps": ("https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", "Google"),
    "Google Satellite": ("https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", "Google"),
    "Esri World Imagery": ("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", "Esri"),
}

for name, (url, attribution) in basemaps.items():
    m.add_tile_layer(url=url, name=name, attribution=attribution, shown=(name == selected_basemap))

if selected_basemap == "OpenStreetMap":
    m.add_basemap("OpenStreetMap")

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


def fmt_coord(lat, lon):
    lat_str = f"{abs(lat):.5f}°{'N' if lat >= 0 else 'S'}"
    lon_str = f"{abs(lon):.5f}°{'E' if lon >= 0 else 'W'}"
    return lat_str, lon_str


with col1:
    map_data = st_folium(m, height=700, use_container_width=True)


with col2:
    st.subheader(f"🌊 {selected_site}")
    st.info(f"📅 {selected_date}")
    st.info(f"🌐 {selected_model}")
    st.info(f"🔗 [Dataset link](https://huggingface.co/datasets/wendian02/bathyunet/tree/main)")

    st.divider()
    st.subheader("Query Depth")
    st.info("💡 Click on the map to query depth")

    if map_data and map_data.get("last_clicked"):
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]
        lat_str, lon_str = fmt_coord(lat, lon)
        st.info(f"📍 {lat_str} &nbsp; {lon_str}")
        try:
            import requests
            with st.spinner("Fetching depth..."):
                response = requests.get(
                    f"{titiler_endpoint}/cog/point/{lon},{lat}",
                    params={"url": tif_path}
                )
                data = response.json()
                if "values" not in data:
                    st.warning("No data at this location")
                else:
                    depth = data["values"][0]
                    if depth is not None and not (depth != depth):
                        st.success(f"**Depth: {depth:.2f} m**")
                    else:
                        st.warning("No data at this location")
        except Exception as e:
            st.error(f"Error: {str(e)}")
