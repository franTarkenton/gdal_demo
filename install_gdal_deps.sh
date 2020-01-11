#!/bin/bash
##############################################################
# manual installation of pyroSAR dependencies
# GDAL, GEOS, PROJ, SpatiaLite
# John Truckenbrodt, Rhys Kidd 2017-2019
##############################################################

# used to keep install dirs unique for different version
instsuffix=302


# define a root directory for downloading packages
root=$HOME/test${instsuffix}

# define a directory for download and unpacked packages
downloaddir=${root}/originals${instsuffix}
packagedir=${root}/packages${instsuffix}

# define the installation directory; This needs to be outside of the root directory so that the latter can be deleted in the end.
# In case installdir is set to a location outside of /usr/*, the following installation commands do not need to be run with
# administration rights (sudo)
#installdir=/usr/local
installdir=$HOME/local${instsuffix}

# where the fgdb libs will be located
fgdb_install_dir=${installdir}/FileGDB_API-64gcc51
echo ${fgdb_install_dir}

# the version of GDAL and its dependencies
GDALVERSION=3.0.2

# the python to use when compiling python bindings... options either python2 or python3
python_type=python3

# oracle OCI libs and headers, provided explicity as gdal expects a lib folder in
# however oracle no longer puts libs in a separate folder and instead puts them all
# in the instantclient foler.  have to unset ORACLE_HOME if it exists as it screws
# up the installation.
unset ORACLE_HOME
oracle_libs=/opt/oracle/instantclient_19_5
oracle_headers=/opt/oracle/instantclient_19_5/sdk/include

# these versions are not quite as important. If you use already installed them you might need to define their location
# for the configuration of GDAL
geos_version=3.7.2
proj_version=6.1.1
spatialite_version=4.3.0

# define the number of threads for compilation
threads=2
########################################################################################################################
# setup environment variables and create directories

if [[ -d "${root}" ]]; then
    if [[  "$(ls -A ${root})" ]]; then
        echo "Error! root already exists. Please choose a fresh directory which can be deleted once finished" 1>&2
        #exit 64
    fi
fi

export PATH=${installdir}/bin:$PATH
export LD_LIBRARY_PATH=${installdir}/lib:$LD_LIBRARY_PATH

for dir in ${root} ${downloaddir} ${packagedir} ${installdir}; do
    mkdir -p ${dir}
done
########################################################################################################################
# download GDAL and its dependencies
# https://github.com/Esri/file-geodatabase-api/raw/master/FileGDB_API_1.5/FileGDB_API_1_5_64gcc51.tar.gz
# FileGDB_API-64gcc51
declare -a remotes=(
                "https://github.com/Esri/file-geodatabase-api/raw/master/FileGDB_API_1.5.1/FileGDB_API_1_5_1-64gcc51.tar.gz"
                "https://download.osgeo.org/gdal/$GDALVERSION/gdal-$GDALVERSION.tar.gz"
                "https://download.osgeo.org/geos/geos-$geos_version.tar.bz2"
                "https://download.osgeo.org/proj/proj-$proj_version.tar.gz"
                "https://www.gaia-gis.it/gaia-sins/libspatialite-sources/libspatialite-$spatialite_version.tar.gz"
                )

for package in "${remotes[@]}"; do
    wget ${package} -nc -P ${downloaddir}
done
########################################################################################################################
# unpack downloaded archives

for package in ${downloaddir}/*tar.gz; do
    tar xfvz ${package} -C ${packagedir}
done
for package in ${downloaddir}/*tar.bz2; do
    tar xfvj ${package} -C ${packagedir}
done

########################################################################################################################
# move the FGDB stuff to the install dir
cp -R ${packagedir}/FileGDB_API-64gcc51 ${installdir}/.
echo "install dir is " ${fgdb_install_dir}
export LD_LIBRARY_PATH=${installdir}/FileGDB_API-64gcc51/lib:$LD_LIBRARY_PATH

########################################################################################################################
# install GEOS

cd ${packagedir}/geos*
./configure --prefix ${installdir}
make -j${threads}
sudo make install
########################################################################################################################
# install PROJ

cd ${packagedir}/proj*
./configure --prefix ${installdir}
make -j${threads}
sudo make install
########################################################################################################################
# install spatialite

cd ${packagedir}/libspatialite*

# PROJ now uses a new API, using the old deprecated one (as done by spatialite) needs to be indicated explicitly
./configure --prefix=${installdir} \
            CFLAGS=-DACCEPT_USE_OF_DEPRECATED_PROJ_API_H

make -j${threads}
sudo make install
########################################################################################################################
# install GDAL

# please check the output of configure to make sure that the GEOS and PROJ drivers are enabled
# otherwise you might need to define the locations of the packages

cd ${packagedir}/gdal*
./configure --prefix ${installdir} \
            --with-oci-include=${oracle_headers} \
            --with-oci-lib=${oracle_libs} \
            --with-python=${python_type} \
            --with-geos=${installdir}/bin/geos-config \
            --with-proj=${installdir} \
            --with-spatialite=${installdir} \
            --with-fgdb=${fgdb_install_dir}

make -j${threads}
sudo make install
########################################################################################################################
# install GDAL Python binding inside a virtual environment

python -m pip install gdal==$GDALVERSION --global-option=build_ext --user --global-option="-I$installdir/include"
########################################################################################################################
########################################################################################################################
# install pysqlite2 python package with static sqlite3 build
# this needs git to be installed

cd ${packagedir}
git clone https://github.com/ghaering/pysqlite.git
cd pysqlite

wget https://sqlite.org/2019/sqlite-amalgamation-3290000.zip

unzip sqlite-amalgamation-3290000.zip
cp sqlite-amalgamation-3290000/* .

sudo python setup.py build_static install --prefix=${installdir}
########################################################################################################################
########################################################################################################################
# finishing the process

echo depending on your choice of installdir and Python version you might need to add the following lines to your .bashrc:
echo "export PATH=${installdir}/bin:$"PATH
echo "export LD_LIBRARY_PATH=${installdir}/lib:$"LD_LIBRARY_PATH
echo "export PYTHONPATH=${installdir}/lib64/python3.6/site-packages:$"PYTHONPATH
echo "done"

# deleting the root directory which is no longer needed
#sudo rm -rf ${root}