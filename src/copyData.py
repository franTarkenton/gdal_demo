'''
Gets a list of data in oracle,
assembles datamigration ogr2ogr commands, set these env vars to run this
script

export ORA_USER=
export ORA_PASSWD =
export ORA_HOST=
export ORA_PORT=
export ORA_SN=

export ACC_KEY=
export ACC_SCRT_KEY=


'''
# dealing with path to the oracle client, this can all be removed if you set up
# your PATH env var with the path to the instant client... I want to keep this
# as portable as possible so keeping in code for now.
import sys
import os
os.environ['ORACLE_HOME'] = r'C:\Kevin\tools\ora\instantclient_19_3'
sys.path.append(os.environ['ORACLE_HOME'])
pthList = os.environ['PATH'].split(';')
pthList.insert(0,os.environ['ORACLE_HOME'])
path = ';'.join(pthList)
os.environ['PATH'] = path
#print('\n'.join(sys.path))
#print(os.environ['PATH'])

import cx_Oracle
import subprocess
import re
import minio
import gzip
import logging

LOGGER = logging.getLogger(__name__)

class Oracle2PostGIS:
    '''
    functionality to dump data out of oracle into whatever the specified format
    is.
    '''

    def __init__(self, ora_user, ora_pass, ora_host, ora_port, ora_sn, out_path):
        """[summary]

        :param ora_user: [description]
        :type ora_user: [type]
        :param ora_pass: [description]
        :type ora_pass: [type]
        :param ora_host: [description]
        :type ora_host: [type]
        :param ora_port: [description]
        :type ora_port: [type]
        :param ora_sn: [description]
        :type ora_sn: [type]
        :param out_path: [description]
        :type out_path: [type]
        :param out_ogr_format: [description], defaults to 'ESRI Shapefile'
        :type out_ogr_format: str, optional
        """
        self.ora_user = ora_user
        self.ora_pass = ora_pass
        self.ora_host = ora_host
        self.ora_port = ora_port
        self.ora_sn = ora_sn
        self.out_path = out_path

        # cx_Oracle.makedsn(host, port, sid=None, service_name=None, region=None, sharding_key=None, super_sharding_key=None)
        self.dsn = cx_Oracle.makedsn(self.ora_host, self.ora_port,
                                    service_name=self.ora_sn)
        if not os.path.exists(out_path):
            os.mkdir(out_path)
        print(f'dsn: {self.dsn}')

        # populated when needed, contains reference to miniowrapper object
        self.minio = None
        self.s3bucketname = 'pgdump'

    def getTables(self, schema):
        """Hits oracle and returns a list fo the tables in the schema

        :param schema: The oracle schema that you want the table list for.
        :type schema: str
        :return: a list of tables in the provided schema
        :rtype: list
        """
        conn = cx_Oracle.connect(self.ora_user, self.ora_pass, self.dsn)
        table_list_sql = f"select table_name from all_tables where owner = '{schema}'"
        cur = conn.cursor()
        cur.execute(table_list_sql)
        results = cur.fetchall()
        return results

    def filterTables(self, tableList):
        '''
        iterates the list looking for system tables that start with mdrt or mdxt
        and removes them from the list

        '''
        filteredList = []
        mdconfig_re = re.compile('^MD(XT|RT)_.*')
        for table in tableList:
            if isinstance(table, tuple):
                table = table[0]
            if not mdconfig_re.match(table):
                filteredList.append(table)
        return   filteredList

    def copyTablestoPGDUMP(self, schema, maxTables=None):
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
        tbl_cnt = 0
        max_tables = 20
        out_format = 'PGDUMP'

        LOGGER.debug(f"output gdal format: {out_format}")
        # HAVE to add the param -lco or the output PGDUMP file will not be valid
        # and will include a blank string for the geometry field which will not
        # be valid when it comes to loading to the database
        commandTemplate = 'ogr2ogr -nln {2} ' + \
                          ' -lco GEOMETRY_NAME=geom ' + \
                          f'-unsetFid --config SCHEMA NO --config EXTRACT_SCHEMA_FROM_LAYER_NAME NO -f "{out_format}" ' + \
                          '{0}' + f' OCI:"{self.ora_user}/' + \
                          f'{self.ora_pass}@(DESCRIPTION=' + \
                          '(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST' + \
                          f'={self.ora_host})(PORT={self.ora_port})))' + \
                          f'(CONNECT_DATA=(SERVICE_NAME={self.ora_sn}))):' + \
                          f'{schema}.' + "{1}" + '"'

        tables = self.getTables(schema)
        tables = self.filterTables(tables)
        
        for table in tables:
            LOGGER.debug(f"working on the table: {table}")
            dumpFile = os.path.join(self.out_path, f'{table}.pgdump')
            ogrCmd = commandTemplate.format(dumpFile, table, table.lower())

            self.copyTableAndZip(ogrCmd)
            self.copy_s3(zippedDumpFile)
            if (maxTables is not None) and tbl_cnt > maxTables:
                LOGGER.info(f'maximumm number of tables: {maxTables} to ' + \
                            'dump has been attained')
                break
            tbl_cnt += 1
        
    def copyTableAndZip(self, command, outputFile):
        """Get an OGR command to run that creates the output file, then 
        zips up the output file.

        :param command: the ogr command to run that will create the output file
        :type command: str
        :param outputFile: the output file that will be created from the ogr 
            command, this is the file that will get gzipped.
        """
        zippedOutputFile = outputFile + '.gz'
        if not os.path.exists(zippedOutputFile):
            if not os.path.exists(outputFile):
                LOGGER.info(f"dumping data to: {os.path.basename(outputFile)}")
                self.exec_ogr(command)
            LOGGER.info(f'Gzipping file {os.path.basename(outputFile)} to {os.path.basename(zippedOutputFile)}')
            with open(dumpFile, 'rb') as src_fh:
                with gzip.open(zippedDumpFile, 'wb') as gzp_fh:
                    gzp_fh.writelines(src_fh)

    def exec_ogr(self, cmd):
        """execute a cmd using subprocess, outputting the lines to the log.  
        If executed on windows adds CMD call to the front of the commaand
        
        :param cmd: a string the describes the command that needs to be executed.
        :type cmd: str
        """
        #cmd = ['ogrinfo', '--formats']
        if sys.platform  == 'win32':
            cmd = ['cmd', '/c'].extend(cmd)
        LOGGER.debug(f"Platform string: {sys.platform}")
        LOGGER.info(f"executing the command: {cmd}")
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, env=os.environ)
        lines = process.communicate()
        linelist = lines[0].decode('UTF-8').split('\n')
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
        #s3bucketname        
        self.minio.copyFile(self.s3bucketname, path)

    def percent_cb(self, complete, total):
        sys.stdout.write('.')
        sys.stdout.flush()

class MinioWrapper:
    """
    wrapper to s3 object storage methods
    """    
    def __init__(self):
        self.minioClient = minio.Minio(os.environ['MINI_URL'],
                                       access_key=os.environ['MINI_KEY'],
                                       secret_key=os.environ['MINI_SCRT_KEY'],
                                       secure=False)
                                       
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
        if  self.object_exists(bucketName, obj_name):
            LOGGER.info(f'removing {obj_name} from s3')
            self.minioClient.remove_object(bucketName, obj_name)
        LOGGER.info(f'uploading {obj_name} to s3')
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
        object_list = self.minioClient.list_objects(bucket_name)
        exists = False
        if object_list:
            for obj in object_list:
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


if __name__ == '__main__':

    # Setup Logging
    LOGGER = logging.getLogger(__name__)
    LOGGER.setLevel(logging.DEBUG)
    hndlr = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s')
    hndlr.setFormatter(formatter)
    LOGGER.addHandler(hndlr)
    LOGGER.debug("test")

    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    ora_pg = Oracle2PostGIS(os.environ['ORA_USER'],
                   os.environ['ORA_PASSWD'],
                   os.environ['ORA_HOST'],
                   os.environ['ORA_PORT'],
                   os.environ['ORA_SN'],
                   outdir)
    ora_pg.copyTables(os.environ['ORA_SCHEMA'])
