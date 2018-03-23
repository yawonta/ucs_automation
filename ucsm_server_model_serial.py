#!/usr/bin/python

__author__ = "Yonatan Wonta"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Yonatan Wonta"
__status__ = "test"

#Execution: python ucsm_server_model_serial.py 1.1.1.1 testuser TestPassw0rd
#Execution: python ucsm_server_model_serial.py FI_VIP USERNAME PASSWORD

from ucsmsdk import ucshandle
import argparse
from urllib2 import URLError
from ucsmsdk.ucsexception import UcsException
import pprint

# prepare arguments for ucsm ip address, user name, and password to access UCSM
parser = argparse.ArgumentParser()
parser.add_argument("ucsm_ip")
parser.add_argument("ucsm_user")
parser.add_argument("ucsm_pass")
args = parser.parse_args()

def ucsm_connection(ucsm_ip, username, password):
    """
    this function will connect to ucsm IP and return handle
    """
    handle = ucshandle.UcsHandle(ucsm_ip.strip(), username.strip(),
                                 password.strip())
    return handle


def login_to_ucsm(handle):
    """
    function to login to ucsm
    :param handle:
    :return login status, LOGIN_SUCCESS, LOGIN_FAIL:
    """
    try:
        handle.login()
        return 1
    except URLError:
        print "Not a ucsm device"
    except UcsException:
        print "wrong username or password"
    return 0


def log_out_ucsm(handle):
    """
    function to log out of ucsm
    :param handle:
    :return logout status, LOGOUT_SUCCESS, LOGOUT_FAIL:
    """
    try:
        handle.logout()
        return 1
    except:
        return 0


def get_server_serial_number(handle, server_type):
    """
    function to get blade and rack model and serial number
    :param handle:
    :param server_type
    :return: dictionary of server model and serial number
    """
    model_serial = {}
    if server_type.lower() == 'blade':
        blades = handle.query_classid("ComputeBlade")
        for blade in blades:
            model_serial[blade.serial] = blade.model
    elif server_type.lower() == 'rack':
        racks = handle.query_classid("ComputeRackUnit")
        for rack in racks:
            model_serial[rack.serial] = rack.model
    return model_serial

if __name__ == '__main__':
    h = ucsm_connection(args.ucsm_ip.strip(), args.ucsm_user.strip(), args.ucsm_pass.strip())
    if login_to_ucsm(h):
        print "successfuly logged into ucsm %s" % args.ucsm_ip.strip()
    else:
        print "login failed"
        login_to_ucsm(h)
        exit()
    print "Getting serial number and model for blade servers"
    print "=================================================="
    pprint.pprint(get_server_serial_number(h, 'blade'), width=1)
    print "\nGetting serial number and model for rack servers"
    print "=================================================="
    pprint.pprint(get_server_serial_number(h, 'rack'), width=1)
    if log_out_ucsm(h):
        print "successfully logged out of ucsm %s" % args.ucsm_ip.strip()
    else:
        print "logout of ucsm %s failed" % args.ucsm_ip.strip()
