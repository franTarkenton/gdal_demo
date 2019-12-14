# Intro
<img src="https://lh3.googleusercontent.com/N7SI_w3wrOhDNs7QCigXYAyLtNK2Eeix-3W4htHQN6GcDG1Px2QbpxzH8fsPq6olPL4iScLHwgRmDsfFqjkFZyuPjF55loJm3D13h1pB2G7uhahFIVc0lJjNeLlP4YNc9mmKmNZ3aSBYrJtWbhgROR4Xk62oOCks8Jbq2SJblD1xSyYiUvQA6NsOKX2VWjhEYCNhOejdxJkj6jubjBzYYgVtCYhuS2_EZqQNAj-w9N-E4T_8VwCPMkesDsiB6XtiTLVm3MjlxgjasQtcpD1Krm1-qesBK8t1N_tZoU1qmqVl_1Ld6SkH-bzqXVYInCqFgpBrvny7ley3HJkFFP7VLMotQM1GLnbEWvXPwXhtzaX_wwjdA5dJvK7IqsXofNheP59fGUQVXGwa8svDy1KsNmiUx-GSuHPRXnPE3L12UORhvsMFFVOqujRd2C-2_1p9_-gZyAs_FRhT4WHAFh3QdxUh0xnXNNuZ24DcUvMJkpEjswtTJMq0CTcw6z9QaL6tf3KcYJbVIckQmqSFyp0cf4WgOfiGiKseZ890rpoCBIAe9RTy0uDqYtm9WVK1F7CMcRnVdEF2DnBdn85sxG3iTcdbcbcoPpmyhLx76PSVgZciqbq7dQnV382w4UbSl4G-HELifFdsVR_A_qztjYolI14ZnvwEvD6IfIpWveSBb9PbacRvpzMRXQew4eJwB4GezYMdEA35YHUc4OozLBT0xwYC_Rip6KOjE76PAiZo8SImttg8=w1325-h746-no" width="700">

Other options for using gdal on windows include the osgeo4win 
option.  I'm not a fan of this option as it doesn't cooperate 
well with other code external to the osgeo4win sandbox.  For 
example python.

This doc identifies how you can configure your paths so that 
you can use the gdal version that comes bundled with QGIS installs.

My preferred option for installing qgis is using [chocolatey](https://chocolatey.org/)

Once chocolately is installed its just:

```
choco install qgis -y
```

And to update:
```
choco upgrade qgis -y
```

or to update all your choco packages:

```
choco upgrade -all -y
```

# Configure gdal paths

Once qgis is installed set up the following environment variables:

set QGIS_HOME="C:\Program Files\QGIS 3.10"
set PATH=%QGIS_HOME%\bin;%PATH%

# test installation

After setting the following paths, if you installed QGIS 3.10
then the  bundled version of gdal should be 2.4.1

```
>gdalinfo --version
GDAL 2.4.1, released 2019/03/15
```

And now double check that you have the OCI drivers setup
```
>ogrinfo --formats | grep OCI
  OCI -vector- (rw+): Oracle Spatial
```

And finally the ultimate test... can we connect to oracle and dump
a table to shape file:
```
ogr2ogr  -f "ESRI Shapefile" <path to shp file> OCI:"<username>/<password>@(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=<db host>)(PORT=<db port>)))(CONNECT_DATA=(SERVICE_NAME=<db service name>))):<oracle schema>.<oracle table to dump>"
```

