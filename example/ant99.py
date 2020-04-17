#!/usr/bin/env python

import sys
from pathlib import Path
sys.path.append(str(Path('..')))
import dsautils.dsa_ant as Ant
#from pkg_resources import Requirement, resource_filename
#etcdconf = resource_filename(Requirement.parse("dsa110-pyutils"), "dsautils/conf/etcdConfig.yml")

import time

def run(ant):
    print("moving antenna")
    ant.move(20.)
    time.sleep(30.)

    print("turning noise a on")    
    ant.noise_a_on(True)
    time.sleep(10.)

    print("turning noise a off, noise b on")        
    ant.noise_a_on(False)
    ant.noise_b_on(True)
    time.sleep(10.)

    print("turning noise a,b off")            
    ant.noise_ab_on(False)

if __name__ == '__main__':
    ant99 = Ant.Ant(99)
    run(ant99)
    
