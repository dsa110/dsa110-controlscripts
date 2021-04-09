#!/usr/bin/env python3

import sys
import os
import time
from dsautils import dsa_store; d = dsa_store.DsaStore()

datestring = '9apr21'

d.put_dict('/cnf/datestring',datestring)
d.put_dict('/cmd/corr/docopy','True')

d.put_dict('/cmd/ant/0', {'cmd': 'move', 'val', 99.6})
time.sleep(60)
os.system('/usr/local/bin/dsacon corr start')
time.sleep(60)
os.system('/usr/local/bin/dsacon corr set')
time.sleep(1800)
d.put_dict('/cmd/corr/0', {'cmd': 'trigger', 'val': '0'})
time.sleep(120)
os.system('/usr/local/bin/dsacon corr stop')
time.sleep(60)

d.put_dict('/cmd/ant/0', {'cmd': 'move', 'val', 104.6})
time.sleep(60)
os.system('/usr/local/bin/dsacon corr start')
time.sleep(60)
os.system('/usr/local/bin/dsacon corr set')
time.sleep(1800)
d.put_dict('/cmd/corr/0', {'cmd': 'trigger', 'val': '0'})
time.sleep(120)
os.system('/usr/local/bin/dsacon corr stop')
time.sleep(60)

d.put_dict('/cmd/corr/docopy','False')
time.sleep(10)
