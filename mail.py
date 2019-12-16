# -*- coding: utf-8 -*-

import smtplib
import sys
import re
import time
from datetime import datetime
import os

SMTP_SERVER = 'smtp.server.com:587'
SMTP_USERNAME = 'user'
SMTP_PASSWORD = os.environ['SMTP_PASSWORD']
NAME = 'Sender Name'
ADDRESS = 'user@server.com'

def login_smtp(address_and_port=SMTP_SERVER, username=SMTP_USERNAME,
               password=SMTP_PASSWORD):
    try:
        server = smtplib.SMTP(address_and_port)
        server.ehlo()
        server.starttls()
        server.login(username, password)
        return server
    except:
        print "Couldn't login"
        sys.exit()

def get_message_body(html_file):
    try:
        file = open(html_file, 'r')
        body = file.read()
        file.close()
        return body
    except:
        print "Couldn't open " + html_file + " file"
        sys.exit()

def split_recipients(recipients):
    return filter(lambda x: x != "", ";".join(recipients).replace(" ", ";").\
                                         replace("\n", ";").split(";"))

def valid_email(email):
    email_regex = re.compile("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\."\
                             "[a-zA-Z0-9-.]+$")
    if email_regex.search(email) == None:
        return False
    else:
        return True

def send_email_infinite(server, to, message, sender=ADDRESS, bcc=ADDRESS):
    if to != "" and not valid_email(to):
        print "Invalid address: " + to
        return

    recipients = [to] + [bcc]

    i = 1
    while True:
        try:
            server.sendmail(sender, recipients, message)
        # Usually the server limits the number of messages per minute. Waits
        # until it is allowed to send again.
        except:
            j = 60*i
            while j > 0:
                sys.stdout.write("\rCouldn't send email. Trying again in " +\
                                 `j` + " seconds.    ")
                sys.stdout.flush()
                try:
                    time.sleep(1)
                except:
                    print
                    sys.exit()
                j = j - 1;
            i = i + 1
            print
            continue
        else:
            if to != "":
                print "Email sent to " + to
            break

def add_message_headers(body, to_address, from_name=NAME, from_address=ADDRESS):
    headers = "From: " + from_name + " <" + from_address + ">\n"\
              "To: "+ to_address + "\n"\
              "MIME-Version: 1.0\n"\
              "Content-type: text/html\n"

    # Subject not already in the body
    if re.search("^Subject:", body[0:body.find("<html>")] , re.MULTILINE) == None:
        try:
            subject = raw_input("Subject: ")
            headers += "Subject: " + subject + "\n"
        except:
            print
            sys.exit()

    return headers + body

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