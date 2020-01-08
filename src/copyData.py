"""Summary

Gets a list of data in oracle,
assembles datamigration ogr2ogr commands, set these env vars to run this
script

export ORA_USER= <oracle user>
export ORA_PASSWD = <oracle password>
export ORA_HOST= <oracle host>
export ORA_PORT= <oracle port>
export ORA_SN= <oracle service name>


export MINI_KEY= <minio key>
export MINI_SECRET_KEY= <minio secret key>
export MINI_URL= <minio url>

"""
# pylint:disable=wrong-import-position,
#                logging-not-lazy,
#                logging-fstring-interpolation

# dealing with path to the oracle client, this can all be removed if you set up
# your PATH env var with the path to the instant client... I want to keep this
# as portable as possible so keeping in code for now.
import sys
import os
import csv

os.environ["ORACLE_HOME"] = r"C:\Kevin\tools\ora\instantclient_19_3"  # nopep8
sys.path.append(os.environ["ORACLE_HOME"])  # nopep8
pthList = os.environ["PATH"].split(";")  # nopep8
pthList.insert(0, os.environ["ORACLE_HOME"])  # nopep8
path = ";".join(pthList)  # nopep8
os.environ["PATH"] = path  # nopep8

import subprocess
import re
import minio
import gzip
import logging
import OracleData

LOGGER = logging.getLogger(__name__)


class Oracle2CSV(OracleData.OraQuery):
    """Ties together functionality to dump oracle tables to CSV

    :param OracleData: Inherits from OraQuery.  Overrides the copyTables method
    :type OracleData: class
    """

    def __init__(self, oraConfig, out_path):
        self.out_path = out_path
        super().__init__(oraConfig)
        self.oraConn = None

    def copyTables(self, schema=None, out_path=None):
        """
        Copies tables from oracle to CSV.
        Csv files will have the same
        name as the table in oracle but with the .csv suffix.  They will
        be copied to the out_path defined in the constructor
        """
        if schema is None:
            schema = os.environ["ORA_SCHEMA"]
        if out_path is None:
            out_path = self.out_path

        if not os.path.exists(out_path):
            LOGGER.info(f"Creating the output path: {out_path}")
            os.mkdir(out_path)

        tableList = self.getTables(schema)
        LOGGER.debug(f"table list: {tableList}")
        for table in tableList:
            outTable = os.path.join(out_path, f"{table}.csv.gz")
            if not os.path.exists(outTable):
                # dump table
                self.copyTable(schema, table, outTable)

    def copyTable(self, schema, table, outTable):
        """Copies the table from the specified schema to a CSV.

        :param schema: Name of the input schema
        :type schema: str
        :param table: name of the table to dump to csv
        :type table: str
        :param outTable: Path to the output csv file
        :type outTable: str
        """
        if not self.oraConn:
            self.oraConn = self.oraConfig.getConnection()

        # set up the cursor
        cur = self.oraConn.cursor()
        LOGGER.debug(f"schema: {schema}  table: {table}")
        cur.execute(f"SELECT * FROM {schema}.{table}")

        # set up output csv
        # outCSVFh = open(outTable, 'w')
        outCSVFh = gzip.open(outTable, "wt")
        csvWriter = csv.writer(
            outCSVFh, delimiter=",", lineterminator="\n", quoting=csv.QUOTE_NONNUMERIC
        )
        LOGGER.info(f"writing data to {outTable}")

        # write the csv header
        header = [head[0] for head in cur.description]
        LOGGER.info(f"header: {header}")
        csvWriter.writerow(header)

        # write the csv
        rowCnt = 0
        for row in cur:
            # remove padding from strings:
            row = [elem.strip() if isinstance(elem, str) else elem for elem in row]
            # LOGGER.debug(f"row: {row}")
            csvWriter.writerow(row)
            rowCnt += 1
        cur.close()
        outCSVFh.close()
        LOGGER.debug(f"table: {table}, {rowCnt}")
        if not rowCnt:
            LOGGER.info(f"removing the empty table: {outTable}")
            os.remove(outTable)


class Oracle2PostGIS(OracleData.OraQuery):
    """
    functionality to dump data out of oracle into whatever the specified format
    is.
    """

    def __init__(self, oraConfig, out_path):
        """[summary]

        :param oraConfig: An oracle config object, provides access to various
            oracle config variables
        :type oraConfig: OraConfig
        :param out_path: Directory where output dump files should be put
        :type out_path: str, path
        """
        self.oraConfig = oraConfig
        self.out_path = out_path

        if not os.path.exists(out_path):
            os.makedirs(out_path)

        # populated when needed, contains reference to miniowrapper object
        self.minio = None
        self.s3bucketname = "pgdump"

    def filterTables(self, tableList):
        """
        Iterates the list looking for system tables that start with mdrt or mdxt
        and removes them from the list

        """
        filteredList = []
        oracleSpatialConfigFiles_regex = re.compile("^MD(XT|RT)_.*")
        for table in tableList:
            if isinstance(table, tuple):
                table = table[0]
            if not oracleSpatialConfigFiles_regex.match(table):
                filteredList.append(table)
        return filteredList

    def copyTablesToPGDUMP(self, schema, maxTables=None):
        """Using the input schema, gets a list of all the non sdo system tables
         in the schema, and then dumps them to the the PGDUMP format.

        :param schema: the input schema in the oracle instance who's tables are
            to be copied to pgdump format.
        :type schema: str
        :param maxTables: limit the number of tables that will be  dumped to
            this number of tables
        :type maxTables: int
        """
        # created a pgdump specific method because getting the correct output
        # in the pgdump format required a bunch of specific options in the
        # og2ogr utility call.
        tableCount = 0
        maxTables = 20
        outFormat = "PGDUMP"

        LOGGER.debug(f"output gdal format: {outFormat}")
        # HAVE to add the param -lco or the output PGDUMP file will not be valid
        # and will include a blank string for the geometry field which will not
        # be valid when it comes to loading to the database
        connParams = self.oraConfig.getUserNamePassword()
        commandTemplate = (
            "ogr2ogr -nln {3} "
            + " -lco GEOMETRY_NAME=geom "
            + "-unsetFid --config SCHEMA NO --config "
            + f'EXTRACT_SCHEMA_FROM_LAYER_NAME NO -f "{outFormat}" '
            + "{0}"
            + f' OCI:"{connParams[0]}/'
            + f"{connParams[1]}@(DESCRIPTION="
            + "(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST"
            + f"={self.oraConfig.host})(PORT={self.oraConfig.port})))"
            + f"(CONNECT_DATA=(SERVICE_NAME={self.oraConfig.servicename}))):"
            + f"{schema}."
            + "{1}"
            + '"'
        )

        tables = self.getTables(schema)
        tables = self.filterTables(tables)

        for table in tables:
            LOGGER.debug(f"working on the table: {table}")
            dumpFile = os.path.join(self.out_path, f"{table}.pgdump")
            ogrCmd = commandTemplate.format(
                dumpFile, table, schema.lower(), table.lower()
            )

            zippedDumpFile = self.copyTableAndZip(ogrCmd, dumpFile)
            self.copy_s3(zippedDumpFile)
            if (maxTables is not None) and tableCount > maxTables:
                LOGGER.info(
                    f"maximumm number of tables: {maxTables} to "
                    + "dump has been attained"
                )
                break
            tableCount += 1

    def copyTableAndZip(self, command, outputFile):
        """Get an OGR command to run that creates the output file, then
        zips up the output file.

        :param command: the ogr command to run that will create the output file
        :type command: str
        :param outputFile: the output file that will be created from the ogr

        :return: the path to the zip file that was ultimately created
        :rtype: str, path
        """

        zippedOutputFile = outputFile + ".gz"
        if not os.path.exists(zippedOutputFile):
            if not os.path.exists(outputFile):
                LOGGER.info(f"dumping data to: {os.path.basename(outputFile)}")
                self.exec_ogr(command)
            LOGGER.info(
                f"Gzipping file {os.path.basename(outputFile)} to "
                + f"{os.path.basename(zippedOutputFile)}"
            )
            with open(outputFile, "rb") as src_fh:
                with gzip.open(zippedOutputFile, "wb") as gzp_fh:
                    gzp_fh.writelines(src_fh)
        if os.path.exists(zippedOutputFile) and os.path.exists(outputFile):
            LOGGER.info(
                "Zip of the file: {outputFile} is not complete. " + " Removing original"
            )
            os.remove(outputFile)
        return zippedOutputFile

    def exec_ogr(self, cmd):
        """Execute a cmd using subprocess, outputting the lines to the log.
        If executed on windows adds CMD call to the front of the commaand

        :param cmd: a string the describes the command that needs to be executed.
        :type cmd: str
        """
        # cmd = ['ogrinfo', '--formats']
        if sys.platform == "win32":
            cmd = ["cmd", "/c"].extend(cmd)
        LOGGER.debug(f"Platform string: {sys.platform}")
        LOGGER.info(f"executing the command: {cmd}")
        process = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, env=os.environ
        )
        lines = process.communicate()
        linelist = lines[0].decode("UTF-8").split("\n")
        for line in linelist:
            LOGGER.info(f"    {line}")

    def copy_s3(self, path):
        """Copies the path to the default S3 bucket that is defined in
        the property: s3bucketname

        :param path: [description]
        :type path: [type]
        """
        if not self.minio:
            self.minio = MinioWrapper()
        # s3bucketname
        self.minio.copyFile(self.s3bucketname, path)


class MinioWrapper:
    """Wrapper to s3 object storage methods"""

    def __init__(self):
        self.minioClient = minio.Minio(
            os.environ["MINI_URL"],
            access_key=os.environ["MINI_KEY"],
            secret_key=os.environ["MINI_SECRET_KEY"],
            secure=False,
        )

    def copyFile(self, bucketName, filePath):
        """Copy the file in the file provided file path to S3.
        the name of the file will be the basename of the filePath after
        being copied to s3

        :param bucketName: the name of the s3 bucket
        :type bucketName: str
        :param filePath: file path to the file that is to be copied
        :type filePath: str
        """
        LOGGER.info(f"copying: {filePath} to s3 bucket: {bucketName}")
        bucketName = bucketName.lower()
        if not self.bucketExists(bucketName):
            self.minioClient.make_bucket(bucketName)
        obj_name = os.path.basename(filePath).lower()
        if self.object_exists(bucketName, obj_name):
            LOGGER.info(f"removing {obj_name} from s3")
            self.minioClient.remove_object(bucketName, obj_name)
        LOGGER.info(f"uploading {obj_name} to s3")
        self.minioClient.fput_object(bucketName, obj_name, filePath)

    def object_exists(self, bucket_name, object_name):
        """Does the object exist in said bucket

        :param bucket_name: the name of the bucket
        :type bucket_name: string
        :param object_name: name of the object who's  existence in said bucket
            is in question
        :type object_name: object_name
        :return: boolean indicating whether the object_name exists in bucket
        :rtype: bool
        """
        objectList = self.minioClient.list_objects(bucket_name)
        exists = False
        LOGGER.debug(f"objectList: {objectList}, is empty {any(objectList)}")
        if any(objectList):
            for obj in objectList:
                if obj.object_name == object_name:
                    exists = True
                    break
        return exists

    def bucketExists(self, bucketName):
        """Returns true or false depending on whether the bucket exists.

        :param bucketName: bucket name
        :type bucketName: str
        :return: boolean indicating if the bucket exists
        :rtype: bool
        """
        bucketName = bucketName.lower()
        bucketList = self.minioClient.list_buckets()
        returnVal = False
        for bucket in bucketList:
            if bucket.name == bucketName:
                returnVal = True
                break
        return returnVal
