#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb
import subprocess
import sys
import re
import time
import openstack

def yes():
    try:
        answer = raw_input("Continue? [y/n] ")
    except:
        print
        sys.exit()

    if re.match("y$|yes$", answer, flags=re.IGNORECASE):
        return True
    else:
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: minicloud delete <user id>"
        sys.exit()

    if not openstack.is_valid_user_id(sys.argv[1]):
        print "Invalid User ID."
        sys.exit()
    else:
        user_id = sys.argv[1]

    projects = openstack.get_projects(user_id)

    if len(projects) == 0:
        print "User to be deleted:         " + openstack.get_username(user_id)
        print "User doesn't belong to any project. Only user will be deleted."
        if not yes():
            sys.exit()
        else:
            openstack.delete_user(user_id)

    if len(projects) == 1 and openstack.single_user_project(projects[0]):
        print "User to be deleted:         " + openstack.get_username(user_id)
        print "Project to be deleted:      " +\
              openstack.get_project_name(projects[0]) + " (" + projects[0] + ")"
        print "Instance(s) to be deleted: "
        instances = openstack.get_instances_by_name(projects[0])
        for i in range(0, len(instances)):
            print "                            "  + instances[i]
        if not yes():
            sys.exit()
        else:
            openstack.delete_content(projects[0])
            openstack.delete_user(user_id)
            openstack.delete_project(projects[0])

    elif len(projects) == 1 and not openstack.single_user_project(projects[0]):
        print "Project '" + openstack.get_project_name(projects[0]) + "' has "\
              "multiple users. To delete it, remove the other users from it "\
              "and run this script again."
        sys.exit()

    else:
        warning = False
        for i in range(len(projects)-1, -1, -1):
            if not openstack.single_user_project(projects[i]):
                print "Warning: Project '" +\
                      openstack.get_project_name(projects[i]) + "' has "\
                      "multiple users. To delete it, kill this script, remove "\
                      "the other users from it and run this script again."
                projects.pop(i)
                warning = True
        if warning == True:
            print

        print "User to be deleted:         " + openstack.get_username(user_id)
        print "Project(s) to be deleted: "
        for i in range(0, len(projects)):
            print "                            " +\
                  openstack.get_project_name(projects[i]) + " (" +\
                  projects[i] + ")"
        print "Instance(s) to be deleted: "
        for i in range(0, len(projects)):
            instances = openstack.get_instances_by_name(projects[i])
            for j in range(0, len(instances)):
                print "                            "  + instances[j]

        if not yes():
            sys.exit()
        else:
            for i in range(0, len(projects)):
                openstack.delete_content(projects[i])
            openstack.delete_user(user_id)
            for i in range(0, len(projects)):
                openstack.delete_project(projects[i])
