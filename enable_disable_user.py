#!/usr/bin/python

import MySQLdb
import sys
import re
import json
import subprocess
import openstack

def check_input(argv):
    exception = False

    if(len(argv) != 3):
        print "Usage: minicloud [enable|disable] <user id>"
        exception = True
    else:
        if argv[1] != "--enable" and argv[1] != "--disable":
            print argv[1] + ": Invalid Option."
            print "Usage: minicloud [enable|disable] <user id>"
            exception = True

        if not openstack.is_valid_user_id(argv[2]):
            print "Invalid User ID."
            exception = True

    if exception == True:
        raise Exception

if __name__== "__main__":
    try:
        check_input(sys.argv)
    except:
        sys.exit()

    user_id = sys.argv[2]
    project_id = openstack.get_default_project(user_id)
    routers_ids = openstack.get_routers(project_id)
    networks_ids = openstack.get_networks(project_id)

    if(sys.argv[1] == "--enable"):
        openstack.enable_user(user_id)
        openstack.enable_routers(routers_ids)
        openstack.enable_networks(networks_ids)
    else:
        openstack.disable_user(user_id)
        openstack.disable_routers(routers_ids)
        openstack.disable_networks(networks_ids)
