import os
import sys
import yaml
import random
import string
from time import sleep
from datetime import datetime
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord, AltAz
from astropy.coordinates import ICRS
from astropy.time import Time
from astropy.table import Table
try:
    from dsautils import dsa_store
    d = dsa_store.DsaStore()
except ImportError:
    print('No dsautils found. Continuing...')


def to_table(sch, show_transitions=True, show_unused=False):
    # TODO: allow different coordinate types                                                                  
    target_names = []
    start_times = []
    end_times = []
    durations = []
    ra = []
    dec = []
    config = []
    for slot in sch.slots:
        if hasattr(slot.block, 'target'):
            start_times.append(slot.start.iso)
            end_times.append(slot.end.iso)
            durations.append(slot.duration.to(u.minute).value)
            target_names.append(slot.block.target.name)
            ra.append(slot.block.target.ra)
            dec.append(slot.block.target.dec)
            config.append(slot.block.configuration)
        elif show_transitions and slot.block:
            start_times.append(slot.start.iso)
            end_times.append(slot.end.iso)
            durations.append(slot.duration.to(u.minute).value)
            target_names.append('TransitionBlock')
            ra.append('')
            dec.append('')
            changes = list(slot.block.components.keys())
            if 'slew_time' in changes:
                changes.remove('slew_time')
            config.append(changes)
        
    return Table([target_names, start_times, end_times, durations,(ra), (dec), config],
                 names=('target', 'start time (UTC)', 'end time (UTC)',
                        'duration (minutes)', 'ra', 'dec', 'configuration'))

def sortFunc(e):
    return e['time'].timestamp()

# to convert to series of actions...
# use transitions to deal with moves
# between transitions, identify start/stop times
# 
def define_actions(tab,sched_start,recording=False):
    
    transition_time = 290*u.second
    transition_time2 = 10*u.second
    start_time = 300*u.second
    stop_time = 180*u.second
    nominal_obs_time = 10800*u.second
    
    actions = []
    
    for ct in np.arange(len(tab)):
        
        if ct==0:
            delta_obs = Time(tab[ct]['end time (UTC)']) - Time(sched_start) - transition_time
            tmove = Time(sched_start)
        else:
            delta_obs = Time(tab[ct]['end time (UTC)']) - Time(tab[ct-1]['end time (UTC)']) - transition_time
            tmove = Time(tab[ct-1]['end time (UTC)'])
            
        psr=False
        if tab[ct]['configuration']['dm'] is not None:
            
            tm = Time(tab[ct]['start time (UTC)']) + 600*u.second
            if recording is True:
                actions.append({'time':tm.datetime, 'cmd':'record','val':'600-'+tab[ct]['target']+'-'})
            
        if tab[ct]['configuration']['trigger'] is True:
            transit_time = Time(tab[ct]['start time (UTC)']) + tab[ct]['duration (minutes)']*u.min/2
            for offset in [-10*u.min, -6*u.min, -3*u.min, 1*u.min, 4*u.min]:
                tm = transit_time+offset
                actions.append(
                    {
                        'time': tm.datetime,
                        'cmd': 'trigger',
                        'val': '0-{0}{1}-'.format(
                            tab[ct]['target'],
                            ''.join([
                                random.choice(string.ascii_lowercase)
                                for i in range(3)
                            ])
                        )
                    }
                )
            
        n_block = (delta_obs.to_value('s')/(start_time + stop_time + nominal_obs_time)).value
        full_blocks = int(np.floor(n_block))
        part_block = n_block - np.floor(n_block)
        
        # move action
        actions.append({'time':tmove.datetime, 'cmd':'move','val':90.-(37.23-tab[ct]['dec'].deg),'config':tab[ct]['configuration']})
        tmove += transition_time
        actions.append({'time':tmove.datetime, 'cmd':'move','val':90.-(37.23-tab[ct]['dec'].deg),'config':tab[ct]['configuration']})
        tmove += transition_time2
        
        # psr?
        psr=False
        if tab[ct]['configuration']['dm'] is not None:
            psr=True
        
        # start/stop actions
        for i in np.arange(full_blocks):
            
            actions.append({'time':tmove.datetime, 'cmd':'start','val':0})
            tmove += start_time + nominal_obs_time
            
            if i<full_blocks-1:
                actions.append({'time':tmove.datetime, 'cmd':'stop','val':0})
                tmove += stop_time
                
            elif i==full_blocks-1:
                if part_block<=0.5:
                    extra_obs_time = part_block*(start_time + stop_time + nominal_obs_time)
                    tmove += extra_obs_time
                    
                    actions.append({'time':tmove.datetime, 'cmd':'stop','val':0})
                    tmove += stop_time
                    
                else:
                    actions.append({'time':tmove.datetime, 'cmd':'stop','val':0})
                    tmove += stop_time
                    
                    
            
        if part_block>0.5:
            
            obs_time = part_block*(start_time + stop_time + nominal_obs_time) - start_time - stop_time
            
            actions.append({'time':tmove.datetime, 'cmd':'start','val':0})
            tmove += start_time + obs_time
            actions.append({'time':tmove.datetime, 'cmd':'stop','val':0})
            tmove += stop_time
            
        if full_blocks==0:
            if part_block<=0.5:
            
                obs_time = part_block*(start_time + stop_time + nominal_obs_time) - start_time - stop_time
            
                actions.append({'time':tmove.datetime, 'cmd':'start','val':0})
                tmove += start_time + obs_time
                actions.append({'time':tmove.datetime, 'cmd':'stop','val':0})
                tmove += stop_time
            
    a = sorted(actions, key = lambda i: i['time'].timestamp())
    return a


def define_actions_simple(srcs,transit_times,max_alts,stimes,end_times,northy,recording=False):
    
    transition_time = 290*u.second
    transition_time2 = 10*u.second
    start_time = 360*u.second
    stop_time = 180*u.second
    
    actions = []
    
    for ct in np.arange(len(transit_times)):
            
        # deal with filterbank recording
        if srcs[ct]['dm'] is not None:
            tm = (transit_times[ct] - 200*u.second)[0]
            if recording is True:
                actions.append({'time':tm.datetime, 'cmd':'record','val':'400-'+srcs[ct]['name']+'-'})
            
            
        if srcs[ct]['trigger'] is True:
            for offset in [-10*u.min, -6*u.min, -3*u.min, 1*u.min, 4*u.min]:
                tm = (transit_times[ct]+offset)[0]
                actions.append(
                    {
                        'time': tm.datetime,
                        'cmd': 'trigger',
                        'val': '0-{0}{1}-'.format(
                            srcs[ct]['name'],
                            ''.join([
                                random.choice(string.ascii_lowercase)
                                for i in range(3)
                            ])
                        )
                    }
                )
            

        # move action
        if northy[ct] is True:
            elevation = (90.-max_alts[ct])+90.
        else:
            elevation = max_alts[ct]
            
        tmove = Time(stimes[ct],format='mjd')
        actions.append({'time':tmove.datetime, 'cmd':'move','val':elevation,'config':None})
        tmove += transition_time
        actions.append({'time':tmove.datetime, 'cmd':'move','val':elevation,'config':None})
        tmove += transition_time2
        
        # start/stop actions
        actions.append({'time':tmove.datetime, 'cmd':'start','val':0})
        tmove = Time(end_times[ct],format='mjd') - stop_time
        actions.append({'time':tmove.datetime, 'cmd':'stop','val':0})

    a = sorted(actions, key = lambda i: i['time'].timestamp())
    return a


# read in sources
def read_srcs(fl):
    with open(fl, 'r') as stream:
        try:
            srcs = yaml.load(stream, Loader=yaml.SafeLoader)
            return(srcs)
        except yaml.YAMLError as exc:
            print('cannot open yaml file')
            
# return start/end times for each source
def return_times_day(srcs, start_time, duration, observer):
    
    # for each source, find transit time
    deltas = np.linspace(0., duration, 6*60*int(duration))*u.hour
    times = start_time + deltas
    transit_times = []
    srcnames = []
    max_alts = []
    northy = []
    repeats = int(np.ceil(max(deltas.value)/24))
    print(repeats)
    for src in srcs['sources']:
        coord=SkyCoord(ra=src['RA'], dec=src['DEC'], unit=(u.hourangle, u.deg))
        for i in range(repeats):
            times0 = times[(deltas.value < (i+1)*24) & (i*24 < deltas.value)]
            aas = coord.transform_to(AltAz(obstime=times0, location=observer))
            alts = aas.alt.value
            azs = aas.az.value

            if (azs.min() < 1) and (alts.max() > 30):
                tt = times0[(azs <= azs.min()) * (azs.min() < 1)]
                print(src['name'], tt, np.max(alts), np.min(azs))
                transit_times.append(tt)
                srcnames.append(src['name'])
                max_alts.append(np.max(alts))
                if coord.dec.deg > 37.23:
                    northy.append(True)
                else:
                    northy.append(False)
            else:
                print(f'{src["name"]} does not transit')
    
    # find times in between transit times
    
    ttimes = np.zeros(len(transit_times))
    for i in range(len(ttimes)):
        ttimes[i] = transit_times[i].mjd
    args = np.argsort(ttimes)
    transit_times = [transit_times[i] for i in args]
    print([(i, np.mod(i, len(srcs['sources']))) for i in args])
    srcs2 = [srcs['sources'][np.mod(i, len(srcs['sources']))] for i in args]
    max_alts = [max_alts[np.mod(i, len(srcs['sources']))] for i in args]
    start_times = []
    end_times = []
    for i in range(len(srcs2)):
        if i==0:
            start_times.append(start_time.mjd)
            end_times.append((0.5*(transit_times[i].mjd+transit_times[i+1].mjd))[0])
        elif i==len(srcs2)-1:
            start_times.append((0.5*(transit_times[i].mjd+transit_times[i-1].mjd))[0])
            end_times.append(start_time.mjd+duration/24)
        else:
            start_times.append((0.5*(transit_times[i].mjd+transit_times[i-1].mjd))[0])
            end_times.append((0.5*(transit_times[i].mjd+transit_times[i+1].mjd))[0])

    return srcs2,transit_times,max_alts,start_times,end_times,northy


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

            
def exec_action(a):
    
    if a['cmd'] == 'move':
        d.put_dict('/cmd/ant/0', {'cmd': 'move', 'val': a['val']})
        
    if a['cmd'] == 'start':
        d.put_dict('/cmd/corr/docopy','True')
        os.system('/usr/local/bin/dsacon corr start')
        sleep(360)
        os.system('/usr/local/bin/dsacon corr set')
        
    if a['cmd'] == 'stop':
        d.put_dict('/cmd/corr/0', {'cmd': 'trigger', 'val': '0-flush-'})
        sleep(120)
        os.system('/usr/local/bin/dsacon corr stop')
        sleep(60)
        d.put_dict('/cmd/corr/docopy','False')

    if a['cmd'] == 'trigger':
        d.put_dict('/cmd/corr/0', {'cmd': 'trigger', 'val': a['val']})
        
    if a['cmd'] == 'record':
        d.put_dict('/cmd/corr/17', {'cmd': 'record', 'val': a['val']})
        d.put_dict('/cmd/corr/18', {'cmd': 'record', 'val': a['val']})
        d.put_dict('/cmd/corr/19', {'cmd': 'record', 'val': a['val']})
        d.put_dict('/cmd/corr/20', {'cmd': 'record', 'val': a['val']})
    
    if a['cmd'] == 'test':
        d.put_dict('/cmd/corr/100', {'cmd': 'test', 'val': '0'})
        sleep(1)
        os.system('echo tested')
