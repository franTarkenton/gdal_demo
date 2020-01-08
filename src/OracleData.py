"""Module contains two classes that are inherited to help with copying oracle
data to different formats.

OraConfig: using the environment variables:
ORA_USER=<oracle user used to connect to db>
ORA_PASSWD=<password>
ORA_HOST=<oracle host>
ORA_PORT=<oracle port>
ORA_SN=<oracle service name>
ORA_SCHEMA=<oracle schema that is to be dumped>

creates the required database connections


:raises OraConfigError: When environment variables do not make sense this error
                        will be raised
:raises OraConfigNoUserEnvVarError: When no ORA_USER exists in env vars
:raises OraConfigNoPasswordEnvVarError: When ORA_PASSWD env var doesn't exist
"""

import os
import cx_Oracle
import logging
import re

LOGGER = logging.getLogger(__name__)

# pylint: disable=logging-fstring-interpolation


class OraConfig:
    """using the environment variables described below established a connection
    to an oracle database:

    ORA_USER=<oracle user used to connect to db>
    ORA_PASSWD=<password>
    ORA_HOST=<oracle host>
    ORA_PORT=<oracle port>
    ORA_SN=<oracle service name>
    ORA_SCHEMA=<oracle schema that is to be dumped>
    """

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
        self.hostEnvVarName = "ORA_HOST"
        self.portEnvVarName = "ORA_PORT"
        self.snEnvVarName = "ORA_SN"
        self.userEnvVar = "ORA_USER"
        self.passEnvVar = "ORA_PASSWD"

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
        """Verifies that the host, port, and service name have values.

        :raises OraConfigError: if required config parameter were not provided
        and cannot be retrieved from environment variables
        """
        msgTemplate = (
            "Unable to populate the property {property} either  "
            + "from arguments provided in the constructor or from "
            + "the environment  variable {envVar}"
        )
        if self.servicename is None:
            msg = msgTemplate.format(property="servicename", envVar=self.snEnvVarName)
            raise OraConfigError(msg)
        if self.port is None:
            msg = msgTemplate.format(property="port", envVar=self.portEnvVarName)
        if self.host is None:
            msg = msgTemplate.format(property="host", envVar=self.hostEnvVarName)

    def getDSN(self):
        """Using host port and servicename constructs a DSN that can be used
        to connect to oracle using easy connect syntax, thus eliminates need to
        have a TNSNames file.

        :return: an oracle DSN
        :rtype: str
        """
        dsn = cx_Oracle.makedsn(self.host, self.port, service_name=self.servicename)
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

        msg = (
            "Trying to grab the {varType} from the environment "
            + "variable: {usrEnvVar} however that env var is undefined "
        )
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
        """Constructs and returns a cx_Oracle connection object

        :return: a database connection object
        :rtype: cx_Oracle.connection
        """
        usrPass = self.getUserNamePassword()
        dsn = self.getDSN()
        conn = cx_Oracle.connect(usrPass[0], usrPass[1], dsn)
        return conn


class OraQuery:
    """Used to get get information out of oracle."""

    def __init__(self, oraConfig):
        """[summary]

        :param oraConfig: An oracle config object, provides access to various
            oracle config variables
        :type oraConfig: OraConfig
        :param out_path: Directory where output dump files should be put
        :type out_path: str, path
        """
        self.oraConfig = oraConfig

    def getTables(self, schema, skipOraSpatialTabs=True):
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
        # puts the results in a list of tuples, want to convert to a simple
        # list
        tableList = []
        oraSpatRe = re.compile("^MD[R|X]T_.*$", re.IGNORECASE)
        for result in results:
            if skipOraSpatialTabs:
                if not oraSpatRe.match(result[0]):
                    LOGGER.debug(f"table: {result[0]}")
                    tableList.append(result[0])
            else:
                tableList.append(result[0])
                LOGGER.debug(f"table: {result[0]}")
        return tableList


class OraConfigError(Exception):
    """Error/Exception used to indicate that a required env var is either
    invalid or not defined
    """

    def __init__(self, message):
        self.message = message


class OraConfigNoUserEnvVarError(LookupError):
    """Error for when the env var with the user is not specified

    :param LookupError: base exception
    :type LookupError: exception
    """

    def __init__(self, message):
        self.message = message


class OraConfigNoPasswordEnvVarError(LookupError):
    """Error/Exception used to indicate that the oracle password required to
    connect to the db has not been provided and does not exist in environment
    variable
    """

    def __init__(self, message):
        self.message = message
