#!/usr/bin/env python3

import sys
import os
import time as pytime
from time import sleep
from datetime import datetime
from datetime import timezone
import numpy as np
from dsautils import dsa_store

def pause_until(time):
    """
    Pause your program until a specific end time.
    'time' is either a valid datetime object or unix timestamp in seconds (i.e. seconds since Unix epoch)
    """
    end = time

    # Convert datetime to unix timestamp
    if isinstance(time, datetime):
        end = time.timestamp()

    # Type check
    if not isinstance(end, (int, float)):
        raise Exception('The time parameter is not a number or datetime object')

    # Now we wait
    while True:
        now = datetime.now().astimezone(timezone.utc).timestamp()
        diff = end - now
        print('waiting: ',diff)

        #
        # Time is up!
        #
        if diff <= 0:
            break
        else:
            # 'logarithmic' sleeping to minimize loop iterations
            sleep(diff / 2)

            
def exec_action(a,d):
    
    if a['cmd'] == 'move':
        d.put_dict('/cmd/ant/0', {'cmd': 'move', 'val': a['val']})
        
    if a['cmd'] == 'start':
        d.put_dict('/cmd/corr/docopy','True')
        os.system('/usr/local/bin/dsacon corr start')
        pytime.sleep(60)
        os.system('/usr/local/bin/dsacon corr set')
        
    if a['cmd'] == 'stop':
        d.put_dict('/cmd/corr/0', {'cmd': 'trigger', 'val': '0'})
        pytime.sleep(120)
        os.system('/usr/local/bin/dsacon corr stop')
        pytime.sleep(60)
        d.put_dict('/cmd/corr/docopy','False')

    if a['cmd'] == 'trigger':
        d.put_dict('/cmd/corr/0', {'cmd': 'trigger', 'val': '0'})
        
    if a['cmd'] == 'record':
        d.put_dict('/cmd/corr/17', {'cmd': 'record', 'val': a['val']})
        d.put_dict('/cmd/corr/18', {'cmd': 'record', 'val': a['val']})
        d.put_dict('/cmd/corr/19', {'cmd': 'record', 'val': a['val']})
        d.put_dict('/cmd/corr/20', {'cmd': 'record', 'val': a['val']})
    
    if a['cmd'] == 'test':
        d.put_dict('/cmd/corr/100', {'cmd': 'test', 'val': '0'})
        pytime.sleep(1)
        os.system('echo tested')
        
# main part of code

schedule = '/home/ubuntu/proj/websrv/temp-clone/actions.npy'
#schedule = 'actions.npy'

d = dsa_store.DsaStore()
d.put_dict('/cnf/datestring','14jun21')

a = np.load(schedule,allow_pickle=True)
for ln in a:

    print(ln)
    pause_until(ln['time'])
    exec_action(ln,d)



