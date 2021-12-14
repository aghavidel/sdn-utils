"""
CONTROLLER_IP = '127.0.0.1'
CONTROLLER_PORT = 6633
CONTROLLER_LISTEN_TIME = 60
RECEIVE_PACKET_SIZE = 2048
CONTROLLER_SLEEP_TIME = 0.1
SLAVE_TIMEOUT = 10
MASTER_TIMEOUT = 60

TABLE_INVENTORY = "http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/{}/table/{}" 
FLOW_INVENTORY = "http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/{}/table/{}/flow/{}"
TOPOLOGY_GET = "http://127.0.0.1:8181/restconf/operational/network-topology:network-topology"
XMLNS = "urn:opendaylight:flow:inventory"

NUMBER_OF_SWITCHES = 5
P = 0.5
MAX_NUMBER_OF_TABLES = 10

ETHER_TYPE = {
	"IPV4" : "2048",
	"ARP" : "2054",
	"IPV6" : "34525",
	"MPLS-uni" : "34887",
	"MPLS-multi" : "34888"
}
"""

# CONTROLLER PARAMETERS
CONTROLLER_IP = '127.0.0.1'
SLAVE_PORT = 6633
CONTROLLER_LISTEN_TIME = 60
RECEIVE_PACKET_SIZE = 2048
CONTROLLER_SLEEP_TIME = 0.1
TIMEOUT = 60
NETCONF_KEEPALIVE = 120

SLAVE_TABLE_INVENTORY = "http://{}:{}/restconf/config/opendaylight-inventory:nodes/node/{}/table/{}" 
SLAVE_FLOW_INVENTORY = "http://{}:{}/restconf/config/opendaylight-inventory:nodes/node/{}/table/{}/flow/{}"
SLAVE_TOPOLOGY_GET = "http://{}:{}/restconf/operational/network-topology:network-topology"

MASTER_TABLE_INVENTORY = "http://{}:{}/restconf/config/network-topology:network-topology/topology/topology-netconf/node/{}/\
yang-ext:mount/opendaylight-inventory:nodes/node/{}/table/{}"
MASTER_FLOW_INVENTORY = "http://{}:{}/restconf/config/network-topology:network-topology/topology/topology-netconf/node/{}/\
yang-ext:mount/opendaylight-inventory:nodes/node/{}/table/{}/flow/{}"
MASTER_TOPOLOGY_GET = "http://{}:{}/restconf/operational/network-topology:network-topology/topology/topology-netconf/node/{}/\
yang-ext:mount/network-topology:network-topology"
MASTER_NETCONF_CONNECTOR = "http://{}:{}/restconf/config/network-topology:network-topology/topology/topology-netconf/node/{}"
NETCONF_SERVER = "http://{}:{}/restconf/config/network-topology:network-topology/topology/topology-netconf"

FLOW_INVENTORY_NAMESPACE = "urn:opendaylight:flow:inventory"
NETCONF_SERVER_NAMESPACE = "urn:TBD:params:xml:ns:yang:network-topology"
NETCONF_NODE_TOPOLOGY_NAMESPACE = "urn:opendaylight:netconf-node-topology"

NUMBER_OF_SWITCHES = 5
P = 0.5
MAX_NUMBER_OF_TABLES = 10

ETHER_TYPE = {
	"IPV4" : "2048",
	"ARP" : "2054",
	"IPV6" : "34525",
	"MPLS-uni" : "34887",
	"MPLS-multi" : "34888"
}