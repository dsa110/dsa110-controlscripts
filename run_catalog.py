#!/usr/bin/python3

import numpy as np
from astropy.time import Time
from astropy.coordinates import EarthLocation
from astropy import units as u
from dsautils import dsa_store
import sched_funcs

d = dsa_store.DsaStore()

# update trig_ct
for i in np.arange(1,21):
    d.put_dict('/mon/corr/'+str(i)+'/voltage_ct',{'n_trigs':0})

# get catalog
catalog = '/home/ubuntu/proj/websrv/temp-clone/catalog.yaml'
srcs = sched_funcs.read_srcs(catalog)
ovro = EarthLocation(lon=-118.2951 * u.deg, lat=37.2317 * u.deg, height=1222 * u.m)
start_time = Time.now()   # or fixed offset from now?

# calculate actions
srcs2, transit_times, max_alts, stimes, end_times, northy = sched_funcs.return_times_day(srcs, start_time, ovro)
schedule = sched_funcs.define_actions_simple(srcs2, transit_times, max_alts, stimes, end_times, northy, recording=True)

# run schedule
for ln in schedule:
    print(ln)
    sched_funcs.pause_until(ln['time'])
    sched_funcs.exec_action(ln, d)
