# Simple Examples:

<IMG src="https://lh3.googleusercontent.com/PaR5aaQ6cebGZ0loeEtkNaOSDcR8aQcmDNonm08zht-9cCx6Lzop_MqvI3JHjZHmKfUXB_rVFxHyKNAJ-EQ1qajA3ycmBWrxWLXeot9x9qfyAxqGzuROeAKqmz4BY2e5Ayj4VFuguqICPESDO8GeOMooDFO9wcaQNwxQdG1Pie4tQ7DbWsuHxkXW7_KA64gjREQyFSViP3mcBSgkB5HPKZCIMJLOsNYkKfvbF-zaX3qUbm53BmmO4FgRNmz28MudFfTk6ZV9VSUXy0hUmieDmwnnDx5ZxM1HCEKUWLaL4h2mN-tsd8NWTO_sQffBmwjHBudSQQDHbzfAQOFx5E1_RJ33Xsf9HgTZaXVLJCELbl5exeg35UorJaQTJHpu6yFOGWCPP7hhSWaZX_35ceXD35-yLTFvfaKQ1cmRIvk3MrsyzIrSKqCEH65fyCOa9vMEe7nnuSnhru_MAzYNP6LHe2e9Eg-whwSYaQwh0phUnLGpfh8UJ8A3mGZrEPb9730-NocMdQooDgCsVX2IGzX743eZj08Y6hFNKcBjbhUMqSOIuJm8VbbEeLHN79_z1OK1W_qqFcxMjiBfM5iH4vCQy3Sq2jqUpLlncJd6US1P1MAZ8oTbMOh0IZcojp_MTJHAT4IsDqfNroTaONxuj759zswGZcmb2QJ7ZiGzwANEMRcdAdGdaoNh6NA=w1563-h879-no" width=400>

## Read Features from FGDB

Code will demo conceptual model:

**Driver -> Data Source -> Layer -> Feature -> Geometry**

**Multiple options for reading FGDB's...**

[comparison of opensource vs esri driver](https://gdal.org/drivers/vector/openfilegdb.html#comparison-with-the-filegdb-driver)

### Driver

[list of ogr drivers](https://gdal.org/drivers/vector/index.html)

``` python
import osgeo.ogr as ogr
driver = ogr.GetDriverByName("OpenFileGDB")
```

### Data Source

``` python
...
dataPath = r'./data/BCTS_OPERATING_AREAS_SP.gdb'

# proprietary ESRI driver, read only, requires separate install
#driver = ogr.GetDriverByName("FileGDB")

# opensource driver, use this! DS is a DataSource object
driver = ogr.GetDriverByName("OpenFileGDB")
ds = driver.Open(dsath, 0)
...
```

### Layer

``` python
...
layer_name = 'WHSE_FOREST_TENURE_BCTS_OPERATING_AREAS_SP'
lyr = ds.GetLayerByName(layer_name)
...
```

### Feature

``` python
...
feat = lyr.GetNextFeature()
...
```

### Geometry

``` python
...
geom = feat.GetGeometryRef()
area = geom.GetArea()
...
```

[putting it all together...](../simple.py)



[next... reading features](gdal_python_overlaps_6.md)

