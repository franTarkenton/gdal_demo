# Summary
<IMG src="https://lh3.googleusercontent.com/ba9_EKHsn5_4Zglj-__D4u_85bGIpeKNxXRFKyJSzwrLGKoq7it2qBwup9M5-anpv5oQzMRLJalhITN9Ia0ew0e4koWhkdKb2lTO-D80T3_OvCL61IApxGFPcZuw4ShSQp0-zu7_ltJGoip95bka_lkfMaLWt2gaxjYZQWNnQ9d6NDsi1dxPf3Rz7faQBPlj9qW8CmIDKEeE3T1A_Y1imEnMT6tef125y9er0SvLUXi1Q6zzvGv9Z5l3gHG03Jqa70t8jKJ6mFiW8aoUSh2pF_OjriZfVSeM2W72ihFY7gIwFK1WR9zdvQHshYImcSAhEPVa6Vhzc3vf6mdG_Mx45juScIenshXYq3q_UFlvfjTD9EWnaP2UnD44GVvA89ndXwNsPSf4qxRvHJ_Ag_lecW-xkH9BDR6Oo24TtyYNhMnn_edfZSEIEXFHxJH1jzbcVXrLoMtepYhWzwhrXpFRpGRkAzzhMYCLEIMhkc7pmYD2OlBnJprKPJHYBAvVwYKpnUoMyXd4tpAJXfB9EMyA2wgvpmjtiaoe4f-l428QQvoINQBfZe8TtzhKBI0OnRMv0Fm-wbS0oAfxv4-onTFTGAtWKLSxxlFdzbA5BLpQQ9r3T3qjR8IpQ095MnU7HczV3-LFaYRf-7LokNh16ckXpfc3em0PYu1r-oyA6m1UVnwTP4gC5Iynut_gBMtH0LImFC9vasFm2tcjOuxnJOU7H7CWhqL1kMJ0lpem6T3M07ENQZbs=w1842-h1036-no" width=500>

Modifying this repo to be a dumping place for GDAL/OGR related utilities.  This
includes the current docs that were created, but also includes various utility 
scripts.

# GDAL Presentation:

## Slides

The presentation is made up of the following slides/pages:

1. [overview / introduction](docs/intro_gdal_pres/presentation_start_1.md)
1. [What is gdal](docs/intro_gdal_pres/gdal_overview_2.md)
1. [Installing](docs/intro_gdal_pres/installing_3.md)
1. [Using GDAL/OGR with python - High Level](docs/intro_gdal_pres/gdal_python_4.md)
1. [Using GDAL/OGR with python - Code Examples](docs/intro_gdal_pres/gdal_python_code_demo_5.md)
1. [GDAL / OGR to detect overlaps](docs/intro_gdal_pres/gdal_python_overlaps_6.md)
1. [Conclusion](docs/intro_gdal_pres/summary_7.md)

## Code

1. [simple code demo's of gdal / python](src/simple.py)
1. [demo of overlap detection](src/demo_overlap_detection.py)

# BCGW OGR Extract

Created a script that will iterate over all the objects in a schema and
dump them them to S3 object storage.  In order to do this needed a gdal
ogr install that had OCI (oracle call interface) included in the compile.

Most of the existing binaries gdal / ogr do not include this feature. 
Created the following document which goes over how to compile ogr from 
source.  

* [BCGW to PGDUMP Script](src/copyData.py)
* [HOWTO: compile gdal / ogr with oracle support](docs/compile_gdal/compile_gdal.md)
* [HOWTO: using qgis gdal](docs/qgis_gdal.md)
