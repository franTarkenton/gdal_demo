# import the ogr module
import osgeo.ogr as ogr

dataPath = r"./data/BCTS_OPERATING_AREAS_SP.gdb"
# proprietary ESRI driver, read only, requires separate install
# driver = ogr.GetDriverByName("FileGDB")
# opensource driver, use this!
driver = ogr.GetDriverByName("OpenFileGDB")

# DATASOURCE object: ds
ds = driver.Open(dataPath, 0)

# Iterate over layers in DATASOURCE
layerNameList = []
for layer_idx in range(ds.GetLayerCount()):
    ogr_layer = ds.GetLayerByIndex(layer_idx)
    layerNameList.append(ogr_layer.GetName())
print(f'layer names: {r",".join(layerNameList)}')

# print columns names in LAYER
layer_name = "WHSE_FOREST_TENURE_BCTS_OPERATING_AREAS_SP"
lyr = ds.GetLayerByName(layer_name)

# FEATURE object: feat
feat = lyr.GetNextFeature()
column_count = feat.GetFieldCount()
for col_cnt in range(0, column_count):
    # FIELDDEFN object: fld_def
    fld_def = feat.GetFieldDefnRef(col_cnt)
    fld_name = fld_def.GetName()
    print(f"fld {col_cnt} is {fld_name}")

# iterate geometries, adding up the area.
total_area = 0
for feat_cnt in range(1, lyr.GetFeatureCount() + 1):
    feat = lyr.GetFeature(feat_cnt)
    geom = feat.GetGeometryRef()
    area = geom.GetArea()
    total_area += area

print(f"total area of: {layer_name} in hecares is {total_area / 10000}")

