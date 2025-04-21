#!/home/ubuntu/anaconda3/envs/casa38/bin/python

import sys
import os
import time as pytime
from time import sleep
from datetime import datetime
#from datetime import timezone
import numpy as np
from dsautils import dsa_store

def get_datestring():

    val = datetime.now()
    datestring = str(val.year)+'_'+str(val.month)+'_'+str(val.day)+'_'+str(val.hour)+'_'+str(val.minute)+'_'+str(val.second)
    return datestring


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
        #now = datetime.now().astimezone(timezone.utc).timestamp()
        now = datetime.utcnow().timestamp()
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
        for i in range(17,21):
            d.put_dict('/cmd/corr/'+str(i), {'cmd':'start', 'val':a['val']})
        pytime.sleep(5)
        for i in range(1,17):
            d.put_dict('/cmd/corr/'+str(i), {'cmd':'start', 'val':a['val']})
        
        pytime.sleep(480)
        os.system('/home/ubuntu/anaconda3/envs/casa38/bin/dsacon corr set')
        
    if a['cmd'] == 'stop':
        d.put_dict('/cmd/corr/0', {'cmd': 'ctrltrigger', 'val': 'flush'})
        pytime.sleep(120)
        os.system('/home/ubuntu/anaconda3/envs/casa38/bin/dsacon corr stop')
        pytime.sleep(60)
        d.put_dict('/cmd/corr/docopy','False')

    if a['cmd'] == 'faststart':
        d.put_dict('/cmd/corr/docopy','True')
        for i in range(17,21):
            d.put_dict('/cmd/corr/'+str(i), {'cmd':'start', 'val':a['val']})
        pytime.sleep(5)
        for i in range(1,17):
            d.put_dict('/cmd/corr/'+str(i), {'cmd':'start', 'val':a['val']})

        pytime.sleep(180)
        os.system('/home/ubuntu/anaconda3/envs/casa38/bin/dsacon corr set')
        
    if a['cmd'] == 'test':
        d.put_dict('/cmd/corr/100', {'cmd': 'test', 'val': '0'})
        pytime.sleep(1)
        os.system('echo tested')
        
# main part of code

schedule = '/home/ubuntu/proj/websrv/temp-clone/actions.npy'

d = dsa_store.DsaStore()

# update trig_ct
for i in np.arange(1,21):
    d.put_dict('/mon/corr/'+str(i)+'/voltage_ct',{'n_trigs':0})

a = np.load(schedule,allow_pickle=True)
for ln in a:

    print(ln)
    pause_until(ln['time'])
    exec_action(ln,d)

pytime.sleep(180)

exec_action({"cmd":"move","val":"124.4"},d)
pytime.sleep(180)
exec_action({"cmd":"move","val":"124.4"},d)
pytime.sleep(10)
exec_action({"cmd":"start","val":"71.6"},d)
    
while True:

    pytime.sleep(3600)
    exec_action({"cmd":"stop","val":"0"},d)
    exec_action({"cmd":"faststart","val":"71.6"},d)
