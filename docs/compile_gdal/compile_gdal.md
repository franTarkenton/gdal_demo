# attempt to create a datamigration script from BCGW to PG

## Requirements

In order to be able to connect OGR to the bcgw you need to make sure
that it has OCI (Oracle call interface) support.  Most binary installs
of GDAL/OGR do not have OCI support, and thus require you to compile 
the code yourself.

Compiling on windows used to be a HUGE pain in the arse.  Windows 10 
saw the introduction of Windows subsystem for linux which makes 
compiling opensource code much easier.  All instructions below require
the use of Windows subsystem for linux.  If you do not already have
this installed I recommend doing so immediately... 

[Windows Subsystem For Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10)

When it comes time to installing a distribution I recommend [ubuntu](https://www.microsoft.com/en-ca/p/ubuntu-1804-lts/9n9tngvndl3q?rtc=1&activetab=pivot:overviewtab)

### Ubuntu packages

install the following package
zip, unzip, swig, gcc, make, sqlite3, build-essential, python-dev

`sudo apt-get install zip unzip swig gcc make sqlite3 build-essential  python-dev`

## Recommendations

[Windows Terminal](https://github.com/microsoft/terminal) or 
[Cmder](https://cmder.net/).  I'd also recommend installing using
[chocolatey](https://chocolatey.org/)

## Installing

### Download / Get the Oracle Crap

All the oracle stuff can be found at the [oracle download page](https://www.oracle.com/database/technologies/instant-client/linux-x86-64-downloads.html)

Download the following files:
* [Basic Packages (ZIP)](https://download.oracle.com/otn_software/linux/instantclient/195000/instantclient-basic-linux.x64-19.5.0.0.0dbru.zip)
* [SQL Plus Package (ZIP)](https://download.oracle.com/otn_software/linux/instantclient/195000/instantclient-sqlplus-linux.x64-19.5.0.0.0dbru.zip)
* [SDK Package (ZIP)](https://download.oracle.com/otn_software/linux/instantclient/195000/instantclient-sdk-linux.x64-19.5.0.0.0dbru.zip)

*I used version 19.5 but I believe any version should work*

### Extract Zips

* create /opt/oracle, and extract the oracle zips into that directory
`cd /opt`
`sudo mkdir oracle`
`sudo unzip /location/to/your/download/instantclient-basic-linux.x64-19.5.0.0.0dbru.zip`
`sudo unzip /location/to/your/download/instantclient-sqlplus-linux.x64-19.5.0.0.0dbru.zip`
`sudo unzip /location/to/your/download/instantclient-sdk-linux.x64-19.5.0.0.0dbru.zip`


### Compile OGR and Dependencies

This repo contains a install_deps.sh script that was stolen from the pyrosal github
repo: https://github.com/johntruckenbrodt/pyroSAR/blob/master/pyroSAR/install/install_deps.sh

I modified the script slightly:
* bash shell path to work with ubuntu 
* modified gdal so it can incorporates the oracle stuff to add OCI interface
* deleted cleanup so that if it fails we don't have to start from scratch.

Now attempt the install (warning this takes about an hour to run)
`sudo ./install_deps.sh`

Once complete you should have a local directory in your ~ (home) folder with gdal command 
lines and any other utilities that are built by the dependencies.

## Testing OGR

use the following command to verify that you can dump data from oracle to some other
format.  example below is for shapefile

ogr2ogr <srs> -f "ESRI Shapefile" \
/favourite/path/test.shp \
OCI:"<oracle user>/<oracle password>@(DESCRIPTION = (ADDRESS_LIST = (ADDRESS = (PROTOCOL = TCP)(HOST = <hostname>)(PORT = <port number>)))(CONNECT_DATA = (SERVICE_NAME  =<sid name>))):<oracle schema>.<oracle table>"

# Useful links:

* [build bash script](https://github.com/johntruckenbrodt/pyroSAR/blob/master/pyroSAR/install/install_deps.sh)
* [extensive docs on compiling o/s geospatial tools / lib](http://scigeo.org/articles/howto-install-latest-geospatial-software-on-linux.html#geos)
* [bunch more references to build scripts:](https://gis.stackexchange.com/questions/317109/build-gdal-with-proj-version-6)
* [specifics to oracle](http://bisoftdiary.com/osm_gdal_oci_linux/)
* [configure oracle client](https://medium.com/@arunkundgol/how-to-setup-oracle-instant-client-on-windows-subsystem-for-linux-cccee61d5b0b)

# outstanding / to look into

## datums

Proj requires some data files that are not currently being downloaded as part of the install, could
modify the install to add those files or possibly figure out how to add stuff in later.  In a 
typical build process the datums get added after 'configure' and before 'make'.

* now get the datums from [here](https://proj.org/download.html)
* direct link to [proj-datumgrid-1.8.zip](https://download.osgeo.org/proj/proj-datumgrid-1.8.zip








