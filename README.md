# sdn-utils
&lt;auto commit on December 14>

This repository contains some utilities that can help when working with SDN controllers. Here, we assume that you are mostly using ODL controller (release 10, Neon).
Most of the time, you only Restconf and Openflow (although, Netconf can be used if it your appliences do not support Openflow, which happens a lot). The infrastructure
can be created with *mininet*, using either *OVSKernelSwitch* or just Linux host routers (you'll need some routing agents if you go that route ...).

**Note:** This project does not use YANG models directly, if you are trying to go that route, you'll need to use internal APIs in your controller, not external interfaces (
for ODL, this API is *odl-yangtools*).
