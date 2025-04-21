

# Load the merged DEM from file
with rasterio.open(output_path) as src:
    merged_dem = src.read(1)  # read the first band
    out_transform = src.transform
    bounds = rasterio.transform.array_bounds(src.height, src.width, out_transform)

# Extract bounding box
miny, minx, maxy, maxx = bounds[1], bounds[0], bounds[3], bounds[2]

# Fix the elevation range for normalization between 0 and 1000
min_elevation = 0
max_elevation = 1000

# Clip values above 1000m to 1000m
clipped_dem = np.clip(merged_dem, min_elevation, max_elevation)

# Normalize based on fixed range (0-1000)
normed_dem = (clipped_dem - min_elevation) / (max_elevation - min_elevation)

# Apply colormap
dem_colormap = cm.terrain(normed_dem)[:, :, :3]
dem_colormap = (dem_colormap * 255).astype(np.uint8)

# Create folium map
m = folium.Map(location=[(miny + maxy)/2, (minx + maxx)/2], zoom_start=8)

# Add ImageOverlay
dem_overlay = ImageOverlay(
    image=dem_colormap,
    bounds=[[miny, minx], [maxy, maxx]],
    opacity=0.6,
    name='FathomDEM (mosaic)'
)
dem_overlay.add_to(m)

# Load and add the AOI shapefile with dashed red line
aoi = gpd.read_file(aoi_path)

# Make sure AOI is in the same CRS as the map (WGS84)
if aoi.crs != 'EPSG:4326':
    aoi = aoi.to_crs('EPSG:4326')

# Add the AOI to the map with dashed red line
folium.GeoJson(
    aoi,
    name='Area of Interest',
    style_function=lambda x: {
        'color': 'red',
        'weight': 2,
        'dashArray': '5, 5',
        'fillOpacity': 0.0
    }
).add_to(m)


# Create a simple colorbar with the terrain colormap
fig, ax = plt.subplots(figsize=(1.5, 4))
norm = mpl.colors.Normalize(vmin=min_elevation, vmax=max_elevation)
cbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap='terrain'), cax=ax)
cbar.set_label('Elevation (m)')
plt.tight_layout()

# Save it to a BytesIO object and encode
buf = BytesIO()
plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
plt.close()
buf.seek(0)
img_str = base64.b64encode(buf.read()).decode('utf-8')

# Add the colorbar to the map
colorbar_html = '''
    <div style="
        position: fixed; 
        bottom: 50px; 
        right: 50px; 
        z-index: 9999; 
        background-color: white;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(0,0,0,0.5);">
        <img src="data:image/png;base64,{}" style="height:200px;">
    </div>
'''.format(img_str)

m.get_root().html.add_child(folium.Element(colorbar_html))

# Layer control
folium.LayerControl().add_to(m)

# Save map as HTML
m_output_path = f'./figures/maps/interactive/FathomDEM/FathomDEM_{site_identifier}.html'

# Ensure the directory exists
os.makedirs(os.path.dirname(m_output_path), exist_ok=True)

# Save the map
m.save(m_output_path)

print(f"Map saved to {m_output_path}")

# Display the map
m