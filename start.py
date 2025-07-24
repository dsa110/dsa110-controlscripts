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
            
def exec_action(a,d):

    if a['cmd'] == 'start':
        d.put_dict('/cmd/corr/docopy','True')
        for i in range(17,21):
            d.put_dict('/cmd/corr/'+str(i), {'cmd':'start', 'val':a['val']})
        pytime.sleep(5)
        for i in range(1,17):
            d.put_dict('/cmd/corr/'+str(i), {'cmd':'start', 'val':a['val']})
        
        pytime.sleep(120)
        os.system('/home/ubuntu/anaconda3/envs/casa38/bin/dsacon corr set')

    if a['cmd'] == 'faststart':
        d.put_dict('/cmd/corr/docopy','True')
        for i in range(17,21):
            d.put_dict('/cmd/corr/'+str(i), {'cmd':'start', 'val':a['val']})
        pytime.sleep(5)
        for i in range(1,17):
            d.put_dict('/cmd/corr/'+str(i), {'cmd':'start', 'val':a['val']})

        pytime.sleep(180)
        os.system('/home/ubuntu/anaconda3/envs/casa38/bin/dsacon corr set')

        
    if a['cmd'] == 'stop':
        #d.put_dict('/cmd/corr/0', {'cmd': 'trigger', 'val': '0-flush-'})
        #pytime.sleep(120)
        os.system('/home/ubuntu/anaconda3/envs/casa38/bin/dsacon corr stop')
        pytime.sleep(10)
        d.put_dict('/cmd/corr/docopy','False')
        pytime.sleep(2)
        

# main part of code

d = dsa_store.DsaStore()
DEC = "22.0"
#d.put_dict('/cnf/datestring',get_datestring())

# update trig_ct
for i in np.arange(1,21):
    d.put_dict('/mon/corr/'+str(i)+'/voltage_ct',{'n_trigs':0})

exec_action({"cmd":"start","val":DEC},d)
    
while True:

    pytime.sleep(3600)
    exec_action({"cmd":"stop","val":"0"},d)
    exec_action({"cmd":"faststart","val":DEC},d)


