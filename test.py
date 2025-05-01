from broadlink import *
from broadlink import discover
#from weatherstation.table_project.table_project import broadlink
import os

#ipv4 = os.popen('ip addr show wlan0 | grep "\<inet\>" | awk \'{ print $2 }\' | awk -F "/" \'{ print $1 }\'').read().strip() # this how we take broker ip address in beging of program-
devices = discover(timeout=5, local_ip_address="192.168.68.126")# lets check devices lis
print(devices)