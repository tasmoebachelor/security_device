#!/usr/bin/python

import syslog
import os
import subprocess 
import shlex
import re

syslog.syslog('Processing started')
for param in os.environ.keys():
    syslog.syslog(param)
    syslog.syslog(os.environ[param])

remote_ip = os.environ["ifconfig_pool_remote_ip"]
common_name = os.environ["common_name"]
client_id =  re.search("clnt(.*)dev",common_name).group(1)


syslog.syslog("user id:" + str(os.getuid()) )
syslog.syslog("Remote IP:" + remote_ip )
syslog.syslog("Common Name : " + common_name )
syslog.syslog("ClientID : " + client_id )

cmd="sudo -b ansible-playbook -i centctrl," + remote_ip +" /usr/local/securitydevice/ansible/playbook_onconfigvpnconnect.yaml --extra-vars=\"remote_ip="+remote_ip+" common_name="+ common_name +" client_id="+ client_id+"\" " 
syslog.syslog("cmd :" + cmd)
args = shlex.split(cmd)
subprocess.call(args)
