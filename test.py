import os, time

for i in range(10):
    time.sleep(3)
    fl = "/home/ubuntu/test"+str(i)
    os.system("echo 'hello' >  "+fl)

