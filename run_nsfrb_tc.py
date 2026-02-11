#!/home/ubuntu/anaconda3/envs/casa38/bin/python
"""
run_nsfrb_tc.py

Same as run_nsfrb.py, but the 'move' command applies per-antenna temperature
correction using pre-computed linear fit solutions, and waits for antennas
to settle before proceeding.

Temperature correction:
    corrected_el = requested_el - (motor_temp * slope + intercept)
    where slope and intercept come from fitsolutions.npy per antenna.
    If no temperature data is available or the correction exceeds 1 degree
    (indicating a bad fit), the uncorrected position is used.
"""

import sys
import os
import time as pytime
from time import sleep
from datetime import datetime
import numpy as np
from dsautils import dsa_store
from dsautils.dsa_store import DsaStore
from dsautils.cnf import Conf

# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

ETCD = DsaStore()
ANTENNAS = list(Conf(use_etcd=True).get('corr')['antenna_order'].values())
print("Antenna list:", ANTENNAS)

# Load temperature-correction fit solutions relative to this script
fitsolns = np.load("/home/ubuntu/proj/websrv/temp-clone/fitsolutions.npy",allow_pickle=True)
fitsolns_antorder = np.load("/home/ubuntu/proj/websrv/temp-clone/fitsolutions_antorder.npy",allow_pickle=True)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def get_datestring():

    val = datetime.now()
    datestring = (str(val.year) + '_' + str(val.month) + '_' + str(val.day)
                  + '_' + str(val.hour) + '_' + str(val.minute) + '_' + str(val.second))
    return datestring


def pause_until(time):
    """
    Pause your program until a specific end time.
    'time' is either a valid datetime object or unix timestamp in seconds
    (i.e. seconds since Unix epoch).
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
        now = datetime.utcnow().timestamp()
        diff = end - now
        print('waiting: ', diff)

        if diff <= 0:
            break
        else:
            # 'logarithmic' sleeping to minimise loop iterations
            sleep(diff / 2)


def move_with_tempcorrection(newposition, timeout=30, tol=0.9):
    """Move every antenna to *newposition* with per-antenna temperature
    correction, then wait for them to settle.

    For each antenna the motor temperature is read from ETCD and a linear
    correction is applied::

        correction  = motor_temp * slope + intercept
        set_el      = newposition - correction

    If no temperature data is available or the absolute correction exceeds
    1 degree (indicating a bad fit), the antenna is moved to the raw
    *newposition* instead.

    Parameters
    ----------
    newposition : float
        Requested elevation in degrees.
    timeout : float
        Maximum time in seconds to wait for antennas to settle.
    tol : float
        Fraction of antennas that must report settled (drv_state == 2)
        before the function returns success.

    Returns
    -------
    int
        0 on success (enough antennas settled), 1 on timeout.
    """
    elapsed = 0.0
    for ant in ANTENNAS:
        # Look up this antenna in the fit-solution arrays
        antidx = list(fitsolns_antorder).index(ant)

        # Read current motor temperature from ETCD
        anttemp = ETCD.get_dict("/mon/ant/" + str(ant))

        if anttemp is None:
            print("Ant " + str(ant) + ": no temp data, using uncorrected position "
                  + str(newposition))
            setposition = newposition
        elif np.abs((anttemp["motor_temp"] * fitsolns[antidx, 0])
                    + fitsolns[antidx, 1]) > 1:
            print("Ant " + str(ant) + ": bad solution, using uncorrected position "
                  + str(newposition))
            setposition = newposition
        else:
            correction = (anttemp["motor_temp"] * fitsolns[antidx, 0]
                          + fitsolns[antidx, 1])
            setposition = newposition - correction
            print("Ant " + str(ant) + " revised elevation from "
                  + str(newposition) + " to " + str(setposition))

        ETCD.put_dict(f'/cmd/ant/{ant}', {'cmd': 'move', 'val': setposition})
        pytime.sleep(1e-3)
        elapsed += 1e-3

    # Wait for antennas to settle (drv_state == 2)
    antenna_moved = np.zeros(len(ANTENNAS))
    while elapsed < timeout:
        for i, ant in enumerate(ANTENNAS):
            if not antenna_moved[i]:
                antdict = ETCD.get_dict(f'/mon/ant/{ant}')
                if antdict is not None and antdict['drv_state'] == 2:
                    antenna_moved[i] = 1
        if antenna_moved.mean() > tol:
            print(f'Antennas settled at position {newposition} (temp-corrected)')
            return 0
        pytime.sleep(3)
        elapsed += 3.

    print(f'Timeout moving to {newposition} (temp-corrected)')
    return 1


def exec_action(a, d):
    """Execute a single schedule action.

    The 'move' command uses per-antenna temperature-corrected positioning
    via `move_with_tempcorrection`.  All other commands are unchanged from
    the original run_nsfrb.py.
    """

    if a['cmd'] == 'move':
        move_with_tempcorrection(float(a['val']))

    if a['cmd'] == 'start':
        d.put_dict('/cmd/corr/docopy', 'True')
        for i in range(17, 21):
            d.put_dict('/cmd/corr/' + str(i), {'cmd': 'start', 'val': a['val']})
        pytime.sleep(5)
        for i in range(1, 17):
            d.put_dict('/cmd/corr/' + str(i), {'cmd': 'start', 'val': a['val']})

        pytime.sleep(600)
        os.system('/home/ubuntu/anaconda3/envs/casa38/bin/dsacon corr set')

    if a['cmd'] == 'stop':

        # edit to avoid missing voltages for previous triggers
        # triggers during these 2 min will likely be missed.
        lastcmd = d.get_dict("/cmd/corr/0")
        if lastcmd['cmd'] == 'trigger':
            if 'flush' not in lastcmd['val']:
                pytime.sleep(120)
        
        #d.put_dict('/cmd/corr/0', {'cmd': 'trigger', 'val': '0-flush-'})
        #pytime.sleep(90)
        os.system('/home/ubuntu/anaconda3/envs/casa38/bin/dsacon corr stop')
        pytime.sleep(10)
        d.put_dict('/cmd/corr/docopy','False')
        pytime.sleep(2)

    if a['cmd'] == 'faststart':
        d.put_dict('/cmd/corr/docopy', 'True')
        for i in range(17, 21):
            d.put_dict('/cmd/corr/' + str(i), {'cmd': 'start', 'val': a['val']})
        pytime.sleep(5)
        for i in range(1, 17):
            d.put_dict('/cmd/corr/' + str(i), {'cmd': 'start', 'val': a['val']})

        pytime.sleep(180)
        os.system('/home/ubuntu/anaconda3/envs/casa38/bin/dsacon corr set')

    if a['cmd'] == 'test':
        d.put_dict('/cmd/corr/100', {'cmd': 'test', 'val': '0'})
        pytime.sleep(1)
        os.system('echo tested')

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

schedule = '/home/ubuntu/proj/websrv/temp-clone/actions.npy'

d = dsa_store.DsaStore()

# update trig_ct
for i in np.arange(1, 21):
    d.put_dict('/mon/corr/' + str(i) + '/voltage_ct', {'n_trigs': 0})

a = np.load(schedule, allow_pickle=True)
for ln in a:

    print(ln)
    pause_until(ln['time'])
    exec_action(ln, d)

pytime.sleep(180)

exec_action({"cmd": "move", "val": "69.04"}, d)
pytime.sleep(180)
exec_action({"cmd": "move", "val": "69.04"}, d)
pytime.sleep(10)
exec_action({"cmd": "start", "val": "16.27"}, d)

while True:

    pytime.sleep(3600)
    exec_action({"cmd": "stop", "val": "0"}, d)
    exec_action({"cmd": "faststart", "val": "16.27"}, d)
