"""
Dumps the data out of oracle schema...

Creates zipped CSV's for tables that do not contain spatial data.

Both spatial and non spatial data also gets dumps to a FGDB.

Uses the following environment variables for oracle connections:

ORA_USER=<oracle user used to connect to db>
ORA_PASSWD=<password>
ORA_HOST=<oracle host>
ORA_PORT=<oracle port>
ORA_SN=<oracle service name>
ORA_SCHEMA=<oracle schema that is to be dumped>


NOT COMPLETE... requires the esri FGDB driver which is additional hassle
to get working.  Just stopping for now.  Could still dump spatial to shape
as another option.
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
#ora_pg.copyTables(schema=os.environ["ORA_SCHEMA"])
ora_pg.copyTable(schema=os.environ["ORA_SCHEMA"], outTable="junk.csv.gz", table="PA_PROTECTED_AREA_POLY")

