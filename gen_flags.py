import numpy as np
import sys, os
from dsautils import cnf; c = cnf.Conf(); a = c.get('corr')['antenna_order']

flagged_ants = [10, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 100]

for i_ant in np.arange(1,len(sys.argv)):
    ant = int(sys.argv[i_ant])
    if (ant in np.arange(1,65)):
        flagged_ants.append(int(sys.argv[i_ant]))

f = open('flagants.dat','w')
for i in np.arange(64):
    if (a[str(i)] in flagged_ants):
        print(f'Flagging antenna {a[str(i)]}')
        f.write(f'{i}\n')
f.close()

for corr in ['03','04','05','06','07','08','10','11','12','14','15','16','18','19','21','22']:
    os.system(f'scp flagants.dat corr{corr}.sas.pvt:~/proj/dsa110-shell/dsa110-xengine/scripts')


    
        
