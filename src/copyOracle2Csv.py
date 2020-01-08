"""Copies data from a specified schema to oracle.  Uses the following environment
variables to do this:

ORA_USER=<oracle user used to connect to db>
ORA_PASSWD=<password>
ORA_HOST=<oracle host>
ORA_PORT=<oracle port>
ORA_SN=<oracle service name>
ORA_SCHEMA=<oracle schema that is to be dumped>
"""

import copyData
import OracleData
import os
import logging


# pylint: disable=logging-fstring-interpolation


# ---- Setup Logging ----
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)
logHandler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s"
)
logHandler.setFormatter(formatter)
LOGGER.addHandler(logHandler)
LOGGER.debug("test")

# ---- setup ----
oraConfig = OracleData.OraConfig(os.environ["ORA_HOST"], os.environ["ORA_PORT"],
                                 os.environ["ORA_SN"])
outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                      "data", "csvs")
outdir = os.path.abspath(outdir)
LOGGER.info(f'Output directory: {outdir}')
ora_pg = copyData.Oracle2CSV(oraConfig, outdir)
ora_pg.copyTables(schema=os.environ["ORA_SCHEMA"])
