# This script creates the flows needed for connectivity in
# the 'small_test.py' topology, it creates the necessary
# flows (in ovs-ofctl format), passes them to the 'flowParser'
# function and saves the output .xml files in ~/demo_flows.
#
# After this, a python REST client sends every flow to the
# SDNC inventory.
# 
# TODO: It is necessary to delete all flows before adding the new
# ones, otherwise a bug can be triggered in ODL that refreshes some of
# the switch flows, while this does not necessary jepordize network
# connectivity, it does reset all flow statistics on the switch, which
# will be bad for any monitoring tool on the switch.

from flowParser import flowParser
import requests
import os
import shutil
from constants import (
		MASTER_FLOW_INVENTORY,
		TIMEOUT,
		SLAVE_FLOW_INVENTORY
	)

flows = {
	"openflow:1" : [
		("table=0,priority=0,actions=output:CONTROLLER", 1),
		("table=0,priority=100,eth_type=0x800,in_port=1,nw_dst=10.0.0.1/32,actions=output:2", 2),
		("table=0,priority=100,eth_type=0x800,in_port=2,nw_dst=10.0.0.2/32,actions=output:1", 3),
		("table=0,priority=100,eth_type=0x800,in_port=2,nw_dst=10.0.0.3/32,actions=output:1", 4),
		("table=0,priority=100,eth_type=0x800,in_port=2,nw_dst=10.0.0.4/32,actions=output:1", 5),
		("table=0,priority=50,eth_type=0x806,actions=output:FLOOD", 6)
	],

	"openflow:2" : [
		("table=0,priority=0,actions=output:CONTROLLER", 1),
		("table=0,priority=100,eth_type=0x800,in_port=1,nw_dst=10.0.0.2/32,actions=output:2", 2),
		("table=0,priority=100,eth_type=0x800,in_port=2,nw_dst=10.0.0.1/32,actions=output:1", 3),
		("table=0,priority=100,eth_type=0x800,in_port=2,nw_dst=10.0.0.3/32,actions=output:1", 4),
		("table=0,priority=100,eth_type=0x800,in_port=2,nw_dst=10.0.0.4/32,actions=output:1", 5),
		("table=0,priority=50,eth_type=0x806,actions=output:FLOOD", 6)
	],

	"openflow:3" : [
		("table=0,priority=0,actions=output:CONTROLLER", 1),
		("table=0,priority=100,eth_type=0x800,in_port=2,nw_dst=10.0.0.1/32,actions=output:1", 2),
		("table=0,priority=100,eth_type=0x800,in_port=1,nw_dst=10.0.0.2/32,actions=output:2", 3),
		("table=0,priority=100,eth_type=0x800,nw_dst=10.0.0.3/32,actions=push_mpls:0x8847,set_field:300->mpls_label,output:3", 4),
		("table=0,priority=100,eth_type=0x800,nw_dst=10.0.0.4/32,actions=push_mpls:0x8847,set_field:400->mpls_label,output:3", 5),
		("table=0,priority=200,eth_type=0x8847,in_port=3,mpls_bos=0,actions=pop_mpls:0x8847,output:TABLE", 6),
		("table=0,priority=200,eth_type=0x8847,in_port=3,mpls_bos=1,actions=pop_mpls:0x800,output:TABLE", 7),
		("table=0,priority=200,eth_type=0x800,in_port=3,nw_dst=10.0.0.1/32,actions=output:1", 8),
		("table=0,priority=200,eth_type=0x800,in_port=3,nw_dst=10.0.0.2/32,actions=output:2", 9),
		("table=0,priority=50,eth_type=0x806,actions=output:FLOOD", 10)
	],

	"openflow:4" : [
		("table=0,priority=0,actions=output:CONTROLLER", 1),
		("table=0,priority=100,in_port=1,eth_type=0x8847,mpls_label=300,actions=output:2", 2),
		("table=0,priority=100,in_port=1,eth_type=0x8847,mpls_label=400,actions=output:3", 3),
		("table=0,priority=400,in_port=2,eth_type=0x8847,mpls_label=600,actions=output:3", 9),
		("table=0,priority=400,in_port=3,eth_type=0x8847,mpls_label=700,actions=output:2", 10),
		("table=0,priority=200,in_port=2,eth_type=0x8847,actions=output:1", 4),
		("table=0,priority=200,in_port=3,eth_type=0x8847,actions=output:1", 5),
		("table=0,priority=300,eth_type=0x800,nw_dst=10.0.0.3/32,actions=output:2", 6),
		("table=0,priority=300,eth_type=0x800,nw_dst=10.0.0.4/32,actions=output:3", 7),
		("table=0,priority=50,eth_type=0x806,actions=output:FLOOD", 8)
	],

	"openflow:5" : [
		("table=0,priority=0,actions=output:CONTROLLER", 1),
		("table=0,priority=100,in_port=1,eth_type=0x8847,mpls_label=300,actions=pop_mpls:0x800,output:2", 2),
		("table=0,priority=200,in_port=2,eth_type=0x800,nw_dst=10.0.0.1/32,actions=push_mpls:0x8847,set_field:500->mpls_label,output:1", 3),
		("table=0,priority=200,in_port=2,eth_type=0x800,nw_dst=10.0.0.2/32,actions=push_mpls:0x8847,set_field:500->mpls_label,output:1", 4),
		("table=0,priority=200,in_port=2,eth_type=0x800,nw_dst=10.0.0.4/32,actions=push_mpls:0x8847,set_field:600->mpls_label,output:1", 5),
		("table=0,priority=200,in_port=1,eth_type=0x8847,mpls_label=700,actions=pop_mpls:0x800,output:2", 6),
		("table=0,priority=50,eth_type=0x806,actions=output:FLOOD", 7)
	],

	"openflow:6" : [
		("table=0,priority=0,actions=output:CONTROLLER", 1),
		("table=0,priority=100,in_port=1,eth_type=0x8847,mpls_label=400,actions=pop_mpls:0x800,output:2", 2),
		("table=0,priority=200,in_port=2,eth_type=0x800,nw_dst=10.0.0.1/32,actions=push_mpls:0x8847,set_field:500->mpls_label,output:1", 3),
		("table=0,priority=200,in_port=2,eth_type=0x800,nw_dst=10.0.0.2/32,actions=push_mpls:0x8847,set_field:500->mpls_label,output:1", 4),
		("table=0,priority=200,in_port=2,eth_type=0x800,nw_dst=10.0.0.3/32,actions=push_mpls:0x8847,set_field:700->mpls_label,output:1", 5),
		("table=0,priority=200,in_port=1,eth_type=0x8847,mpls_label=600,actions=pop_mpls:0x800,output:2", 6),
		("table=0,priority=50,eth_type=0x806,actions=output:FLOOD", 7)
	]
}

if os.path.isdir('./demo_flows'):
	shutil.rmtree('demo_flows')
os.mkdir('demo_flows')

for key in flows.keys():
	for tp in flows[key]:
		name = key + '_' + str(tp[1])
		file = open('./demo_flows/' + name + '.xml', 'w')
		data = flowParser(tp[0], tp[1])
		file.write(data)
		file.close()

cmd = input("Send flows?")

if cmd == 'y':
	cmap = {
		"openflow:1" : "c1",
		"openflow:2" : "c1",
		"openflow:3" : "c1",
		"openflow:4" : "c2",
		"openflow:5" : "c2",
		"openflow:6" : "c2",
	}
	for file_name in os.listdir('./demo_flows'):
		name = file_name.replace('.xml', '')
		ls = name.split('_')
		file = open('./demo_flows/' + file_name, "r")
		node = ls[0]
		flow_id = ls[1]
		url = MASTER_FLOW_INVENTORY.format(
				'192.168.0.162',
				'30267',
				cmap[node],
				node,
				"0",
				flow_id
			)
		print("\n\nURL: " + url)

		# umap = {
		# 	"c1" : SLAVE_FLOW_INVENTORY.format(
		# 			'127.0.0.1',
		# 			'8181',
		# 			node,
		# 			"0",
		# 			flow_id
		# 		),

		# 	"c2" : SLAVE_FLOW_INVENTORY.format(
		# 			'192.168.1.1',
		# 			'8181',
		# 			node,
		# 			"0",
		# 			flow_id
		# 		)
		# }

		# url = umap[cmap[node]]

		data = file.read()

		headers = {
			"Content-Type" : "application/xml"
		}

		auth = (
			"admin",
			"Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U"
		)

		# auth = (
		# 	"admin",
		# 	"admin"
		# )

		try:
			response = requests.put(
				url=url,
				data=data,
				headers=headers,
				timeout=TIMEOUT,
				auth=auth
			)

			st = response.status_code

			print("file " + file_name + " was sent.")
			print("response : HTTP " + str(st))

			if st != 200 or st != 201:
				print(response.text)
		except:
			print("Something went wrong.")
			if response is not None:
				print(response)





