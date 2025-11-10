import json

global sGrid
from pysheds.sgrid import sGrid

threshold = 300
prefix = "TEST_"
acc_path = "data/raster/TCA_test.tif"
fdir_path = "data/raster/FDIR_test.tif"
dem_path = "data/raster/DEM_depitted_test.tif"

# outlet bacino diretto
x = 4515709
y = 2593661

split_points_list = [
    (x, y),                # 0
    (4514415, 2593243),    # 1
    (4514354, 2594384),    # 2
    (4513724, 2593094),    # 3
    (4515135, 2593454),    # 4
    (4514475, 2594473),    # 5 outlet bacino allacciato (es. opera di presa)
    (4512706, 2594326)     # 6 outlet bacino allacciato (es. opera di presa)
]

grid: sGrid = sGrid.from_raster(acc_path)
fdir = grid.read_raster(fdir_path)
acc = grid.read_raster(acc_path)

network = acc > threshold

grid.to_raster(network, f"data/raster/{prefix}Network_{threshold}.tif", blockxsize=16, blockysize=16)

catchment_area = grid.catchment(x=x, y=y, fdir=fdir, xytype="coordinate", snap="center")

profiles, connections = grid.extract_profiles(
    fdir, network, split_points=split_points_list
)

print(connections)

sub_basins = grid.extract_subcatchment(
    fdir, network, split_points=split_points_list
)

# write raster sub-basins
grid.to_raster(
    sub_basins,
    f"data/raster/{prefix}SubBasin{threshold}.tif",
    apply_output_mask=True,
    blockxsize=16,
    blockysize=16,
)

# write vecotor sub-basins
grid.to_sb_shapefile(sub_basins, f"data/vector/{prefix}SubBasin_{threshold}.shp", dem_path=dem_path)

branches = grid.extract_river_network(
    fdir, network, split_points=split_points_list, dem_path=dem_path
)

# write vector network
with open(f"data/vector/{prefix}Network_{threshold}.geojson", "w") as f:
    json.dump(branches, f)


