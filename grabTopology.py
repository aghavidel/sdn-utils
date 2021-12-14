import requests
import os
import sys
import xml.etree.ElementTree as ET
import json
import errno
from socket import error as serror
from constants import (
		TOPOLOGY_GET,
		TIMEOUT
	)

"""
This file will grab the topology from OpenDaylight and break it into
a set of python 'Link' and 'Node' classes, it will allow for any optimization
process for route optimization.
"""

def getTopology_json():
	"""
	Interface with OpenDaylight to grab the recognized topology
	"""
	auth = (
		"admin",
		"admin"
		)

	headers = {
		"Content-Type" : "application/xml"
		}

	if not os.path.isdir('./topology'):
		os.mkdir('topology')

	try:
		response = requests.get(
				url=TOPOLOGY_GET,
				auth=auth,
				headers=headers,
				timeout=TIMEOUT
			)

		st = response.status_code
		print('response : HTTP ' + str(st))

		if st == 200 or st == 201:
			data = response.json()

			for tp in data['network-topology']['topology']:
				topology_id = tp['topology-id']

				with open('./topology/' + topology_id + '.json', 'w') as file:
					json.dump(tp, file)

	except serror as e:
		if e.errno == 111:
			raise e
		else:
			print("Connection Refused, ODL is either dead or not active.")
		sys.exit()

	except TimeoutError:
		print("Connection Timeout ... controller is busy.")
		sys.exit()

def createTopologyGraph():
	"""
	create the Topology object
	"""
	for file_name in os.listdir('./topology'):
		with open('./topology/' + file_name, 'r') as file:
			try:
				j = json.load(file)
				topology_id = j['topology-id']

				nodes = []
				links = []

				for node in j['node']:
					if "host-tracker-service:id" in node:
						continue

					node_id = node['node-id']

					if "host" in node_id:
						continue

					tp_pair_list = node['termination-point']
					tp_list = []
					for tp_pair in tp_pair_list:
						tp_list.append(str(tp_pair['tp-id']))

					# print(tp_list)
					nodes.append(Node(
							topology_id=topology_id,
							node_id=node_id,
							node_intf=tp_list
						))

				for link in j['link']:
					link_id = str(link['link-id'])
					tp1 = str(link['source']['source-tp'])
					tp2 = str(link['destination']['dest-tp'])

					if "host" in link_id:
						continue

					links.append(Link(
							topology_id=topology_id,
							link_id=link_id,
							tp1=tp1,
							tp2=tp2
						))

			except KeyError:
				print("Malformed topology file!")
				print("If the topology file was added manually, check it, otherwise \
						restart the controller")
				sys.exit()

	# for node in nodes:
	# 	node.showNode()

	# for link in links:
	# 	link.showLink()

	topo = Topology(topology_id=topology_id, nodes=nodes, links=links)
	topo.createGraph()
	topo.showTopology()

	return topo

class Node():
	"""
	Contains the attributes of a node ...
	"""
	def __init__(self, topology_id, node_id, node_intf):
		self.node_id = node_id
		self.node_intf = node_intf
		self.topology_id = topology_id

	def showNode(self):
		print('**************** NODE ********************')
		print('Topology : ' + self.topology_id)
		print('ID : '  + self.node_id)
		print('Interfaces : ' + str(self.node_intf))
		print('**************** NODE ********************\n\n')

class Link():
	"""
	Contains the attributes of a bi-directional link ...
	"""
	def __init__(self, topology_id, tp1, tp2, link_id):
		self.link_id = link_id
		self.tp1 = tp1
		self.tp2 = tp2
		self.w = None
		self.topology_id = topology_id

	def showLink(self):
		print('**************** LINK ********************')
		print('Topology : ' + self.topology_id)
		print('ID : ' + self.link_id)
		if self.w is not None:
			print('Weight : ' + str(self.w))
		else:
			print('Weight : None')
		print('(TP1, TP2) : ' + str((self.tp1, self.tp2)))
		print('**************** LINK ********************\n\n')

class Topology():
	"""
	Contains the attributes of the topology ...
	"""
	def __init__(self, topology_id, nodes, links):
		self.topology_id = topology_id
		self.nodes = nodes
		self.links = links
		self.graph = None

	def createGraph(self):
		"""
		Create the adjacency matrix of the topology ...
		"""
		n = len(self.nodes)
		graph = [[0 for j in range(n)] for i in range(n)]
		
		node_name_list = list(map(lambda node: str(node.node_id), self.nodes))
		node_map = {}
		
		for i in range(n):
			node_map[node_name_list[i]] = i

		link_name_list = map(lambda link: (link.tp1.rsplit(':', 1)[0], link.tp2.rsplit(':', 1)[0]), self.links)
		
		for link_name in link_name_list:
			graph[node_map[link_name[0]]][node_map[link_name[1]]] = 1
			graph[node_map[link_name[1]]][node_map[link_name[0]]] = 1

		self.graph = graph
		self.node_map = node_map
		self.node_name_list = node_name_list

	def showTopology(self):
		print('**************** TOPO ********************')
		print('Topology : ' + self.topology_id)
		print('Nodes : ' + str(self.node_name_list))
		print('Graph : Node Mapping --> ' + str(self.node_name_list))
		for i in range(len(self.graph)):
			print(self.graph[i])
		print('**************** TOPO ********************\n\n')

if __name__ == '__main__':
	getTopology_json()
	topo = createTopologyGraph()