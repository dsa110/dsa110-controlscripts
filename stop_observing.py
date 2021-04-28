#!/usr/bin/env python3

import sys
import os
import time as pytime
from time import sleep
from datetime import datetime
from datetime import timezone
import numpy as np
from dsautils import dsa_store

d.put_dict('/cmd/corr/0', {'cmd': 'trigger', 'val': '0'})
pytime.sleep(120)
os.system('/usr/local/bin/dsacon corr stop')
pytime.sleep(60)
d.put_dict('/cmd/corr/docopy','False')
pytime.sleep(10)


