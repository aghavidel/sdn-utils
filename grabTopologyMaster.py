import requests
import os
import sys
import xml.etree.ElementTree as ET
import json
import errno
from socket import error as serror
from constants import (
		SLAVE_TOPOLOGY_GET,
		NETCONF_SERVER,
		MASTER_TOPOLOGY_GET,
		TIMEOUT
	)
from requests.exceptions import (
		Timeout,
		RequestException
	)


"""
Same as the old grabTopology.py, but it tries to gather topology data from 
all SLAVE controllers via only the MASTER.
"""

def getSlaveTopology_json(
	master_ip, master_restconf_port, master_username, master_password, controller_name):
	"""
	Interface with OpenDaylight to grab the recognized topology.
	This function only interfaces with a single SLAVE controller, after
	this, it will save the topology data to a 'topology' directory with
	the name '<topology-id>_<controller_name>'
	"""
	auth = (
		master_username,
		master_password
		)

	headers = {
		"Content-Type" : "application/xml"
		}

	url = MASTER_TOPOLOGY_GET.format(master_ip, master_restconf_port, controller_name)

	if not os.path.isdir('./topology'):
		os.mkdir('topology')

	try:
		response = requests.get(
				url=url,
				auth=auth,
				headers=headers,
				timeout=TIMEOUT
			)

		st = response.status_code
		print('response : HTTP ' + str(st))

		if st == 200:
			data = response.json()

			for tp in data['network-topology']['topology']:
				topology_id = tp['topology-id']

				if topology_id == "topology-netconf":
					continue

				file_name = controller_name + '_' + topology_id

				with open('./topology/' + file_name + '.json', 'w') as file:
					json.dump(tp, file)

		elif st == 401:
			print("Unauthorzied on {}, check username and password.".format(
					controller_name
				))

	except Timeout:
		print("Connection Timeout ... controller is busy.")
		sys.exit()

	except RequestException:
		print("Problem contacting {}, check the URL and the RESTCONF plugin.".format(
			controller_name
		))
		sys.exit()

def getTopology_json(master):
	"""
	Get Topology data from every single SLAVE controller under the given 'master',
	a dict object holding the MASTER informations.

	First we retreive the mounted NETCONF devices on MASTER and then call
	each of the SLAVE controllers by name (device names and controller names are
	assumed to be the same, see createControllerHierarchy.py).

	Then SLAVE topologies are retrieved and stored in a file, necessary python
	topology objects are created afterwards.
	"""

	master_ip = master["ip"]
	master_restconf_port = master["restconf_port"]
	master_username = master["username"]
	master_password = master["password"]

	url = NETCONF_SERVER.format(master_ip, master_restconf_port)

	headers = {
		"Accept" : "application/json"
	}

	auth = (
		master_username,
		master_password
	)

	try:
		reponse = requests.get(
			url=url,
			headers=headers,
			auth=auth,
			timeout=TIMEOUT
		)

		st = reponse.status_code
		print("reponse : HTTP " + str(st))

		slave_names = []

		if st == 200:
			data = reponse.json()
			# for node in data["topology"]["node"]:
			# 	slave_names.append(node["node-id"])
			for topo in data["topology"]:
				for node in topo["node"]:
					slave_names.append(node["node-id"])

		elif st == 401:
			print("Unauthorzied on MASTER, check username and password.")

	except Timeout:
		print("Connection Timeout ... controller is busy.")
		sys.exit()

	except RequestException:
		print("Problem contacting MASTER, check the URL and the RESTCONF plugin.")
		sys.exit()

	print("*"*10 + " Slave names : " + str(slave_names))

	for slave in slave_names:
		getSlaveTopology_json(
			master_ip=master_ip,
			master_restconf_port=master_restconf_port,
			master_username=master_username,
			master_password=master_password,
			controller_name=slave
			)


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
	master = {
		"ip" : "192.168.0.161",
		"restconf_port" : 30267,
		"username" : "admin",
		"password" : "Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U"
	}

	getTopology_json(master)
	topo = createTopologyGraph()