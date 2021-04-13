#!/usr/bin/env python3

import datetime
import os
import time
from dsautils import dsa_store
from astropy.time import Time
d = dsa_store.DsaStore()

cals = {
    '3C48' : {
        'el': 85.93,
        'slew': 4,
        'before': 30,
        'after': 30+153
    },
    '3C138' : {
        'el': 69.41,
        'slew': 4,
        'before': 30,
        'after': 4
    },
    '3C147' : {
        'el': 102.62,
        'slew': 7,
        'before': 2,
        'after': 29+87
    },
    '3C196' : {
        'el': 100.98,
        'slew': 1,
        'before': 30,
        'after': 30+246
    },
    '3C286' : {
        'el': 83.28,
        'slew': 4,
        'before': 30,
        'after': 4
    },
    '3C295' : {
        'el': 104.99,
        'slew': 5,
        'before': 2,
        'after': 30
    }
}
datestring = '13apr21'
start = Time('2021-04-13T19:33:55.870')

d.put_dict('/cnf/datestring',datestring)
d.put_dict('/cmd/corr/docopy','True')

now = Time(datetime.datetime.utcnow())
time.sleep(int(start-now))

# 3C48 - start at 
for cal in cals:
    d.put_dict('/cmd/ant/0', {'cmd': 'move', 'val': cal['el']})
    time.sleep(cal['slew']*60)
    d.put_dict('/cmd/ant/0', {'cmd': 'move', 'val': cal['el']})
    time.sleep(cal['slew']*60)
    os.system('/usr/local/bin/dsacon corr start')
    time.sleep(60)
    os.system('/usr/local/bin/dsacon corr set')
    time.sleep((cal['before']-2)*60)
    for i in range(3):
        d.put_dict('/cmd/corr/0', {'cmd': 'trigger', 'val': '0'})
        time.sleep(60*2)
    time.sleep((cal['after']-4)*60)
    os.system('/usr/local/bin/dsacon corr stop')
    time.sleep(60)

d.put_dict('/cmd/corr/docopy','False')
time.sleep(10)
