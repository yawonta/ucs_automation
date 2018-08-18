from ucsmsdk import ucshandle
import re
import time

# prepare arguments for ucsm ip address, user name, and password to access UCSM
parser = argparse.ArgumentParser()
parser.add_argument("ucsm_ip")
parser.add_argument("ucsm_user")
parser.add_argument("ucsm_password")
args = parser.parse_args()

handle = ucshandle.UcsHandle(args.ucsm_ip, args.ucsm_user, args.ucsm_password)
handle.login()

fault_filter = '(severity, "critical|major")'

blade_filter = '(association, "associated")'
list_of_blades = handle.query_classid("ComputeBlade", filter_str=blade_filter)

list_of_racks = handle.query_classid("ComputeRackUnit", filter_str=blade_filter)

handle.logout()
fault_ctr = 0
print("Started fault monitor for blade and rack servers on ucsm %s" % args.ucsm_ip)
while not fault_ctr:
    handle.login()
    list_of_faults = handle.query_classid("FaultInst", filter_str=fault_filter)
    for fault in list_of_faults:
        for server in (list_of_blades + list_of_racks):
            if re.search(server.dn, fault.dn):
                fault_ctr+=1
    handle.logout()
    if fault_ctr:
        print("faults on blades, please investigate")
        for fault in list_of_faults:
            print fault.descr
        exit(0)
    else:
        print("NO FAULT OBSERVED AT:  %s" % time.ctime())
        time.sleep(30)


