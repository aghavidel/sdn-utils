"""
This file creates the necessary controller hierarchy provided with a
Controll Hierarchy Discription file, provided by the user or the orchestrator.

The structure of a CHD is like the following:
{
	nodes : [
		...
		{
			"name" : <STRING>,
			"ip" : <STRING>,
			"restconf_port" : <INT>,
			"netconf_port" : <INT>,
			"role" : <STRING>, either "MASTER", or "SLAVE",
			"restconf_password" : <STRING>,
			"restconf_username" : <STRING>
		},
		...
	]
}

After the file is processed, the MASTER mounts a NETCONF manager on every
SLAVE and begins the network configuration.
"""

import requests
import os
import shutil
import sys
import xml.etree.ElementTree as ET
import json
from requests.exceptions import (
		Timeout,
		RequestException
	)

from constants import (
		MASTER_NETCONF_CONNECTOR,
		NETCONF_SERVER,
		NETCONF_SERVER_NAMESPACE,
		NETCONF_NODE_TOPOLOGY_NAMESPACE,
		NETCONF_KEEPALIVE,
		TIMEOUT
	)

def checkMdsalNetconfServer(
	ip, restconf_port, password, username, netconf_port):
	"""
	Check if the desiered conntroller has an available NETCONF server.
	"""

	url = NETCONF_SERVER.format(
			ip,
			restconf_port
		)

	headers = {
		"Accept" : "application/json"
	}

	auth = (
		username,
		password
	)

	try:
		response = requests.get(
				auth=auth,
				headers=headers,
				url=url,
				timeout=TIMEOUT
			)

		st = response.status_code
		print('response : HTTP ' + str(st))

		if st == 200 or st == 201:
			if response.json():
				print("Controller netconf server listenning on {}:{}".format(
						ip,
						netconf_port
					))
			else:
				print("NETCONF API on {}:{} is not yet active, check the connection or\
					 check if feature:odl-netconf-mdsal is installed.".format(
					 	ip,
					 	netconf_port
					 ))
		elif st == 401:
			print("Unauthorzied on {}:{}, check username and password.".format(
					ip,
					restconf_port
				))

	except Timeout:
		print("Timeout error on {}:{}, controller is busy ...".format(
				ip,
				restconf_port
			))

	except RequestException:
		print("Connectioin refused on {}:{}, controller is either dead or not active or the URL is inavalid...".format(
				ip,
				restconf_port
			))
		print("If nither, check if feature:odl-restconf-all is installed.")

def netconfMasterSlaveXml(
	master_ip, master_restconf_port, master_username, master_password,
	slave_name, slave_ip, slave_netconf_port, slave_username, slave_password):
	"""
	Create a single Master-Slave NETCONF connection config file.
	First an xml tree is created that tells the MASTER controller
	to create a NETCONF device on itself to connect to the SLAVE.

	The NETCONF device has the same name as the controller name in CHD.json 
	and tries to connect to the SLAVE's NETCONF server, if checkMdsalNetconfServer()
	returns true for every controller, then only TimeoutError can cause exceptions.

	All xml files are stored in 'netconf_server_xmls' and are sent in by another function.
	"""

	node = ET.Element("node", xmlns=NETCONF_SERVER_NAMESPACE)
	ET.SubElement(node, "node-id").text = slave_name
	ET.SubElement(node, "host", xmlns=NETCONF_NODE_TOPOLOGY_NAMESPACE).text = slave_ip
	ET.SubElement(node, "port", xmlns=NETCONF_NODE_TOPOLOGY_NAMESPACE).text = str(slave_netconf_port)
	ET.SubElement(node, "username", xmlns=NETCONF_NODE_TOPOLOGY_NAMESPACE).text = slave_username
	ET.SubElement(node, "password", xmlns=NETCONF_NODE_TOPOLOGY_NAMESPACE).text = slave_password
	ET.SubElement(node, "tcp-only", xmlns=NETCONF_NODE_TOPOLOGY_NAMESPACE).text = "false"
	ET.SubElement(node, "keepalive-delay", xmlns=NETCONF_NODE_TOPOLOGY_NAMESPACE).text = str(NETCONF_KEEPALIVE)

	xml = ET.tostring(node).decode('utf-8')
	file_name = slave_name

	if os.path.isdir('./netconf_server_xmls'):
		shutil.rmtree('./netconf_server_xmls')
		os.mkdir('netconf_server_xmls')
		file = open('./netconf_server_xmls/' + file_name, "w")
		file.write(xml)
	else:
		os.mkdir('netconf_server_xmls')
		file = open('./netconf_server_xmls/' + file_name, "w")
		file.write(xml)
	file.close()

def sendNetconfConnectionRequest(
	master_ip, master_restconf_port, master_username, master_password, config, slave_name):
	"""
	Send a single NETCONF xml configuration to the MASTER.
	"""

	url = MASTER_NETCONF_CONNECTOR.format(master_ip, master_restconf_port, slave_name)

	headers = {
		"Content-Type": "application/xml",
		"Accept": "application/xml"
	}

	auth = (
		master_username,
		master_password
	)

	data = config

	try:
		response = requests.put(
				url=url,
				data=data,
				headers=headers,
				auth=auth,
				timeout=TIMEOUT
			)

		st = response.status_code

		if st == 200 or st == 201:
			print("Pushed config for {} to MASTER.".format(slave_name))
		elif st == 401:
			print("Unauthorzied on {}:{}, check username and password.".format(
					master_ip,
					master_restconf_port
				))

	except Timeout:
		print("Timeout error on {}:{}, controller is busy ...".format(
				master_ip,
				master_restconf_port
			))

def createMasterSlaveNetconfService():
	"""
	Create a NETCONF device on the MASTER for every single SLAVE
	under it's control.
	"""
	print("*"*10 + " Reading CHD " + "*"*10)

	if os.path.isfile('./chd.json'):
		with open('./chd.json', "r") as chd:
			j = json.laod(chd)
			nodes = j["nodes"]

			slaves = []

			for node in nodes:
				if node["role"] == "MASTER":
					master = node
				else:
					slaves.append(node)
	else:
		print("No Controller Hierarchy Descriptor file was found, aborting ...")
		sys.exit()

	print("*"*10 + " Creating config files " + "*"*10)

	for slave in slaves:
		netconfMasterSlaveXml(
			master_ip=master["ip"], master_restconf_port=master["restconf_port"], 
			master_username=master["master_username"], master_password=master["master_password"],
			slave_name=slave["name"], slave_ip=slave["ip"], slave_netconf_port=slave["netconf_port"],
			slave_username=salve["username"], slave_password=slave["password"]
		)

	print("*"*10 + " Sending config files " + "*"*10)

	for file_name in os.listdir('./netconf_server_xmls'):
		file = open(file_name, "r")
		config = file.read()

		sendNetconfConnectionRequest(
			master_ip=master["ip"], master_restconf_port=master["restconf_port"],
			master_password=master["password"], master_username=master["username"],
			config=config, slave_name=file_name)

	print("*"*10 + " All files sent " + "*"*10)