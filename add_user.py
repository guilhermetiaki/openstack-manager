#!/usr/bin/python
# -*- coding: utf-8 -*-

import openstack
import sys
import mail
import re
import subprocess
import argparse

def confirmation():
    try:
        answer = raw_input("Continue? [y/n] ")
    except:
        print
        sys.exit()

    if re.match("y$|yes$", answer, flags=re.IGNORECASE):
        return True
    else:
        return False


def random_password():
    try:
        return subprocess.check_output("openssl rand -base64 18".split()).\
                          strip()
    except:
        print "Error generating password"
        sys.exit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage='minicloud add [--no-last-name] '\
                                     '[--no-email] first_name [last_name] '\
                                     '[email]')
    parser.add_argument('--no-last-name', action='store_true', default=False,
                        dest='no_last_name', help='allow user creation '\
                        'without providing a last name')
    parser.add_argument('--no-email', action='store_true', default=False,
                        dest='no_email', help='allow user creation without '\
                        'providing an email')
    parser.add_argument('first_name')
    parser.add_argument('last_name', nargs='?', default='')
    parser.add_argument('email', nargs='?', default='')

    args = parser.parse_args()

    if args.no_last_name == True and args.no_email == True:
        if args.last_name != '' or args.email != '':
            print "usage: minicloud add [--no-last-name] [--no-email] "\
            "first_name [last_name] [email]"
            print "Too many arguments."
            sys.exit()
    elif args.no_last_name == True and args.no_email == False:
        if args.email != '':
            print "usage: minicloud add [--no-last-name] [--no-email] "\
            "first_name [last_name] [email]"
            print "Too many arguments."
            sys.exit()
        elif args.last_name == '':
            print "usage: minicloud add [--no-last-name] [--no-email] "\
            "first_name [last_name] [email]"
            print "Too few arguments"
            sys.exit()
        # Inverts arguments, since the secound argument is always placed in
        # last_name
        args.email = args.last_name
        args.last_name = ''
    elif args.no_last_name == False and args.no_email == True:
        if args.email != '':
            print "usage: minicloud add [--no-last-name] [--no-email] "\
            "first_name [last_name] [email]"
            print "Too many arguments."
            sys.exit()
        elif args.last_name == '':
            print "usage: minicloud add [--no-last-name] [--no-email] "\
            "first_name [last_name] [email]"
            print "Too few arguments"
            sys.exit()
    else: # args.no_last_name == False and args.no_email == False
        if args.last_name == '' or args.email == '':
            print "usage: minicloud add [--no-last-name] [--no-email] "\
            "first_name [last_name] [email]"
            print "Too few arguments"
            sys.exit()

    first_name = args.first_name
    last_name = args.last_name
    email = args.email

    valid_input = True
    # Check input
    if re.search("^[a-zA-Z]+$", first_name) == None:
        print first_name + ": Invalid first name. Only A-Z allowed."
        valid_input = False
    if last_name != '' and re.search("^[a-zA-Z]+$", last_name) == None:
        print last_name + ": Invalid last name. Only A-Z allowed."
        valid_input = False
    if email != '' and not mail.valid_email(email):
        print email + ": Invalid email."
        valid_input = False
    if not valid_input:
        sys.exit()

    # Check email already registered
    if email != '' and openstack.email_exists(email):
        print "Email already registered. A username reminder will be sent to "\
              "the user."
        if confirmation():
            server = mail.login_smtp()
            username = openstack.get_username_from_email(email)
            body = mail.get_message_body("./duplicated-request.html").\
                        replace("__EMAIL__", email).\
                        replace("__USERNAME__", username)
            toaddr = email
            message = mail.add_message_headers(body, toaddr)
            mail.send_email_infinite(server, toaddr, message)
            sys.exit()
        else:
            sys.exit()

    # Check duplicated username or project name
    if args.no_last_name == False:
        unappended_project_name = first_name.title() + " " + last_name.title()
        unappended_username = first_name.lower() + "." + last_name.lower()
    else:
        unappended_project_name = first_name.title()
        unappended_username = first_name.lower()
    project_name = unappended_project_name + "'s project"
    username = unappended_username
    if openstack.username_exists(username) or\
       openstack.project_exists(project_name.replace("'", "\\'")):
        i = 2
        project_name = unappended_project_name + `i` + "'s project"
        username = unappended_username + `i`
        while openstack.username_exists(username) or\
              openstack.project_exists(project_name.replace("'", "\\'")):
            i = i + 1
            project_name = unappended_project_name + `i` + "'s project"
            username = unappended_username + `i`

    password = random_password()

    print "Username:      " + username
    print "Password:      " + password
    print "Project:       " + project_name
    if email != '':
        print "Email:         " + email
    else:
        print "Warning: No email provided. Only use this option for accounts "\
              "used by our own team"
    if not confirmation():
        sys.exit()
    else:
        print

    try:
        print "Creating project..."
        project_id = openstack.create_project(project_name)
    except:
        print "Error creating project."
        sys.exit()

    try:
        print "Creating user..."
        user_id = openstack.create_user(username, email, password)
    except:
        print "Error creating user. Rolling back..."
        openstack.delete_project(project_id)
        sys.exit()

    try:
        openstack.set_quotas(project_id)
    except:
        print "Error setting quotas. Rolling back..."
        openstack.delete_user(user_id)
        openstack.delete_project(project_id)
        sys.exit()

    try:
        print "Adding role to user..."
        openstack.add_role_to_user(project_id, user_id)
    except:
        print "Error adding role to user. Rolling back..."
        openstack.delete_user(user_id)
        openstack.delete_project(project_id)
        sys.exit()

    try:
        print "Creating network..."
        network_id = openstack.create_network(project_id, "Intranet")
    except:
        print "Error creating network. Rolling back..."
        openstack.delete_user(user_id)
        openstack.delete_project(project_id)
        sys.exit()

    try:
        print "Creating subnet..."
        subnet_id = openstack.create_subnet(project_id, network_id, "Subnet",
                                            "9.9.9.9")
    except:
        print "Error creating subnet. Rolling back..."
        openstack.delete_networks([network_id])
        openstack.delete_user(user_id)
        openstack.delete_project(project_id)
        sys.exit()

    try:
        print "Creating router..."
        router_id = openstack.create_router(project_id, "Router")
    except:
        print "Error creating router. Rolling back..."
        openstack.delete_subnets([subnet_id])
        openstack.delete_networks([network_id])
        openstack.delete_user(user_id)
        openstack.delete_project(project_id)
        sys.exit()

    try:
        print "Adding interface to router..."
        openstack.add_router_interface(router_id, subnet_id)
    except:
        print "Error adding router interface. Rolling back..."
        openstack.delete_routers([router_id])
        openstack.delete_subnets([subnet_id])
        openstack.delete_networks([network_id])
        openstack.delete_user(user_id)
        openstack.delete_project(project_id)
        sys.exit()

    try:
        print "Setting router gateway..."
        openstack.set_router_gateway(router_id,
                                     "2f487de7-1695-475d-8345-4e6e681f699a")
    except:
        print "Error setting router gateway. Rolling back..."
        openstack.delete_routers([router_id])
        openstack.delete_subnets([subnet_id])
        openstack.delete_networks([network_id])
        openstack.delete_user(user_id)
        openstack.delete_project(project_id)
        sys.exit()

    security_group_id = openstack.get_security_groups(project_id)[0]
    try:
        print "Adding security group rules..."
        openstack.add_icmp_rule(project_id, security_group_id)
        openstack.add_ssh_rule(project_id, security_group_id)
    except:
        print "Error adding security group rules. Rolling back..."
        openstack.delete_routers([router_id])
        openstack.delete_subnets([subnet_id])
        openstack.delete_networks([network_id])
        openstack.delete_user(user_id)
        openstack.delete_project(project_id)
        sys.exit()

    # If the user has no email, the email will still be sent to no one, so the
    # user creation is registered in our outbox.
    if email != '':
        print
        print "Sending credentials to the user..."
    try:
        server = mail.login_smtp()
        body = mail.get_message_body("./request.html").\
                    replace("__USERNAME__", username).\
                    replace("__PASSWORD__", password)
        toaddr = email
        message = mail.add_message_headers(body, toaddr)
        mail.send_email_infinite(server, toaddr, message)
    except:
        print "Error sending email. Please send the credentials manually to "\
              "the user"
        sys.exit()
