# This script creates a simple test topology to check the connectivty 
# between two seperate ODL controllers that are configured only via 
# SDNC, the network looks like the following.
# 
# +----+      +----+                           +----+      +----+
# | h1 | ---- | s1 | --+                   +-- | s5 | ---- | h3 |
# +----+      +----+   |                   |   +----+      +----+
#					   |                   |
#                    +----+              +----+
#					 | s3 | ------------ | s4 |
#                    +----+              +----+
#                      |                   |
# +----+      +----+   |                   |   +----+      +----+
# | h2 | ---- | s2 | --+                   +-- | s6 | ---- | h4 |
# +----+      +----+                           +----+      +----+
#
#\______________________/\_______________/\_____________________/
#          
#       IP Routing          (BGP Routing)       MPLS Routing
#    <controlled by c1>           |           <controlled by c2>
#								  |
#								  v
#                    /----------------------------\
#					 | This part consists of the  |
#					 | edge routers, currenly it  |
#                    | is just a single link and  |
#                    | the real "edge routing" is |
#					 | done by s3, in the next    |
#					 | step, it will be a BGP     |
#					 |		    network.          |
#                    \----------------------------/
#
# * The goal is that all the hosts can ping each other, h1 and h2
#   will only exchange IP packets while h3 and h4 only exchange 
#   MPLS packets, if a host (like h1) wants to ping a host in the
#   other cluster, it will send a packet the usual way and the routing
#   is done by s3 and s4.

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink
from mininet.node import (
		OVSSwitch,
		RemoteController
	)
from functools import partial

setLogLevel('info')

c1 = RemoteController(
		name="c1",
		ip="127.0.0.1",
		port=6633
	)

c2 = RemoteController(
		name="c2",
		ip="192.168.1.1",
		port=6633
	)

cmap = {
	's1' : c1,
	's2' : c1,
	's3' : c1,
	's4' : c2,
	's5' : c2,
	's6' : c2
}

class Switch(OVSSwitch):
	def start(self, controllers):
		super(Switch, self).start([cmap[self.name]])

OF13Switch = partial(Switch, protocols="OpenFlow13")

net = Mininet(
		switch=OF13Switch,
		controller=RemoteController,
		link=TCLink
	)

s1 = net.addSwitch("s1")
s2 = net.addSwitch("s2")
s3 = net.addSwitch("s3")
s4 = net.addSwitch("s4")
s5 = net.addSwitch("s5")
s6 = net.addSwitch("s6")

s1.start([c1, c2])
s2.start([c1, c2])
s3.start([c1, c2])
s4.start([c1, c2])
s5.start([c1, c2])
s6.start([c1, c2])

net.addLink("s1", "s3")
net.addLink("s2", "s3")
net.addLink("s3", "s4")
net.addLink("s4", "s5")
net.addLink("s4", "s6")

h1 = net.addHost('h1')
h2 = net.addHost('h2')
h3 = net.addHost('h3')
h4 = net.addHost('h4')

net.addLink(s1, h1)
net.addLink(s2, h2)
net.addLink(s5, h3)
net.addLink(s6, h4)

net.build()
net.start()
CLI(net)
net.stop()


