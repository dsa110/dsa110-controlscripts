#!/usr/bin/env python3

import datetime
import os
import time
from dsautils import dsa_store
d = dsa_store.DsaStore()

datestring = '16apr21'
start = datetime.datetime(2021, 4, 17, 2, 50)

d.put_dict('/cnf/datestring',datestring)
d.put_dict('/cmd/corr/docopy', 'True')

now = datetime.datetime.utcnow()
time.sleep((start-now).seconds)

d.put_dict('/cmd/ant/0', {'cmd': 'move', 'val': 84.24})
time.sleep(5*60)
d.put_dict('/cmd/ant/0', {'cmd': 'move', 'val': 84.24})
time.sleep(5*60)

for i in range(6):
    os.system('/usr/local/bin/dsacon corr start')
    time.sleep(60)
    os.system('/usr/local/bin/dsacon corr set')
    time.sleep(56*60)
    d.put_dict('/cmd/corr/0', {'cmd': 'trigger', 'val': '0'})
    time.sleep(60*2)
    os.system('/usr/local/bin/dsacon corr stop')
    time.sleep(60)

d.put_dict('/cmd/corr/docopy','False')
time.sleep(10)
