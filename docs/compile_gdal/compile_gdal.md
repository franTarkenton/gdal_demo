# Compile GDAL/OGR

<img src="https://lh3.googleusercontent.com/-_rLz3dpB8He6Mn44TIPD_9IoD-0g5NhQ0aKAHS0diilBnOGek18Om0DCwgOlyhf_Wt4nr7P_ZyKir6C12Wv7qmwlvu2WTd86ElxVxSMZA3lZhKP_EJcv7tTQ1xRMVeaGrrlktknrwz5QE-_VISYaPxL1dzQL6isOqyR8Qe5sSnBdLGXVbkJ1ZKtu53FQGrJd2Fuwjrz1EBGg8FNC-yosKpsBtewvBY_7JO7KnDEaTdqmjrTZTSVk5bb2cZYSNuIT60VjQpkaaoOO12cZ6vbsjxuZnyPFyD6M_dW6LqqmmbhwDoFgdWZbap3966_TLDKU2qndPfC3BrioAWUDoWW_u--nb7iD8P6oPNpOzA4iuW40zP8podEvBd_ucvfVfgozosfEB4KvnuOqdo46nlVzyZGOBl1utD7O1aAGiSiUOKy0qFXb9eJBd_yx5apwA8egur0rgjIjJs21hBXyCmTMj1x9J9pkLPO67kSpgQBbHWCc9X1qKGc9_ZEgJEcnvRUiOO5PdcABxW3_uk1_5GMIoPlVjUYGKAnxc62duTkdG1rwowswcmG0bnsawqDbqfhkYEmmw3X6VRk4bF_3DJMbvW04ZcTqx_DXUmkiRB95IHGh0WftCxSgBmSXBau8ZG8y32HkNRnPMKK8biXXftKubJ3-VWS0pJQifmzkAF7W8IwWIissqG4_8ZV3rn7MckPEXjbwOvMcLHQJhwBU5xozQRXFibNRpCB4nr_xpLB72lPjeQh=w1066-h519-no" width=700>

## Background

In order to be able to connect OGR to the bcgw you need to make sure
that the version of gdal/ogr you are using supports OCI 
(Oracle call interface).  Most binary installs do not.  This means in 
many cases you are stuck with the requirement to compile gdal
yourself.

Compiling gdal on windows used to be a HUGE pain in the arse.  Windows 10 
introduced the Windows subsystem for linux (WSL) which makes 
compiling opensource code way easier.  The remainder of this document
assumes you have WSL installed.  Most of it however will probably just work
on osx.

## Requirements (assuming this stuff is set up)

* [Installing Windows Subsystem For Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10)

When it comes time to installing a distribution I recommend [ubuntu](https://www.microsoft.com/en-ca/p/ubuntu-1804-lts/9n9tngvndl3q?rtc=1&activetab=pivot:overviewtab)

Ubuntu is actually now creating special distribution that are designed to 
work with WSL. [article](https://www.zdnet.com/article/canonical-makes-ubuntu-for-windows-subsystem-for-linux-a-priority/)

### Ubuntu / linux packages required

* zip
* unzip
* swig
* gcc
* make
* build-essential
* python-dev

**Installing:**

```sudo apt-get install zip unzip swig gcc make sqlite3 build-essential  python-dev```

## Recommendations

Not required but do a great job of masking the stench that is windows:

* [Windows Terminal](https://github.com/microsoft/terminal) or 
* [Cmder](https://cmder.net/).  I'd also recommend installing using
* [chocolatey](https://chocolatey.org/)

## Getting and Configuring Oracle's Crap

### Download Links

All the oracle stuff can be found at the [oracle download page](https://www.oracle.com/database/technologies/instant-client/linux-x86-64-downloads.html)

Proceed with downloading the following files:
* [Basic Packages (ZIP)](https://download.oracle.com/otn_software/linux/instantclient/195000/instantclient-basic-linux.x64-19.5.0.0.0dbru.zip)
* [SQL Plus Package (ZIP)](https://download.oracle.com/otn_software/linux/instantclient/195000/instantclient-sqlplus-linux.x64-19.5.0.0.0dbru.zip)
* [SDK Package (ZIP)](https://download.oracle.com/otn_software/linux/instantclient/195000/instantclient-sdk-linux.x64-19.5.0.0.0dbru.zip)

*I used version 19.5 but I believe any version should work*

### Extract Zips

* create /opt/oracle, and extract the oracle zips into that directory
```
cd /opt
sudo mkdir oracle
sudo unzip /location/to/your/download/instantclient-basic-linux.x64-19.5.0.0.0dbru.zip
sudo unzip /location/to/your/download/instantclient-sqlplus-linux.x64-19.5.0.0.0dbru.zip
sudo unzip /location/to/your/download/instantclient-sdk-linux.x64-19.5.0.0.0dbru.zip
```

### Compile OGR and Dependencies

This repo contains a [install_deps.sh](../../install_gdal_deps.sh) script that was stolen from the pyrosal github
repo: https://github.com/johntruckenbrodt/pyroSAR/blob/master/pyroSAR/install/install_deps.sh

It has been modified slightly in the following ways:
* bash shell path to work with ubuntu
* modified gdal configure so it can incorporates the oracle stuff to add OCI interface
* deleted cleanup so that if it fails we don't have to start from scratch.

#### **Run the OGR/GDAL Compile** (warning this takes about an hour to run)
```
sudo ./install_deps.sh
```

Once complete you should have a *local* directory in your ~ (home) folder with gdal utilities and a bunch of other stuff that you may find useful at a later date.

## Testing OGR

Use the following command to verify that you can dump data from oracle to some other
format.  example below is for a pgdump file, you can test for any output format.

To get a list of supported formats:

```
cd ~/local
./ogrinfo --formats
```

If the install worked you should see a line that says OCI

```
... OCI -vector- (rw+): Oracle Spatial ...
```

Test dump of BCGW table to PGDUMP format.
```
ogr2ogr -nln <output object name>  -lco GEOMETRY_NAME=geom -f "PGDUMP" <path to pgdump file> OCI:"<username>/<password>@(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=<db host>)(PORT=<db port>)))(CONNECT_DATA=(SERVICE_NAME=<db service name>))):<oracle schema>.<oracle table to dump>"
```

Specific Options that needed to be set to get a valid PGDUMP file:

* **-nln**: specifies the name of the object to be created in the postgres db. without this option will generate an invalid object name for the destination
* **-lco**: specifies the output geometry name.  without this option generates a dump file with "" for the geometry column which makes the file invalid.

## Finalize install

### move the compiled binaries to  `/opt`

```
sudo mkdir /opt/gdal
sudo cp -R ~/local/* /opt/gdal/.
```

### Modify your shell init

Add the following lines to .bashrc
```
export GDAL_HOME=/opt/gdal
export ORACLE_HOME=/opt/oracle/instantclient_19_5
export LD_LIBRARY_PATH=$ORACLE_HOME:$GDAL_HOME/lib:$GDAL_HOME/include:$LD_LIBRARY_PATH
export PATH=$ORACLE_HOME:$GDAL_HOME/bin:$PATH
```

and lastly open a new shell and verify that you have ogr installed:

```
ogrinfo --version
```
should be 3.0.1

# Useful links:

* [build bash script](https://github.com/johntruckenbrodt/pyroSAR/blob/master/pyroSAR/install/install_deps.sh)
* [extensive docs on compiling o/s geospatial tools / lib](http://scigeo.org/articles/howto-install-latest-geospatial-software-on-linux.html#geos)
* [bunch more references to build scripts:](https://gis.stackexchange.com/questions/317109/build-gdal-with-proj-version-6)
* [specifics to oracle](http://bisoftdiary.com/osm_gdal_oci_linux/)
* [configure oracle client](https://medium.com/@arunkundgol/how-to-setup-oracle-instant-client-on-windows-subsystem-for-linux-cccee61d5b0b)
* [the great oracle's ideas on gdal/ogr](https://www.oracle.com/technetwork/database/enterprise-edition/gdal-howto-compile-windows-128267.txt)

# outstanding / to look into

## datums

Proj requires some data files that are not currently being downloaded as part of the install, could
modify the install to add those files or possibly figure out how to add stuff in later.  In a 
typical build process the datums get added after 'configure' and before 'make'.

* now get the datums from [here](https://proj.org/download.html)
* direct link to [proj-datumgrid-1.8.zip](https://download.osgeo.org/proj/proj-datumgrid-1.8.zip








