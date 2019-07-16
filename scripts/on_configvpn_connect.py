#!/usr/bin/python

#
# Dieses Script wird bei jedem erfolgreichen Aufbau einer Verbindung durch den OpenVPN
# Daemon gestartet. Es dient im Grunde genommen nur dazu, ein Ansible-Playbook zu starten.
#  

import syslog
import os
import subprocess 
import shlex
import re

# OpenVPN gibt eine reihe von Environmentvariabeln mit. Davon sind interessant:
# Die IP-Addresse des sich verbindenen Client-Devices im Config-VPN. Dies wird fuer 
# fuer die Ansible-Verbindung zum Client-Device benutzt. 
remote_ip = os.environ["ifconfig_pool_remote_ip"]
# Der Common-Name im fuer die erfolgreiche Verbinung genutzten Zertifikat
common_name = os.environ["common_name"]
# Wo man schon mal im Python ist, kann man auch gleich die Client-ID rausschneiden.
client_id =  re.search("clnt(.*)dev",common_name).group(1)

# Das Ansible-Script muss hier sudo nutzen, da der OpenVPN-Server fuers Config-VPN unter 
# dem User openvpn laeuft, das Ansible-Playbook braucht aber root.
cmd="sudo -b ansible-playbook -i centctrl," + remote_ip +" /usr/local/securitydevice/ansible/playbook_onconfigvpnconnect.yaml --extra-vars=\"remote_ip="+remote_ip+" common_name="+ common_name +" client_id="+ client_id+"\" " 
args = shlex.split(cmd)
subprocess.call(args)
