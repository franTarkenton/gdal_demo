import osgeo.ogr as ogr



dataPath = r'./data/BCTS_OPERATING_AREAS_SP.gdb'
# proprietary ESRI driver, read only, requires separate install
#driver = ogr.GetDriverByName("FileGDB")
# opensource driver, use this!
driver = ogr.GetDriverByName("OpenFileGDB")
ds = driver.Open(dataPath, 0)

# print all the feature classes/tables in the FGDB
featsClassList = []
for featsClass_idx in range(ds.GetLayerCount()):
    featsClass = ds.GetLayerByIndex(featsClass_idx)
    featsClassList.append(featsClass.GetName())
print(f'fature classes: {r",".join(featsClassList)}')

# print columns
fc_name = 'WHSE_FOREST_TENURE_BCTS_OPERATING_AREAS_SP'
lyr = ds.GetLayerByName(fc_name)
feat = lyr.GetNextFeature()
column_count = feat.GetFieldCount()
for col_cnt in range(0, column_count):
    fld_def = feat.GetFieldDefnRef(col_cnt)
    fld_name = fld_def.GetName()
    print(f'fld {col_cnt} is {fld_name}')

# iterate geometries
total_area = 0
for feat_cnt in range(1, lyr.GetFeatureCount() + 1):
    feat = lyr.GetFeature(feat_cnt)
    geom = feat.GetGeometryRef()
    area = geom.GetArea()
    total_area += area
    #print(f'feature area: {area}, {total_area}')


print(f'total area of: {fc_name} in hecares is {total_area / 10000}')


