#!/usr/bin/env python3

import sys
import os
import time
from dsautils import dsa_store; d = dsa_store.DsaStore()

datestring = '26mar21'

d.put_dict('/cnf/datestring',datestring)
d.put_dict('/cmd/corr/docopy','True')

os.system('/usr/local/bin/dsacon corr start')
time.sleep(20)
os.system('/usr/local/bin/dsacon corr set')
time.sleep(3600)

d.put_dict('/cmd/corr/0', {'cmd': 'trigger', 'val': '0'})
time.sleep(120)
os.system('/usr/local/bin/dsacon corr stop')
time.sleep(60)
d.put_dict('/cmd/corr/docopy','False')
time.sleep(10)







