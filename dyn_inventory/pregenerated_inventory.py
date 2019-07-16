#!/usr/bin/python3.5

import os
import sys

base_inventory=open("/usr/local/securitydevice/dyn_inventory/baseinventory.txt","r")
base_inventory_content = base_inventory.read()
print(base_inventory_content)

print("[client_devices]")
openvpn_statuslog_file = open("/etc/openvpn/openvpn-status.log","r")
openvpn_statuslog_content = openvpn_statuslog_file.readlines()
for line in openvpn_statuslog_content:
	if "10.8." in line:
		if not "/24" in line:
			ip=line.split(",")[0]
			print(ip)

