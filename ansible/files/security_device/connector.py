#!/usr/bin/python3.5

import os
import paramiko
import subprocess
import shlex
import time
from pathlib import Path

# Am Anfang des Scripts werden alle OpenVPN-Prozesse terminiert
# Damit werden sämtliche VPN-Tunnel und Tunnel-Interfaces entfernt. 
os.system("killall openvpn")

# Zunächst wird ein verbliebenes Semaphore-File entfernt.
#
ansible_semaphore = Path("/usr/local/vpnconnector/ansible.semaphore")
if ansible_semaphore.is_file():
	os.remove('/usr/local/vpnconnector/ansible.semaphore') 

# Username, Hostname und Password aus dem Environment des Prozesses uebernehmen. Dadurch stehen diese Daten nicht in der Prozesstabelle.

hostname= os.environ['VPN_HOSTNAME']
port = 22
username= os.environ['VPN_USERNAME']
password= os.environ['VPN_PASSWORD']

# Mit SFTP das Configfile fuer das ConfigVPN holen"

try:
    t = paramiko.Transport((hostname, port))
    t.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(t)
    sftp.get('/home/'+username+'/configvpn.ovpn','/usr/local/vpnconnector/configfiles/configvpn.ovpn')
finally:
    t.close()


# Das VPN fuer das Config-VPN starten und warten bis das tun0 Interface oben ist.
command_config_openvpn = "openvpn --daemon --config /usr/local/vpnconnector/configfiles/configvpn.ovpn"
splitted_command_config_openvpn = shlex.split(command_config_openvpn)
subprocess.call(splitted_command_config_openvpn)
tun0_available = False
find_ip_on_tun0 = 'ip -o addr list'
splitted_find_ip_on_tun0 = shlex.split(find_ip_on_tun0)
while not tun0_available == True:
	ip_output   = subprocess.check_output(splitted_find_ip_on_tun0)
	ip_output   = ip_output.decode("ascii",errors="ignore")
	for line in ip_output.splitlines():
		if 'tun0' in line:
			if "inet " in line:
				tun0_available = True
	print("tun0 check")
	time.sleep(1)	

# Eine erfolgreiche Verbindung an das ConfigVPN startet ein Ansible-Playbook
# an dessem Ende ein Semaphorefile angelegt wird. Dies passiert nur, wenn 
# vorher alle anderen Schritte erfolgreich waren. Durch die Existenz des 
# Semaphores wissen wir, das alle Komponenten auf einen Start des Daten-VPN
# vorbereitet sind. Das Script wartet endlos auf das Erscheinen des Semaphore. 

ansible_semaphore = Path("/usr/local/vpnconnector/ansible.semaphore")
while not ansible_semaphore.is_file():
    print("check semaphore")
    time.sleep(1)

# Das DatenVPN wird mit dem von Ansible auf den Host, auf dem auch dieses
# Script gestartet worden ist, geschobenen unified configuration file 
# für das DatenVPN gestartet.

command_data_openvpn = "openvpn --daemon  --config /usr/local/vpnconnector/configfiles/datavpn.ovpn"
splitted_command_data_openvpn = shlex.split(command_data_openvpn)
subprocess.call(splitted_command_data_openvpn)

