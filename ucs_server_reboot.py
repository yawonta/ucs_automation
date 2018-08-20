__author__ = "Yonatan Wonta"
__copyright__ = "Copyright 2017"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Yonatan Wonta"
__status__ = "test"

import os
import re
import time
import pprint
from ucsmsdk import ucshandle
from ucsmsdk.mometa.ls.LsPower import LsPower

def get_ucs_params():
    print("=======================================")
    UCS_IP = raw_input("ENTER UCSM IP:\t\t")
    USER_NAME = raw_input("ENTER UCS USER NAME:\t")
    PASSWORD = raw_input("ENTER PASSWORD:\t\t")
    print("=======================================")
    print("Pinging the UCS IP...")
    if (os.system("ping -c 1 " + UCS_IP.strip() + " >/dev/null 2>&1") !=0):
        print("UCSM IP is not reachable, please verify system is accessible!!!")
        return 0
    else:
        return UCS_IP.strip(), USER_NAME.strip(), PASSWORD.strip()


def check_fault(handle, ucs_obj):
    faults = handle.query_classid("FaultInst")
    fault_obj = []
    for fault in faults:
        for obj in ucs_obj:
            if re.search(obj.dn, fault.dn) and (fault.severity == 'critical' or fault.severity == 'major'):
                fault_obj.append(fault)
    return fault_obj


os.system("clear")
ucs_details  = get_ucs_params()
if ucs_details:
    print("Connecting UCS as user '%s' and IP address '%s'" % (ucs_details[1], ucs_details[0]))
    handle = ucshandle.UcsHandle(ucs_details[0], ucs_details[1], ucs_details[2])
    handle.login()
else:
    print("Cannot reach the UCS server specified, please try again!!!")
    exit()

racks = handle.query_classid("ComputeRackUnit")
blades = handle.query_classid("ComputeBlade")
all_servers = blades + racks

assoc_servers = []
loop_count = 0

print("-----------------------------------------")
for server in all_servers:
    if server.association == "associated":
        assoc_servers.append(server)
        print("(%s) %s" % (loop_count, server.dn))
        loop_count+=1

print("-----------------------------------------")
choices = raw_input("Please Enter The Server to Reboot, Separated by Commas (e.g. 0,1,3,5):\n")
print("-----------------------------------------")
choice = choices.strip().split(",")
print("\nThe Following Servers Will Be Rebooted")
print("-----------------------------------------")
for val in choice:
    print assoc_servers[int(val)].dn
print("-----------------------------------------")
servers_to_reboot = [assoc_servers[int(i)] for i in choice]

faults = check_fault(handle, servers_to_reboot)
if faults:
    print("The following faults are observed")
    for fault in faults:
        print(fault.descr)
    print("Check faults, Clear them, and Re-run the test!!")
    handle.logout()
    exit()

num_of_reboot = int(raw_input("Enter the number of reboot iterations you would like to run\n"))
reboot_count = 0
fault_server = []

while reboot_count < num_of_reboot:
    handle.logout()
    handle.login()
    print("=======================================")
    print("PERFORMING REBOOT %s" % (reboot_count+1))
    print("=======================================\n")
    print(time.ctime())
    if not servers_to_reboot:
        print("There are no servers to reboot, re-run the test with servers to reboot")
        handle.logout()
        exit()
    for server in servers_to_reboot:
        print("REBOOTING SERVER %s WITH SP %s" % (server.dn, server.assigned_to_dn))
        mo = LsPower(parent_mo_or_dn=server.assigned_to_dn, state="hard-reset-immediate")
        handle.set_mo(mo)
        handle.commit()

    time.sleep(240)
    print("\nCHECKING FAULTS AFTER REBOOT...")
    faults = check_fault(handle, servers_to_reboot)
    if faults:
        print("Faults observers, waiting to see if UCSM clears...")
        time.sleep(90)
        faults = check_fault(handle, servers_to_reboot)
        if faults:
            print("THE FOLLOWING FAULTS ARE OBSERVED")
            for fault in faults:
                print(fault.descr)
                print("FAILURE REPORTED AFTER %s REBOOTS, CHECK SYSTEM FOR FAULTS", (reboot_count+1))
                for fault in faults:
                    for server in servers_to_reboot:
                        if re.search(server.dn, fault.dn):
                            fault_server.append((server.dn, "failed at reboot num %s" % reboot_count+1))
                            servers_to_reboot.pop(servers_to_reboot.index(server))

    if fault_server:
        pprint.pprint("Failed Servers: %s" % fault_server)
    time.sleep(30)
    print("\nREBOOT #%s COMPLETED SUCCESSFULLY\n" % (reboot_count+1))
    print(time.ctime())
    reboot_count+=1

print("\nREBOOT TEST COMPLETED SUCCESSFULLY")

