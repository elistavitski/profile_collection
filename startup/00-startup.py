# Make ophyd listen to pyepics.
from ophyd import setup_ophyd
setup_ophyd()

import sys
#sys.path.insert(0, './.ipython/') # To be able to import files from .ipython directory

# Subscribe metadatastore to documents.
# If this is removed, data is not saved to metadatastore.
# import metadatastore.commands
from metadatastore.mds import MDS
from databroker import Broker
from databroker.core import register_builtin_handlers
from filestore.fs import FileStore
from bluesky.global_state import gs

RE = gs.RE  # convenience alias
from historydict import HistoryDict
RE.md = HistoryDict('/GPFS/xf08id/metadata/bluesky_history.db') #/home/istavitski/.config/bluesky/bluesky_history.db

# At the end of every run, verify that files were saved and
# print a confirmation message.
from bluesky.callbacks.broker import verify_files_saved, post_run
# gs.RE.subscribe('stop', post_run(verify_files_saved))

# Import matplotlib and put it in interactive mode.
import matplotlib.pyplot as plt
plt.ion()

# Make plots update live while scans run.
from bluesky.utils import install_qt_kicker
install_qt_kicker()

# Optional: set any metadata that rarely changes.
# RE.md['beamline_id'] = 'YOUR_BEAMLINE_HERE'

# convenience imports
from ophyd.commands import *
from bluesky.callbacks import *
from bluesky.spec_api import *
from bluesky.global_state import gs, abort, stop, resume
# from databroker import (DataBroker as db, get_events, get_images,
#                         get_table, get_fields, restream, process)
# import metadataclient.mds as mdc
# db.mds = mdc.MDS({'host': 'xf08id-ca1.cs.nsls2.local', 'port': 7601,
#		    'timezone': 'US/Eastern'})


mds = MDS({'host':'xf08id-ca1.cs.nsls2.local', 
	   'database': 'datastore', 'port': 27017, 'timezone': 'US/Eastern'}, auth=False)

db = Broker(mds, FileStore({'host':'xf08id-ca1.cs.nsls2.local', 'port': 27017, 'database':'filestore'}))
register_builtin_handlers(db.fs)
# gs.RE.subscribe_lossless('all', db.mds.insert)
gs.RE.subscribe('all', mds.insert)

from time import sleep
import numpy as np
from bluesky.plan_tools import print_summary


# Uncomment the following lines to turn on verbose messages for debugging.
# import logging
# ophyd.logger.setLevel(logging.DEBUG)

# Set up default metadata.
gs.RE.md['group'] = 'iss'
gs.RE.md['beamline_id'] = 'ISS'
