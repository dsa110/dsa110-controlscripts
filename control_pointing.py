"""
Automated slew across a calibrator source.
"""
import time
import argparse
import numpy as np
from dsautils.dsa_store import DsaStore
from dsautils.cnf import Conf
ETCD = DsaStore()
ANTENNAS = list(Conf().get('corr')['antenna_order'].values())
OFFSETS = Conf().get('cal')['el_offset']

def move_and_wait(newposition : float, refants : list, timeout : float = 30, tol : float = 0.99):
    """Move antennas to `newposition` and wait for settling.

    `refants` are not moved.  `newposition` is in deg and (imprecise) timeout in s.
    """
    elapsed = 0.0
    for ant in ANTENNAS:
        if ant not in refants:
            ETCD.put_dict(
                f'/cmd/ant/{ant}',
                {'cmd': 'move', 'val': newposition-OFFSETS.get(ant, 0)}
            )
            time.sleep(1e-3)
            elapsed += 1e-3
    antenna_moved = np.zeros(len(ANTENNAS), dtype=np.bool)
    while elapsed < timeout:
        for i, ant in enumerate(ANTENNAS):
            if not antenna_moved[i]:
                antdict = ETCD.get_dict(f'/mon/ant/{ant}')
                if antdict is not None and antdict['drv_state'] == 2:
                    antenna_moved[i] = True
        if antenna_moved.mean() > tol:
            return 0
        time.sleep(3)
        elapsed += 3.
    return 1

def report_status(status : int, current_el : float):
    """Report the status of the last move command.
    """
    if status > 0:
        print(f'Timeout moving to {current_el}')
    else:
        print(f'Successful move to {current_el}')

def slew_across(home_el : float, refants : list, range_el : float=20.0, step_el : float=0.4):
    """Slew across the calibator source at `home_el`, over a range of `range_el`
    in steps of `step_el.  Hold `refants` constant.

    `home_el`, `range_el` and `step_el` are in deg
    """
    current_el = home_el-range_el/2
    # Move antennas to the starting point
    status = move_and_wait(current_el, refants, timeout=120)
    report_status(status, current_el)
    while current_el < home_el+range_el/2:
        current_el += step_el
        status = move_and_wait(current_el, refants)
        report_status(status, current_el)

def report_commanded_elevation():
    """Report the mean commanded elevation of all antennas.
    """
    commanded_els = np.ones(len(ANTENNAS), dtype=float)*np.nan
    for i, ant in enumerate(ANTENNAS):
        antdict = ETCD.get_dict(f'/mon/ant/{ant}')
        if antdict is not None:
            commanded_els[i] = antdict['ant_cmd_el']
    return np.nanmean(commanded_els)

def main():
    """Parse arguments and run.
    """
    parser = argparse.ArgumentParser(description='Point antennas or slew antennas across a calibrator source.')
    parser.add_argument('command', type=str, choices=['point', 'slew_over'], help='whether to point all antennas or slew over a calibrator source')
    parser.add_argument('--el', type=float,
                        help='the elevation to slew across or point to')
    parser.add_argument('--range', type=float, default=20.,
                        help='the range across which to slew')
    parser.add_argument('--step', type=float, default=0.4,
                        help='the step size in elevation')
    parser.add_argument('--refants', type=str, default='')
    args = parser.parse_args()
    if args.refants == '':
        refants = []
    else:
        refants = [int(itm) for itm in args.refants.strip('[').strip(']').split(',')]
    print(args.command)
    if args.command == 'point':
        move_and_wait(args.el, refants)
    else:
        current_el = report_commanded_elevation()
        if np.abs(current_el-args.el) > args.range*2.1:
            print(f'Current elevation of {current_el} more than {2.1*args.range} from source elevation of {args.el}.  Please move antennas and rerun script.')
        else:
            slew_across(args.el, refants, range_el=args.range, step_el=args.step)

if __name__=='__main__':
    main()
