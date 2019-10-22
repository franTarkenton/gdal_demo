# Simple Examples:

<IMG src="https://lh3.googleusercontent.com/rHg0MYNHW6IRrfqKfI82GE2GZzX23-OPhgK3vKfLn2i7Sj1065XF4u10oSttu3NShUuTXc4zij9zbsoYQvxp3yxuGKCYkJcgsP5_J7SpokydLOXgrEHdpJpouA8fpJQrGpxnAtMYWz4=w1842-h1036-no" width=400>

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

