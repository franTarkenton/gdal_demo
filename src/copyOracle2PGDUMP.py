"""using the environment variables described below copies the data from a
oracle schema to PGDUMP tables using OGR.  PGDump tables then get copied
to S3 staging area.

Environment Variables:
ORA_USER=<oracle user used to connect to db>
ORA_PASSWD=<password>
ORA_HOST=<oracle host>
ORA_PORT=<oracle port>
ORA_SN=<oracle service name>
ORA_SCHEMA=<oracle schema that is to be dumped>

MINI_KEY=<s3 key>
MINI_SECRET_KEY=<s3 secret key>
MINI_URL=<s3 url/host>
"""

import logging
import OracleData
import copyData
import os

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
oraConfig = OracleData.OraConfig(
    os.environ["ORA_HOST"], os.environ["ORA_PORT"], os.environ["ORA_SN"]
)
outdir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data", "dumpfiles"
)
outdir = os.path.abspath(outdir)
LOGGER.info(f"Output directory: {outdir}")
ora_pg = copyData.Oracle2PostGIS(oraConfig, outdir)
ora_pg.copyTablesToPGDUMP(os.environ["ORA_SCHEMA"], 5)
