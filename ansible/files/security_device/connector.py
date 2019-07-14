#!/usr/bin/python3.5

import os
import paramiko
import subprocess
import shlex
import time
from pathlib import Path

# Cleanup: Alle OpenVPN Prozesse terminieren 
os.system("killall openvpn")

# Cleanup: Das Semaphore-File wegraeumen, wenn es aelter ist als 24h 

os.remove('/usr/local/vpnconnector/ansible.semaphore') 
print("remove stale ansible semaphore")

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
    sftp.get('/home/cda2/configvpn.ovpn','/usr/local/vpnconnector/configfiles/configvpn.ovpn')
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

ansible_semaphore = Path("/usr/local/vpnconnector/ansible.semaphore")

while not ansible_semaphore.is_file():
    print("check semaphore")
    time.sleep(1)

command_data_openvpn = "openvpn --daemon  --config /usr/local/vpnconnector/configfiles/datavpn.ovpn"
splitted_command_data_openvpn = shlex.split(command_data_openvpn)
subprocess.call(splitted_command_data_openvpn)

