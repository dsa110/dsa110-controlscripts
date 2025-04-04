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
    
    if a == 'start':
        d.put_dict('/cmd/corr/docopy','True')
        os.system('/usr/local/bin/dsacon corr start')
        pytime.sleep(600)
        os.system('/usr/local/bin/dsacon corr set')
        
    if a == 'stop':
        d.put_dict('/cmd/corr/0', {'cmd': 'trigger', 'val': '0-flush-'})
        pytime.sleep(120)
        os.system('/usr/local/bin/dsacon corr stop')
        pytime.sleep(60)
        d.put_dict('/cmd/corr/docopy','False')
        

# main part of code

d = dsa_store.DsaStore()

while True:

    exec_action('stop',d)
    pytime.sleep(60)
    exec_action('start',d)
    pytime.sleep(3600*4.)


