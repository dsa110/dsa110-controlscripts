#!/home/ubuntu/anaconda3/envs/casa38/bin/python  

import sys
import os
import time as pytime
from time import sleep
from datetime import datetime
from datetime import timezone
import numpy as np
from dsautils import dsa_store

d = dsa_store.DsaStore()
#d.put_dict('/cmd/corr/0', {'cmd': 'trigger', 'val': '0-flush-'})
#pytime.sleep(120)
os.system('/home/ubuntu/anaconda3/envs/casa38/bin/dsacon corr stop')
#pytime.sleep(60)
#d.put_dict('/cmd/corr/docopy','False')
pytime.sleep(10)


