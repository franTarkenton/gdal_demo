"""
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
# pylint:disable=wrong-import-position, logging-not-lazy, logging-fstring-interpolation

# dealing with path to the oracle client, this can all be removed if you set up
# your PATH env var with the path to the instant client... I want to keep this
# as portable as possible so keeping in code for now.
import sys
import os

os.environ["ORACLE_HOME"] = r"C:\Kevin\tools\ora\instantclient_19_3"
sys.path.append(os.environ["ORACLE_HOME"])
pthList = os.environ["PATH"].split(";")
pthList.insert(0, os.environ["ORACLE_HOME"])
path = ";".join(pthList)
os.environ["PATH"] = path
# print('\n'.join(sys.path))
# print(os.environ['PATH'])

import cx_Oracle
import subprocess
import re
import minio
import gzip
import logging

LOGGER = logging.getLogger(__name__)

class OraConfig:
    def __init__(self, host=None, port=None, servicename=None):
        """constructor, for ora config... allows for override of config 
        parameters.  if not provided they get retrieved from environment
        variables
        
        :param host: the oracle host, defaults to None
        :type host: str, optional
        :param port: the oracle port, defaults to None
        :type port: str, optional
        :param servicename: the oracle service name, defaults to None
        :type servicename: str, optional
        """
        self.hostEnvVarName = 'ORA_HOST'
        self.portEnvVarName = 'ORA_PORT'
        self.snEnvVarName = 'ORA_SN'
        self.userEnvVar = 'ORA_USER'
        self.passEnvVar = 'ORA_PASSWD'

        self.host = host
        self.port = port
        self.servicename = servicename

        # if these params are not set then try to get from env vars
        if self.host is not None:
            self.host = os.environ[self.hostEnvVarName]
        if self.port is not None:
            self.port = os.environ[self.portEnvVarName]
        if self.servicename is not None:
            self.servicename = os.environ[self.snEnvVarName]
        self.checkSelf()

    def checkSelf(self):
        """verifies that the host, port, and service name have values.
        
        :raises OraConfigError: if required config parameter were not provided
        and cannot be retrieved from environment variables
        """
        msgTemplate = "Unable to populate the property {property} either  " + \
                  "from arguments provided in the constructor or from " + \
                  "the environment  variable {envVar}"
        if self.servicename is None:
            msg = msgTemplate.format(property='servicename', envVar=self.snEnvVarName)
            raise OraConfigError(msg)
        if self.port is None:
            msg = msgTemplate.format(property='port', envVar=self.portEnvVarName)
        if self.host is None:
            msg = msgTemplate.format(property='host', envVar=self.hostEnvVarName)

    def getDSN(self):
        """Using host port and servicename constructs a DSN that can be used
        to connect to oracle using easy connect syntax, thus eliminates need to 
        have a TNSNames file.
        
        :return: an oracle DSN
        :rtype: str
        """
        dsn = cx_Oracle.makedsn(
            self.host, self.port, service_name=self.servicename
        )
        LOGGER.info(f"DSN: {dsn}")
        return dsn

    def getUserNamePassword(self, usrEnvVar=None, passEnvVar=None):
        """Either using default environment variables or the override 
        environment variables provided to this method, returns a list 
        [username, password]
        
        :param usrEnvVar: override env var to use to get the oracle 
            username, defaults to None
        :type usrEnvVar: str, optional
        :param passEnvVar: override env var to use to retrieve the oracle 
            password, defaults to None
        :type passEnvVar: str, optional
        :raises OraConfigNoUserEnvVarError: if the username cannot be resolved
        :raises OraConfigNoPasswordEnvVarError: if the password cannot be resolved
        :return: two element list [username, password]
        :rtype: list
        """
        if usrEnvVar is None:
            usrEnvVar = self.userEnvVar
        if passEnvVar is None:
            passEnvVar = self.passEnvVar
                    
        msg = "Trying to grab the {varType} from the environment " + \
                "variable: {usrEnvVar} however that env var is undefined "
        if usrEnvVar not in os.environ:
            varType = "oracle username"
            msg = msg.format(varType=varType, usrEnvVar=usrEnvVar)
            raise OraConfigNoUserEnvVarError(msg)
        if passEnvVar not in os.environ:
            varType = "oracle password"
            msg = msg.format(varType=varType, usrEnvVar=varType)
            raise OraConfigNoPasswordEnvVarError(msg)
        return [os.environ[usrEnvVar], os.environ[passEnvVar]]

    def getConnection(self):
        """constructs and returns a cx_Oracle connection object
        
        :return: a database connection object
        :rtype: cx_Oracle.connection
        """
        usrPass = self.getUserNamePassword()
        dsn = self.getDSN()
        conn = cx_Oracle.connect(usrPass[0], usrPass[1], dsn)
        return conn

class Oracle2PostGIS:
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

    def getTables(self, schema):
        """Hits oracle and returns a list fo the tables in the schema

        :param schema: The oracle schema that you want the table list for.
        :type schema: str
        :return: a list of tables in the provided schema
        :rtype: list
        """
        conn = self.oraConfig.getConnection()
        table_list_sql = f"select table_name from all_tables where owner = '{schema}'"
        cur = conn.cursor()
        cur.execute(table_list_sql)
        results = cur.fetchall()
        return results

    def filterTables(self, tableList):
        """
        iterates the list looking for system tables that start with mdrt or mdxt
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
            "ogr2ogr -nln {2} "
            + " -lco GEOMETRY_NAME=geom "
            + '-unsetFid --config SCHEMA NO --config '
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
            ogrCmd = commandTemplate.format(dumpFile, table, table.lower())

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
                f"Gzipping file {os.path.basename(outputFile)} to {os.path.basename(zippedOutputFile)}"
            )
            with open(outputFile, "rb") as src_fh:
                with gzip.open(zippedOutputFile, "wb") as gzp_fh:
                    gzp_fh.writelines(src_fh)
        if os.path.exists(zippedOutputFile) and os.path.exists(outputFile):
            LOGGER.info("Zip of the file: {outputFile} is not complete. " + \
                        " Removing original")
            os.remove(outputFile)
        return zippedOutputFile

    def exec_ogr(self, cmd):
        """execute a cmd using subprocess, outputting the lines to the log.  
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

    def percent_cb(self, complete, total):
        sys.stdout.write(".")
        sys.stdout.flush()


class MinioWrapper:
    """
    wrapper to s3 object storage methods
    """

    def __init__(self):
        self.minioClient = minio.Minio(
            os.environ["MINI_URL"],
            access_key=os.environ["MINI_KEY"],
            secret_key=os.environ["MINI_SECRET_KEY"],
            secure=False,
        )

    def copyFile(self, bucketName, filePath):
        """copy the file in the file provided file path to S3.  
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
        """returns true or false depending on whether the bucket exists.
        
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

class OraConfigNoUserEnvVarError(LookupError):
    def __init__(self, message):
        self.message = message

class OraConfigNoPasswordEnvVarError(LookupError): 
    def __init__(self, message):
        self.message = message

class OraConfigError(Exception):
    def __init__(self, message):
        self.message = message


if __name__ == "__main__":

    # ---- Setup Logging ----
    LOGGER = logging.getLogger(__name__)
    LOGGER.setLevel(logging.DEBUG)
    logHandler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s"
    )
    logHandler.setFormatter(formatter)
    LOGGER.addHandler(logHandler)
    LOGGER.debug("test")

    # ---- setup ----
    oraConfig = OraConfig(os.environ["ORA_HOST"], os.environ["ORA_PORT"],
                          os.environ["ORA_SN"])
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
        "data", "dumpfiles")
    outdir = os.path.abspath(outdir)
    LOGGER.info(f'Output directory: {outdir}')
    ora_pg = Oracle2PostGIS(oraConfig, outdir)
    ora_pg.copyTablesToPGDUMP(os.environ["ORA_SCHEMA"], 5)
