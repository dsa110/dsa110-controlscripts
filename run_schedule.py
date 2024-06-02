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
        os.system('/home/ubuntu/anaconda3/envs/casa38/bin/dsacon corr start')
        pytime.sleep(600)
        os.system('/home/ubuntu/anaconda3/envs/casa38/bin/dsacon corr set')
        
    if a['cmd'] == 'stop':
        d.put_dict('/cmd/corr/0', {'cmd': 'ctrltrigger', 'val': 'flush'})
        pytime.sleep(120)
        os.system('/home/ubuntu/anaconda3/envs/casa38/bin/dsacon corr stop')
        pytime.sleep(60)
        d.put_dict('/cmd/corr/docopy','False')

    if a['cmd'] == 'trigger':
        d.put_dict('/cmd/corr/0', {'cmd': 'trigger', 'val': a['val']})

    if a['cmd'] == 'ctrltrigger':
        d.put_dict('/cmd/corr/0', {'cmd': 'ctrltrigger', 'val': a['val']})
        
    if a['cmd'] == 'record':
        d.put_dict('/cmd/corr/17', {'cmd': 'record', 'val': a['val']})
        d.put_dict('/cmd/corr/18', {'cmd': 'record', 'val': a['val']})
        d.put_dict('/cmd/corr/19', {'cmd': 'record', 'val': a['val']})
        d.put_dict('/cmd/corr/20', {'cmd': 'record', 'val': a['val']})

    if a['cmd'] == 't2snr':
        t2dict = d.get_dict('/cnf/t2')
        t2dict['min_snr'] = float(a['val'])
        d.put_dict('/cnf/t2',t2dict)

    if a['cmd'] == 't2snrwide':
        t2dict = d.get_dict('/cnf/t2')
        t2dict['min_snr_wide'] = float(a['val'])
        d.put_dict('/cnf/t2',t2dict)

    if a['cmd'] == 'use_gal_dm':
        t2dict = d.get_dict('/cnf/t2')
        t2dict['use_gal_dm'] = int(a['val'])
        d.put_dict('/cnf/t2',t2dict)

    if a['cmd'] == 'max_ibox':
        t2dict = d.get_dict('/cnf/t2')
        t2dict['max_ibox'] = int(a['val'])
        d.put_dict('/cnf/t2',t2dict)

        
    if a['cmd'] == 'test':
        d.put_dict('/cmd/corr/100', {'cmd': 'test', 'val': '0'})
        pytime.sleep(1)
        os.system('echo tested')
        
# main part of code

schedule = '/home/ubuntu/proj/websrv/temp-clone/actions.npy'
#schedule = 'actions.npy'

d = dsa_store.DsaStore()
#d.put_dict('/cnf/datestring',get_datestring())

# update trig_ct
for i in np.arange(1,21):
    d.put_dict('/mon/corr/'+str(i)+'/voltage_ct',{'n_trigs':0})

a = np.load(schedule,allow_pickle=True)
for ln in a:

    print(ln)
    pause_until(ln['time'])
    exec_action(ln,d)



