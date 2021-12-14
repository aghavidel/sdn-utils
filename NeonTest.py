import requests
import xml.etree.ElementTree as ET
import lxml.etree
import os
import sys
import json
from constants import (
		TABLE_INVENTORY,
		FLOW_INVENTORY, 
		XMLNS,
		TIMEOUT,
		MAX_NUMBER_OF_TABLES
	)
from grabTopology import *

file_list = {}
flow_id_list = {}

def ARPFlow(node_num, table, id, priority=0):
	flow = ET.Element("flow", xmlns=XMLNS)
	ET.SubElement(flow, "id").text = str(id)
	ET.SubElement(flow, "table_id").text = str(table)
	ET.SubElement(flow, "priority").text = str(priority)

	match = ET.SubElement(flow, "match")
	# ET.SubElement(match, "ipv4-destination").text = str(nw_dst)
	# ET.SubElement(match, "in-port").text = str(in_port)
	
	ethernet_match = ET.SubElement(match, "ethernet-match")
	ethernet_type = ET.SubElement(ethernet_match, "ethernet-type")
	ET.SubElement(ethernet_type, "type").text = str(int(0x806))

	instructions = ET.SubElement(flow, "instructions")
	instruction = ET.SubElement(instructions, "instruction")
	apply_actions = ET.SubElement(instruction, "apply-actions")
	ET.SubElement(instruction, "order").text = "0"

	action = ET.SubElement(apply_actions, "action")
	ET.SubElement(action, "order").text = "0"
	# ET.SubElement(action, "dec-nw-ttl")

	output_action = ET.SubElement(action, "output-action")
	# ET.SubElement(output_action, "output-node-connector").text = str(out_port)
	ET.SubElement(output_action, "output-node-connector").text = "FLOOD"
	ET.SubElement(output_action, "max-length").text = str(65535)

	# xml = str(ET.tostring(flow))
	xml = ET.tostring(flow).decode('utf-8')
	file_name = "{}_{}_{}.xml".format(node_num, table, id)

	if os.path.isdir('./flows'):
		file = open('./flows/' + file_name, "w")
		file.write(xml)
	else:
		os.mkdir('flows')
		file = open('./flows/' + file_name, "w")
		file.write(xml)
	file.close()

	file_list[file_name] = "undone"
	switch_name = "openflow:" + str(node_num)
	updateID(
		switch_name=switch_name,
		table_id=table
		)

def IPv4ForwardingFlow(node_num, in_port, out_port, table, id, nw_dst, dl_dst, priority=0):
	flow = ET.Element("flow", xmlns=XMLNS)
	ET.SubElement(flow, "id").text = str(id)
	ET.SubElement(flow, "table_id").text = str(table)
	ET.SubElement(flow, "priority").text = str(priority)

	match = ET.SubElement(flow, "match")
	ET.SubElement(match, "ipv4-destination").text = str(nw_dst)
	ET.SubElement(match, "in-port").text = str(in_port)

	ethernet_match = ET.SubElement(match, "ethernet-match")
	ethernet_type = ET.SubElement(ethernet_match, "ethernet-type")
	ET.SubElement(ethernet_type, "type").text = str(int(0x800))

	ethernet_destination = ET.SubElement(ethernet_match, "ethernet-destination")
	ET.SubElement(ethernet_destination, "address").text = str(dl_dst)

	instructions = ET.SubElement(flow, "instructions")
	instruction = ET.SubElement(instructions, "instruction")
	apply_actions = ET.SubElement(instruction, "apply-actions")
	ET.SubElement(instruction, "order").text = "0"

	action = ET.SubElement(apply_actions, "action")
	ET.SubElement(action, "order").text = "0"
	# ET.SubElement(action, "dec-nw-ttl")
	# ET.SubElement(action, "dl_dst").text = str(dl_dst)

	output_action = ET.SubElement(action, "output-action")
	ET.SubElement(output_action, "output-node-connector").text = str(out_port)
	ET.SubElement(output_action, "max-length").text = str(65535)

	# xml = str(ET.tostring(flow))
	xml = ET.tostring(flow).decode('utf-8')
	file_name = "{}_{}_{}.xml".format(node_num, table, id)

	if os.path.isdir('./flows'):
		file = open('./flows/' + file_name, "w")
		file.write(xml)
	else:
		os.mkdir('flows')
		file = open('./flows/' + file_name, "w")
		file.write(xml)
	file.close()

	file_list[file_name] = "undone"
	switch_name = "openflow:" + str(node_num)

	updateID(
		switch_name=switch_name,
		table_id=table
		)

# def MPLSFlow()

def TableMissFlow(node_num):
	flow = ET.Element("flow", xmlns=XMLNS)
	ET.SubElement(flow, "id").text = "0"
	ET.SubElement(flow, "table_id").text = "0"
	ET.SubElement(flow, "priority").text = "0"

	match = ET.SubElement(flow, "match")

	instructions = ET.SubElement(flow, "instructions")
	instruction = ET.SubElement(instructions, "instruction")
	apply_actions = ET.SubElement(instruction, "apply-actions")
	ET.SubElement(instruction, "order").text = "0"

	action = ET.SubElement(apply_actions, "action")
	ET.SubElement(action, "order").text = "0"

	output_action = ET.SubElement(action, "output-action")
	ET.SubElement(output_action, "max-length").text = "65535"
	ET.SubElement(output_action, "output-node-connector").text = "CONTROLLER"

	# xml = str(ET.tostring(flow))
	xml = ET.tostring(flow).decode('utf-8')
	file_name = "{}_0_0.xml".format(node_num)

	if os.path.isdir('./flows'):
		file = open('./flows/' + file_name, "w")
		file.write(xml)
	else:
		os.mkdir('flows')
		file = open('./flows/' + file_name, "w")
		file.write(xml)
	file.close()

	file_list[file_name] = "undone"



def check():
	# tree = lxml.etree.parse("./flows/10_0_0.xml")
	# print(lxml.etree.tostring(tree, pretty_print=True))
	ls = os.listdir('./flows')

	for file in ls:
		tree = lxml.etree.parse("./flows/" + file)
		print("************\n")
		print(file)
		print("\n")
		print(lxml.etree.tostring(tree, pretty_print=True))

def refreshTables():
	if os.path.isdir('./flows'):
		file_list = os.listdir('./flows')
	else:
		print('No flow was added from here, terminating ...')
		sys.exit()

	name_set = set()
	for file_name in file_list:
		params = file_name.replace('.xml', '').split('_')
		name_set.add(params[0])

	for name in name_set:
		for table in range(MAX_NUMBER_OF_TABLES):
			url = TABLE_INVENTORY.format(name, table)

			headers = {
				"Content-Type" : "application/xml",
				"Accept" : "application/xml"
			}

			auth = (
				"admin",
				"admin"
			)

			try:
				response = requests.delete(
						url=url,
						headers=headers,
						auth=auth,
						timeout=TIMEOUT
					)

				print('deleted : ' + url)
				print('response : HTTP ' + str(response.status_code))

			except ConnectionRefusedError:
				print("Connection Refused, ODL is dead.")
				# sys.exit()

			except TimeoutError:
				print("Connection Timeout ... controller is busy.")
				# sys.exit()

			except:
				print("Something is wrong ...")

def sendRequests():
	for file_name in file_list.keys():
		if file_list[file_name] == "done":
			continue
		else:
			params = file_name.replace('.xml', '').split('_')
			url = FLOW_INVENTORY.format(params[0], params[1], params[2])
			file = open('./flows/' + file_name, "r")
			# data = str(file.read())
			data = file.read()

			headers = {
				"Content-Type" : "application/xml",
				"Accept" : "application/xml"
			}

			auth = (
				"admin",
				"admin"
			)

			try:
				response = requests.put(
						url=url,
						data=data,
						headers=headers,
						auth=auth,
						timeout=TIMEOUT
					)

				print('sent to : ' + url)
				print('response : HTTP ' + str(response.status_code))

				if response.status_code == 200 or response.status_code == 201:
					file_list[file_name] = "done"

			except ConnectionRefusedError:
				print("Connection Refused, ODL is dead.")
				sys.exit()

			except TimeoutError:
				print("Connection Timeout ... controller is busy.")
				sys.exit()

def LLDPHandle(sw_list):
	for sw in sw_list:
		# node_num = int(sw[1:])
		node_num = int(sw.split(':')[-1])
		TableMissFlow(node_num)
		updateID(switch_name=sw, table_id=0)
		# ARPFlow(
		# 	node_num=node_num,
		# 	table=0,
		# 	id=flow_id_list[switch_name][0],
		# 	priority=123
		# 	)

def addRoute(route, nw_dst, dl_dst):
	route_sliced = [[route[i], route[i+1], route[i+2]] for \
	 i in map(lambda x: 3*x, range(len(route)//3))]

	for pair in route_sliced:
		switch_name = pair[0]
		in_port = pair[1]
		out_port = pair[2]
		node_num = int(switch_name.split(':')[-1])

		table=0

		IPv4ForwardingFlow(
			node_num=node_num,
			in_port=in_port,
			out_port=out_port,
			table=table,
			id=flow_id_list[switch_name][table],
			nw_dst=nw_dst,
			dl_dst=dl_dst,
			priority=200
			)

def updateID(switch_name, table_id):
	# if switch_name not in flow_id_list.keys():
	# 	flow_id_list[switch_name] = {i:0 for i in range(MAX_NUMBER_OF_TABLES)}
	# flow_id_list[switch_name][table_id] += 1	

	# for key in flow_id_list.keys():
	# 	print(key + ' --> ' + str(flow_id_list[key]))
	# print('***************')
	pass

if __name__ == '__main__':
	print("remove tables?")
	inp = input()

	if inp == 'n':
		LLDPHandle(['openflow:1'])

		ARPFlow(1, 0, 1, 123)
		# ARPFlow(2, 0, 1, 123)
		# ARPFlow(3, 0, 1, 123)

		IPv4ForwardingFlow(1, 1, 2, 0, 2, "10.0.0.2/32", "00:00:00:00:00:02", 123)
		# IPv4ForwardingFlow(1, 1, 2, 0, 3, "10.0.0.3/32", "00:00:00:00:00:03", 123)
		IPv4ForwardingFlow(1, 2, 1, 0, 4, "10.0.0.1/32", "00:00:00:00:00:01", 123)

		# IPv4ForwardingFlow(3, 1, 2, 0, 2, "10.0.0.1/32", "00:00:00:00:00:01", 123)
		# IPv4ForwardingFlow(3, 1, 2, 0, 3, "10.0.0.2/32", "00:00:00:00:00:02", 123)
		# IPv4ForwardingFlow(3, 2, 1, 0, 4, "10.0.0.3/32", "00:00:00:00:00:03", 123)

		# IPv4ForwardingFlow(2, 1, 2, 0, 2, "10.0.0.1/32", "00:00:00:00:00:01", 123)
		# IPv4ForwardingFlow(2, 1, 3, 0, 3, "10.0.0.3/32", "00:00:00:00:00:03", 123)
		# IPv4ForwardingFlow(2, 2, 1, 0, 4, "10.0.0.2/32", "00:00:00:00:00:02", 123)
		# IPv4ForwardingFlow(2, 3, 1, 0, 5, "10.0.0.2/32", "00:00:00:00:00:02", 123)
		# IPv4ForwardingFlow(2, 2, 3, 0, 6, "10.0.0.3/32", "00:00:00:00:00:03", 123)
		# IPv4ForwardingFlow(2, 3, 2, 0, 7, "10.0.0.1/32", "00:00:00:00:00:01", 123)

		sendRequests()
		# getTopology_json()

		# topo = createTopologyGraph()
		# sw_list = topo.node_name_list
		# for switch_name in sw_list:
		# 	flow_id_list[switch_name] = {i:0 for i in range(MAX_NUMBER_OF_TABLES)}

		# LLDPHandle(sw_list)

		# if os.path.isfile('./nrd.json'):
		# 	with open('./nrd.json', 'r') as file:
		# 		j = json.load(file)
		# 		paths = j["paths"]
		# 		for path in paths:
		# 			nw_dst = path["nw_dst"]
		# 			dl_dst = path["dl_dst"]
		# 			route = path["route"]
		# 			addRoute(
		# 				nw_dst=nw_dst,
		# 				dl_dst=dl_dst,
		# 				route=route
		# 				)
		# 	sendRequests()

		# else:
		# 	print('No network routing discription file was found, aborting ...')
		# 	sys.exit()

		# check()
	else:
		refreshTables()