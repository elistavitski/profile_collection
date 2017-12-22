# Make ophyd listen to pyepics.
import nslsii

nslsii.configure_base(get_ipython().user_ns, 'iss', pbar=False, bec=False)

# Subscribe metadatastore to documents.
# If this is removed, data is not saved to metadatastore.
RE.subscribe(db.insert)

# convenience imports
# import bluesky.callbacks as bc
# import bluesky.plans as bp
# import bluesky.plan_stubs as bps
# mv, mvr, mov, movr imported

#import bluesky.simulators
#import bluesky.callbacks.broker

from pyOlog.ophyd_tools import *

# Uncomment the following lines to turn on verbose messages for
# debugging.
# import logging
# ophyd.logger.setLevel(logging.DEBUG)
# logging.basicConfig(level=logging.DEBUG)


from pathlib import Path
from historydict import HistoryDict

try:
    RE.md = HistoryDict('/GPFS/xf08id/metadata/bluesky_history.db')
except Exception as exc:
    print(exc)
    RE.md = HistoryDict('{}/.config/bluesky/bluesky_history.db'.format(str(Path.home())))
RE.is_aborted = False

#mds = MDS({'host': 'xf08id-ca1.cs.nsls2.local', 'port': 7770,'timezone': 'US/Eastern'})

#db = Broker(mds, FileStore({'host':'xf08id-ca1.cs.nsls2.local', 'port': 27017, 'database':'filestore'}))


# register_builtin_handlers(db.fs)


def ensure_proposal_id(md):
    if 'proposal_id' not in md:
        raise ValueError("You forgot the proposal_id.")


# Set up default metadata.
RE.md['group'] = 'iss'
RE.md['beamline_id'] = 'ISS'
RE.md['proposal_id'] = None
RE.md_validator = ensure_proposal_id

