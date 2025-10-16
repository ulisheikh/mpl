#!/usr/bin/env python

import subprocess 

# subprocess.call("ifconfig",shell=True)
subprocess.call("sudo ifconfig wlan0 down",shell=True)
subprocess.call("sudo ifconfig wlan0 hw ether 00:01:02:03:04:05",shell=True)
subprocess.call("sudo ifconfig wlan0 up",shell=True)


