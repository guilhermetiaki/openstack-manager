# OpenStack Manager

These scripts were designed and tested using OpenStack Liberty (2015).

It implements three main functionalities:

## Add User

    ./minicloud.sh add first_name last_name email_address

Creates the user per se, automatically generating its username, assigning it to a project and creating related entities to simplify the user initial setup: network, subnet, and router. It also sets the quota and adds a security group. Finally, sends the user its username and password using an HTML message template.

## Delete User

    ./minicloud.sh delete user_id

Deletes the OpenStack user per se, its project, and all related entities: snapshots, instances, floating IPs, security groups, routers, subnets, and networks.

## Disable/Enable User

    ./minicloud.sh disable user_id
    ./minicloud.sh enable user_id

Disabling a user blocks its access to its instances and the dashboard. Enabling it reverses the process.
