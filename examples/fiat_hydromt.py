#%%
# import required packages
import os
from hydromt_fiat.fiat import FiatModel
from hydromt.log import setuplog
from pathlib import Path
import geopandas as gpd
import matplotlib.pyplot as plt
import shutil

#%%
model_root = 'FIAT_database'  # where to save the FIAT model
model_name = "example" # name of the case study

#%%
model_folder = Path(model_root) / model_name  # full path to model folder
data_catalog = Path(os.path.abspath("")) / "data" / "hydromt_fiat_catalog_global.yml"  # path to data catalog relative to this notebook
logger_name = "hydromt_fiat"  # name of the logger
logger = setuplog(logger_name, log_level=10) # setup logger

#%%
# domain_fn = Path('./data/KingstonUponHull_domain.geojson')
# region = gpd.read_file(domain_fn)
# flood_area = gpd.read_file("c:/Code/COMPASS/sfincs_models/sfincs_MZ_ERA5/gis/floodmap.tif")
region = gpd.read_file("c:/Code/COMPASS/COMPASS/sfincs_sofala/sfincs_sofala/gis/region.geojson")
continent = "Africa"
country = "Mozambique"
# continent = 'Europe'
# country = 'United Kingdom'

# area_of_interest = {
#     "type": "FeatureCollection",
#     "features": [
#         {
#             "type": "Feature",
#             "properties": {},
#             "geometry": {
#                 "coordinates": [
#                      [
#             [34.37939695948343, -20.07031561711855],
#             [34.387653838143834, -19.377711500714003],
#             [34.92179500387799, -19.368799942263994],
#             [34.92293033010172, -20.07136792215392],
#             [34.37939695948343, -20.07031561711855]
#           ]
#         ],
#                 "type": "Polygon",
#             },
#         }
#     ],
# }
# region = gpd.GeoDataFrame.from_features(area_of_interest, crs="EPSG:4326")

#%%
from pyproj import CRS
# Specify the CRS for the region (for example, UTM zone 36S)
utm_crs = CRS.from_epsg(32736)  # Replace with the correct EPSG code

# Ensure the region geometry is set to the correct CRS
region = region.to_crs(utm_crs)

# Save the GeoDataFrame as GeoJSON
region.to_file("region.geojson", driver='GeoJSON')

#%%
### Setup vulnerability parameters ###
vulnerability_fn = "jrc_vulnerability_curves"
vulnerability_identifiers_and_linking_fn = "jrc_vulnerability_curves_linking"
unit = "m"

### Setup exposure parameters ###
asset_locations = "OSM"
occupancy_type = "OSM"
max_potential_damage = "jrc_damage_values"
ground_floor_height = 0
damage_types = ["total"]
unit = "m"

### Setup output parameters ###
output_dir = "output"
output_csv_name = "output.csv"
output_vector_name = "spatial.gpkg"

#%%
configuration = {
    "setup_output": {
        "output_dir": output_dir,
        "output_csv_name": output_csv_name,
        "output_vector_name": output_vector_name,
    },
    "setup_vulnerability": {
        "vulnerability_fn": vulnerability_fn,
        "vulnerability_identifiers_and_linking_fn": vulnerability_identifiers_and_linking_fn,
        "continent": continent,
        "unit": unit,
    },
    "setup_exposure_buildings": {
        "asset_locations": asset_locations,
        "occupancy_type": occupancy_type,
        "max_potential_damage": max_potential_damage,
        "ground_floor_height": ground_floor_height,
        "unit": unit,
        "damage_types": damage_types,
        "country": country,
    },
}

#%%
if model_folder.exists():
    shutil.rmtree(model_folder)
fiat_model = FiatModel(root=model_folder, mode="w", data_libs=[data_catalog], logger=logger)

#%%
fiat_model.build(region={"geom": region}, opt=configuration, write=False)

#%%
# Get the geodataframe with exposure data
# gdf = fiat_model.exposure.get_full_gdf(fiat_model.exposure.exposure_db)
# gdf.to_file('exposure_test.geojson', driver='GeoJSON')

#%%
# gdf[['Secondary Object Type', 'geometry']]
# Plot the region and the secondary object types of the exposure data
# m = region.explore(name='Region', style_kwds={'color': 'black', 'fill': False})
# m = gdf.explore(m=m, column='Secondary Object Type', name='Exposure types')
# m

#%%
# gdf.explore(column='Max Potential Damage: Total')

#%%
# Get the range of (possible) water depths
water_depths = fiat_model.vulnerability.hazard_values
# Plot damage curves for some occupancy types
line_styles = ['--', '-', ':']
for function_name, ls in zip(fiat_model.vulnerability.functions.keys(), line_styles):
    dmg = [float(i) for i in fiat_model.vulnerability.functions[function_name]]
    plt.plot(water_depths, dmg, label=function_name, ls=ls)
plt.xlabel('depth (m)')
plt.ylabel('damage fraction (-)')
plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
plt.show()

#%%
fiat_model.write()

#%%
fiat_model_new = FiatModel(root=model_folder, mode="r", data_libs=[data_catalog], logger=logger)
fiat_model_new.read()
# %%
# TO DO: add hazard automatically to setting file by specifying floodmap file
