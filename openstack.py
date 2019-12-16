# -*- coding: utf-8 -*-

import sys
import subprocess
import MySQLdb
import time
import re
import json
import datetime
import os

db_host = "localhost"
db_username = "root"
db_password = os.environ['DB_PASSWORD']

################################### Projects ###################################

def get_projects(user_id):
    db = MySQLdb.connect(db_host, db_username, db_password, "keystone")
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT target_id FROM assignment WHERE "\
                   "actor_id='" + user_id + "' AND type='UserProject'")
    results = cursor.fetchall()
    return [row[0] for row in results]

def get_default_project(user_id):
    db = MySQLdb.connect(db_host, db_username, db_password, "keystone")
    cursor = db.cursor()
    cursor.execute("SELECT default_project_id FROM user WHERE id='" +\
                   user_id + "'")
    results = cursor.fetchall()
    return results[0][0]

def get_project_name(project_id):
    db = MySQLdb.connect(db_host, db_username, db_password, "keystone")
    cursor = db.cursor()
    cursor.execute("SELECT name FROM project WHERE id='" + project_id + "'")
    results = cursor.fetchall()
    if len(results) > 0:
        return results[0][0]
    else:
        print "Error: Project not found."
        sys.exit()

def single_user_project(project_id):
    db = MySQLdb.connect(db_host, db_username, db_password, "keystone")
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT actor_id FROM assignment WHERE "\
                   "target_id='" + project_id + "'")
    results = cursor.fetchall()
    if(len(results) > 1):
        return False
    else:
        return True

def delete_project(project_id):
    print "Deleting project: " + `project_id`
    subprocess.check_output(("openstack project delete " + project_id).split())

def project_exists(project_name):
    db = MySQLdb.connect(db_host, db_username, db_password, "keystone")
    cursor = db.cursor()
    cursor.execute("SELECT id FROM project WHERE name='" + project_name + "'")
    results = cursor.fetchall()
    if len(results) == 0:
        return False
    else:
        return True

def create_project(name):
    project = subprocess.check_output(['openstack', 'project', 'create',
                                       '--domain', 'default', name])
    match = re.search("^\\| id +\\| ([a-z0-9]+) +\\|", project, re.MULTILINE)
    return match.group(1)

# Projects without any user assigned to it
def get_ownerless_projects():
    db = MySQLdb.connect(db_host, db_username, db_password, "keystone")
    cursor = db.cursor()
    cursor.execute("SELECT id FROM project WHERE id NOT IN (SELECT target_id "\
                   "FROM keystone.assignment)")
    results = cursor.fetchall()
    return [row[0] for row in results]

#################################### Users ####################################

def get_username(user_id):
    db = MySQLdb.connect(db_host, db_username, db_password, "keystone")
    cursor = db.cursor()
    cursor.execute("SELECT name FROM user WHERE id='" + user_id + "'")
    results = cursor.fetchall()
    if len(results) > 0:
        return results[0][0]
    else:
        print "Error: User not found."
        sys.exit()

def delete_user(user_id):
    print "Deleting user: " + `user_id`
    subprocess.check_output(("openstack user delete " + user_id).split())


def enable_user(user_id):
    print "Enabling user: " + `user_id`
    subprocess.check_output(("openstack user set --enable " + user_id).split())

def disable_user(user_id):
    print "Disabling user: " + `user_id`
    subprocess.check_output(("openstack user set --disable " + user_id).split())

def is_valid_user_id(user_id):
    id_regex = re.compile("^[a-f0-9]{32}$")
    if id_regex.search(user_id) == None:
        return False
    else:
        db = MySQLdb.connect(db_host, db_username, db_password, "keystone")
        cursor = db.cursor()
        cursor.execute("SELECT * FROM user WHERE id='" + user_id + "'")
        results = cursor.fetchall()
        if len(results) == 0:
            return False
    return True

def get_username_from_email(email):
    db = MySQLdb.connect(db_host, db_username, db_password, "keystone")
    cursor = db.cursor()
    cursor.execute("SELECT name FROM user WHERE extra LIKE '%\"email\": \"" +\
                   email + "\"%'")
    results = cursor.fetchall()
    return results[0][0]

def username_exists(username):
    db = MySQLdb.connect(db_host, db_username, db_password, "keystone")
    cursor = db.cursor()
    cursor.execute("SELECT id FROM user WHERE name='" + username + "'")
    results = cursor.fetchall()
    if len(results) == 0:
        return False
    else:
        return True

def create_user(name, email, password):
    user = subprocess.check_output(['openstack', 'user', 'create', '--domain',
                                    'default', '--email', email,'--password',
                                    password, name])
    match = re.search("^\\| id +\\| ([a-z0-9]+) +\\|", user, re.MULTILINE)
    return match.group(1)

def add_role_to_user(project, user):
    subprocess.check_output(['openstack', 'role', 'add', '--project', project,
                             '--user', user, 'user'])
    subprocess.check_output(['openstack', 'user', 'set', '--project', project,
                             user])

# Users not assigned to any project
def get_ownerless_users():
    db = MySQLdb.connect(db_host, db_username, db_password, "keystone")
    cursor = db.cursor()
    cursor.execute("SELECT id FROM user WHERE id NOT IN (SELECT actor_id FROM "\
                   "keystone.assignment)")
    results = cursor.fetchall()
    return [row[0] for row in results]

################################### Networks ###################################

def get_networks(project_id):
    db = MySQLdb.connect(db_host, db_username, db_password, "neutron")
    cursor = db.cursor()
    cursor.execute("SELECT id FROM networks WHERE tenant_id='" +\
                   project_id + "'")
    results = cursor.fetchall()
    return [row[0] for row in results]

def delete_networks(networks):
    print "Deleting networks: " + `networks`
    for i in range(0, len(networks)):
        subprocess.check_output(("neutron net-delete " + networks[i]).split())

def enable_networks(networks):
    print "Enabling networks: " + `networks`
    for i in range(0, len(networks)):
        subprocess.check_output(("openstack network set --enable " +\
                                 networks[i]).split())

def disable_networks(networks):
    print "Disabling networks: " + `networks`
    for i in range(0, len(networks)):
        subprocess.check_output(("openstack network set --disable " +\
                                 networks[i]).split())

def create_network(project_id, name):
    network = subprocess.check_output(['neutron', 'net-create', '--tenant-id',
                                       project_id, name])
    match = re.search("^\\| id +\\| ([a-z0-9-]+) +\\|", network, re.MULTILINE)
    return match.group(1)

def get_ownerless_networks():
    db = MySQLdb.connect(db_host, db_username, db_password, "neutron")
    cursor = db.cursor()
    cursor.execute("SELECT id FROM networks WHERE tenant_id NOT IN (SELECT id "\
                   "FROM keystone.project)")
    results = cursor.fetchall()
    return [row[0] for row in results]

################################### Subnets ###################################

def get_subnets(project_id):
    db = MySQLdb.connect(db_host, db_username, db_password, "neutron")
    cursor = db.cursor()
    cursor.execute("SELECT id FROM subnets WHERE tenant_id='" +\
                   project_id + "'")
    results = cursor.fetchall()
    return [row[0] for row in results]

def delete_subnets(subnets):
    print "Deleting subnets: " + `subnets`
    for i in range(0, len(subnets)):
        subprocess.check_output(("neutron subnet-delete " + subnets[i]).split())

def create_subnet(project_id, network_id, name, dns):
    subnet = subprocess.check_output(['neutron', 'subnet-create', '--tenant-id',
                                      project_id, '--name', name,
                                      '--dns-nameserver', dns, '--gateway',
                                      '192.168.1.1', network_id,
                                      '192.168.1.0/24'])
    match = re.search("^\\| id +\\| ([a-z0-9-]+) +\\|", subnet, re.MULTILINE)
    return match.group(1)

def get_ownerless_subnets():
    db = MySQLdb.connect(db_host, db_username, db_password, "neutron")
    cursor = db.cursor()
    cursor.execute("SELECT id FROM subnets WHERE tenant_id NOT IN (SELECT id "\
                   "FROM keystone.project)")
    results = cursor.fetchall()
    return [row[0] for row in results]

################################### Routers ###################################

def get_routers(project_id):
    db = MySQLdb.connect(db_host, db_username, db_password, "neutron")
    cursor = db.cursor()
    cursor.execute("SELECT id FROM routers WHERE tenant_id='" +\
                   project_id + "'")
    results = cursor.fetchall()
    return [row[0] for row in results]

def get_router_subnets(router_id):
    db = MySQLdb.connect(db_host, db_username, db_password, "neutron")
    cursor = db.cursor()

    cursor.execute("SELECT port_id FROM routerports WHERE router_id='" +\
                   router_id + "' AND port_type='network:router_interface'")
    results = cursor.fetchall()

    port_id = [row[0] for row in results]

    subnets = []
    for i in range(0, len(port_id)):
        cursor.execute("SELECT subnet_id FROM ipallocations WHERE port_id='" +\
                       port_id[i] + "'")
        results = cursor.fetchall()
        subnets.append(results[0][0])

    return subnets

def delete_routers(routers):
    for i in range(0, len(routers)):
        router_subnets = get_router_subnets(routers[i])
        print "Deleting router interfaces: " + `router_subnets`
        for j in range(0, len(router_subnets)):
            subprocess.check_output(("neutron router-interface-delete " +\
                                     routers[i] + " " +\
                                     router_subnets[j]).split())

        print "Deleting routers: " + `routers`
        subprocess.check_output(("neutron router-delete " + routers[i]).split())

def create_router(project_id, name):
    router = subprocess.check_output(['neutron', 'router-create',
                                      '--tenant-id', project_id, name])
    match = re.search("^\\| id +\\| ([a-z0-9-]+) +\\|", router, re.MULTILINE)
    return match.group(1)

def add_router_interface(router_id, subnet_id):
    subprocess.check_output(("neutron router-interface-add " + router_id +\
                             " " + subnet_id).split())

def set_router_gateway(router_id, external_network_id):
    subprocess.check_output(("neutron router-gateway-set " + router_id +\
                             " " + external_network_id).split())

def enable_routers(routers):
    print "Enabling routers: " + `routers`
    for i in range(0, len(routers)):
        subprocess.check_output(("neutron router-update --admin-state-up "\
                                 "True " + routers[i]).split())

def disable_routers(routers):
    print "Disabling routers: " + `routers`
    for i in range(0, len(routers)):
        subprocess.check_output(("neutron router-update --admin-state-up "\
                                 "False " + routers[i]).split())

def get_ownerless_routers():
    db = MySQLdb.connect(db_host, db_username, db_password, "neutron")
    cursor = db.cursor()
    cursor.execute("SELECT id FROM routers WHERE tenant_id NOT IN (SELECT id "\
                   "FROM keystone.project)")
    results = cursor.fetchall()
    return [row[0] for row in results]

################################# Floating IPs #################################

def get_floating_ips(project_id):
    db = MySQLdb.connect(db_host, db_username, db_password, "neutron")
    cursor = db.cursor()
    cursor.execute("SELECT id FROM floatingips WHERE tenant_id='" +\
                   project_id + "'")
    results = cursor.fetchall()
    return [row[0] for row in results]

def delete_floating_ips(floating_ips):
    print "Deleting floating ips: " + `floating_ips`
    for i in range(0, len(floating_ips)):
        subprocess.check_output(("neutron floatingip-delete " +\
                                 floating_ips[i]).split())

def get_ownerless_floating_ips():
    db = MySQLdb.connect(db_host, db_username, db_password, "neutron")
    cursor = db.cursor()
    cursor.execute("SELECT id FROM floatingips WHERE tenant_id NOT IN (SELECT "\
                   "id FROM keystone.project)")
    results = cursor.fetchall()
    return [row[0] for row in results]

################################## Instances ##################################

def get_instances(project_id):
    db = MySQLdb.connect(db_host, db_username, db_password, "nova")
    cursor = db.cursor()
    cursor.execute("SELECT uuid FROM instances WHERE deleted='0' AND "\
                   "project_id='" + project_id + "'")
    results = cursor.fetchall()
    return [row[0] for row in results]

def get_instances_by_name(project_id):
    db = MySQLdb.connect(db_host, db_username, db_password, "nova")
    cursor = db.cursor()
    cursor.execute("SELECT display_name FROM instances WHERE deleted='0' AND "\
                   "project_id='" + project_id + "'")
    results = cursor.fetchall()
    return [row[0] for row in results]

def delete_instances(instances):
    print "Deleting instances: " + `instances`
    for i in range(0, len(instances)):
        subprocess.check_output(("nova delete " + instances[i]).split())

        # Waits for instance to be actually deleted
        while True:
            db = MySQLdb.connect(db_host, db_username, db_password, "nova")
            cursor = db.cursor()
            cursor.execute("SELECT * FROM instances WHERE deleted='0' AND "\
                           "uuid='" + instances[i] + "'")
            results = cursor.fetchall()
            if len(results) == 0:
                break
            time.sleep(0.1)

def get_ownerless_instances():
    db = MySQLdb.connect(db_host, db_username, db_password, "nova")
    cursor = db.cursor()
    cursor.execute("SELECT uuid FROM instances WHERE deleted='0' and "\
                   "project_id NOT IN (SELECT id FROM keystone.project)")
    results = cursor.fetchall()
    return [row[0] for row in results]

################################## Snapshots ##################################

def get_snapshots(project_id):
    db = MySQLdb.connect(db_host, db_username, db_password, "glance")
    cursor = db.cursor()
    cursor.execute("SELECT id FROM images WHERE deleted='0' AND owner='" +\
                   project_id + "'")
    results = cursor.fetchall()
    return [row[0] for row in results]

def delete_snapshots(snapshots):
    print "Deleting snapshots: " + `snapshots`
    for i in range(0, len(snapshots)):
        subprocess.check_output(("glance image-delete " + snapshots[i]).split())

def get_ownerless_snapshots():
    db = MySQLdb.connect(db_host, db_username, db_password, "glance")
    cursor = db.cursor()
    cursor.execute("SELECT id FROM images WHERE deleted='0' and owner NOT IN "\
                   "(SELECT id FROM keystone.project)")
    results = cursor.fetchall()
    return [row[0] for row in results]

############################### Security Groups ###############################

def get_security_groups(project_id):
    db = MySQLdb.connect(db_host, db_username, db_password, "neutron")
    cursor = db.cursor()
    cursor.execute("SELECT id FROM securitygroups WHERE tenant_id='" +\
                   project_id + "'")
    results = cursor.fetchall()
    return [row[0] for row in results]

def delete_security_groups(security_groups):
    print "Deleting security groups: " + `security_groups`
    for i in range(0, len(security_groups)):
        try:
            subprocess.check_output(("neutron security-group-delete " +\
                                     security_groups[i]).split())
        except:
            time.sleep(5)
            subprocess.check_output(("neutron security-group-delete " +\
                                     security_groups[i]).split())

def add_icmp_rule(project_id, security_group_id):
    subprocess.check_output(("neutron security-group-rule-create "\
                             "--tenant-id " + project_id + " --direction "\
                             "ingress --protocol icmp --remote-ip-prefix "\
                             "0.0.0.0/0 " + security_group_id).split())

def add_ssh_rule(project_id, security_group_id):
    subprocess.check_output(("neutron security-group-rule-create "\
                             "--tenant-id " + project_id + " --direction "\
                             "ingress --protocol tcp --port-range-min 22 "\
                             "--port-range-max 22 --remote-ip-prefix "\
                             "0.0.0.0/0 " + security_group_id).split())

#################################### Emails ####################################

def all_emails():
    db = MySQLdb.connect(db_host, db_username, db_password, "keystone")
    cursor = db.cursor()
    cursor.execute("SELECT extra FROM user")
    results = cursor.fetchall()

    emails = []

    for i in range(0, len(results)):
        try:
            emails.append(json.loads(results[i][0])["email"])
        except:
            pass

    return emails

def active_users_emails():
    db = MySQLdb.connect(db_host, db_username, db_password)
    cursor = db.cursor()
    cursor.execute("SELECT extra FROM keystone.user INNER JOIN nova.instances "\
                   "ON keystone.user.id = nova.instances.user_id AND "\
                   "nova.instances.deleted='0' GROUP BY nova.instances.user_id")
    results = cursor.fetchall()

    emails = []

    for i in range(0, len(results)):
        try:
            emails.append(json.loads(results[i][0])["email"])
        except:
            pass

    return emails

def email_exists(email):
    db = MySQLdb.connect(db_host, db_username, db_password, "keystone")
    cursor = db.cursor()
    cursor.execute("SELECT extra FROM user WHERE extra LIKE '%\"email\": \"" +\
                   email + "\"%'")
    results = cursor.fetchall()
    if len(results) == 0:
        return False
    else:
        return True

#################################### Quotas ####################################

def set_quotas(project_id, VCPUs = 4, instances = 4, RAM = 4096,
               security_groups = 10, security_group_rules = 100,
               floating_ips = 4, networks = 10, routers = 10, ports = 20,
               subnets = 10, key_pairs = 10):
    openstack_quotas = ("openstack quota set"\
    " --ram " + `RAM` +\
    " --secgroup-rules " + `security_group_rules` +\
    " --instances " + `instances` +\
    " --key-pairs " + `key_pairs` +\
    " --secgroups " + `security_groups` +\
    " --floating-ips " + `floating_ips` +\
    " --cores " + `VCPUs` +\
    " " + project_id).split()

    subprocess.check_output(openstack_quotas)

    nova_quotas = ("nova quota-update"\
    " --instances " + `instances` +\
    " --cores " + `VCPUs` +\
    " --ram " + `RAM` +\
    " --floating-ips " + `floating_ips` +\
    " --key-pairs " + `key_pairs` +\
    " --security-groups " + `security_groups` +\
    " --security-group-rules " + `security_group_rules` +\
    " " + project_id).split()

    subprocess.check_output(nova_quotas)

    neutron_quotas = ("neutron quota-update"\
    " --network " + `networks` +\
    " --subnet " + `subnets` +\
    " --port " + `ports` +\
    " --router " + `routers` +\
    " --floatingip " + `floating_ips` +\
    " --security-group " + `security_groups` +\
    " --security-group-rule " + `security_group_rules` +\
    " --tenant-id " + project_id).split()

    subprocess.check_output(neutron_quotas)

#################################### Others ####################################

def delete_content(project_id):
    delete_snapshots(get_snapshots(project_id))
    delete_instances(get_instances(project_id))
    delete_floating_ips(get_floating_ips(project_id))
    delete_security_groups(get_security_groups(project_id))
    delete_routers(get_routers(project_id))
    delete_subnets(get_subnets(project_id))
    delete_networks(get_networks(project_id))

def delete_ownerless_content():
    projects = get_ownerless_projects()
    for p in projects:
        delete_project(p)
    users = get_ownerless_users()
    for u in users:
        delete_user(u)
    delete_snapshots(get_ownerless_snapshots())
    delete_instances(get_ownerless_instances())
    delete_floating_ips(get_ownerless_floating_ips())
    delete_routers(get_ownerless_routers())
    delete_subnets(get_ownerless_subnets())
    delete_networks(get_ownerless_networks())

def get_instances_older_than(days):
    timedelta = datetime.timedelta(days=days)
    limit_date = (datetime.date.today() - timedelta).strftime('%Y-%m-%d')

    db = MySQLdb.connect(db_host, db_username, db_password)
    cursor = db.cursor()
    cursor.execute("SELECT keystone.user.extra,nova.instances.uuid,"\
                   "nova.instances.display_name,nova.instances.project_id "\
                   "FROM keystone.user INNER JOIN nova.instances ON "\
                   "nova.instances.user_id=keystone.user.id AND "\
                   "nova.instances.deleted='0' AND "\
                   "nova.instances.created_at<'" + limit_date + "'")
    results = cursor.fetchall()

    results = list(results)
    i = 0
    while i < len(results):
        results[i] = list(results[i])
        try:
            results[i][0] = json.loads(results[i][0])["email"]
        except:
            results.pop(i)
        else:
            i = i + 1

    return results
