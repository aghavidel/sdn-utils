import re
import json
import xml.etree.ElementTree as ET
import xml.dom.minidom
from constants import (
	FLOW_INVENTORY_NAMESPACE,
)

def flowParser(flow_ovs, flow_id, **kwargs):
	"""
	Parse an OVS flow into an ODL-XML format flow, until now
	supported flows look like this :

	ovs-flow :: <match 1>,<match 2> ... ,actions=<action 1>,<action 2> ...

			    |--------matches--------||------------actions-------------|

	so we can split the command from 'actions=' and get the comma-seperated
	list of matches and actions, now supported matches are:

	--> table, in_port, eth_type, nw_src, nw_dst, dl_src, dl_dst, mpls_bos, 
		mpls_label, mpls_tc

	list of actions supported :

	--> output, goto_table, push_mpls, pop_mpls, set_field
	"""

	flow_ovs = flow_ovs.replace(" ","")

	if ',actions=' in flow_ovs:

		ls = flow_ovs.split(',actions=')
		actions = ls[1].split(',')
		matches = ls[0].split(',')

		flow = ET.Element('flow', xmlns=FLOW_INVENTORY_NAMESPACE)
		ET.SubElement(flow, "id").text = str(flow_id)

		# for element in matches 
		for i in range(len(matches)):
			element = matches[i]
			ls = element.split('=')
			(key, value) = (ls[0], ls[1])

			if key == "table":
				ET.SubElement(flow, "table_id").text = value
			if key == "priority":
				ET.SubElement(flow, "priority").text = value


			elif key == "in_port":
				if "match" not in locals():
					match = ET.SubElement(flow, "match")
				ET.SubElement(match, "in-port").text = value
			elif key == "nw_src":
				if "match" not in locals():
					match = ET.SubElement(flow, "match")
				ET.SubElement(match, "ipv4-source").text = value
			elif key == "nw_dst":	
				if "match" not in locals():
					match = ET.SubElement(flow, "match")
				ET.SubElement(match, "ipv4-destination").text = value


			elif key == "dl_src":
				if "match" not in locals():
					match = ET.SubElement(flow, "match")
				if "ethernet_match" not in locals():
					ethernet_match = ET.SubElement(match, "ethernet-match")
				if "ethernet_source" not in locals():
					ethernet_source = ET.SubElement(ethernet_match, "ethernet-source")
				ET.SubElement(ethernet_source, "address").text = value
			elif key == "dl_dst":
				if "match" not in locals():
					match = ET.SubElement(flow, "match")
				if "ethernet_match" not in locals():
					ethernet_match = ET.SubElement(match, "ethernet-match")
				if "ethernet_destination" not in locals():
					ethernet_destination = ET.SubElement(ethernet_match, "ethernet-destination")
				ET.SubElement(ethernet_destination, "address").text = value
			elif key == "eth_type":
				if "match" not in locals():
					match = ET.SubElement(flow, "match")
				if "ethernet_match" not in locals():
					ethernet_match = ET.SubElement(match, "ethernet-match")
				if "ethernet_type" not in locals():
					ethernet_type = ET.SubElement(ethernet_match, "ethernet-type")
				ET.SubElement(ethernet_type, "type").text = value


			elif key == "mpls_bos":
				if "match" not in locals():
					match = ET.SubElement(flow, "match")
				if "protocol_match_fields" not in locals():
					protocol_match_fields = ET.SubElement(match, "protocol-match-fields")
				ET.SubElement(protocol_match_fields, "mpls-bos").text = value
			elif key == "mpls_tc":
				if "match" not in locals():
					match = ET.SubElement(flow, "match")
				if "protocol_match_fields" not in locals():
					protocol_match_fields = ET.SubElement(match, "protocol-match-fields")
				ET.SubElement(protocol_match_fields, "mpls-tc").text = value
			elif key == "mpls_label":
				if "match" not in locals():
					match = ET.SubElement(flow, "match")
				if "protocol_match_fields" not in locals():
					protocol_match_fields = ET.SubElement(match, "protocol-match-fields")
				ET.SubElement(protocol_match_fields, "mpls-label").text = value


		# print("*"*10 + "check" + "*"*10)
		# print(actions)
		# for element in actions:
		for i in range(len(actions)):
			element = actions[i]
			ls = element.split(":")
			(key, value) = (ls[0], ls[1])

			if "instructions" not in locals():
				instructions = ET.SubElement(flow, "instructions")
				instruction = ET.SubElement(instructions, "instruction")
				ET.SubElement(instruction, "order").text = str(0)
				apply_actions = ET.SubElement(instruction, "apply-actions")

			action = ET.SubElement(apply_actions, "action")
			ET.SubElement(action, "order").text = str(i)

			if key == "output":
				output_action = ET.SubElement(action, "output-action")
				ET.SubElement(output_action, "output-node-connector").text = value
			if key == "push_mpls":
				push_mpls_action = ET.SubElement(action, "push-mpls-action")
				ET.SubElement(push_mpls_action, "ethernet-type").text = str(34887)
			if key == "pop_mpls":
				pop_mpls_action = ET.SubElement(action, "pop-mpls-action")
				ET.SubElement(pop_mpls_action, "ethernet-type").text = str(2048)
			if key == "set_field":
				set_field = ET.SubElement(action, "set-field")
				le = value.split("->")
				(field_name, field_value) = (le[1], le[0])
				
				if field_name == "mpls_label":
					protocol_match_fields = ET.SubElement(set_field, "protocol-match-fields")
					ET.SubElement(protocol_match_fields, "mpls-label").text = field_value
				elif field_name == "nw_dst":
					ET.SubElement("ipv4-destination").text = field_value
				elif field_name == "nw_src":
					ET.SubElement("ipv4-source").text = field_value
				elif field_name == "dl_dst":
					ethernet_match = ET.SubElement(set_field, "ethernet-match")
					ethernet_destination = ET.SubElement(ethernet_match, "ethernet-destination")
					ET.SubElement(ethernet_destination, "address").text = field_value
				elif field_name == "dl_src":
					ethernet_match = ET.SubElement(set_field, "ethernet-match")
					ethernet_source = ET.SubElement(ethernet_match, "ethernet-source")
					ET.SubElement(ethernet_source, "address").text = field_value

		for (key, value) in kwargs.items():
			fixed_key = str(key).replace("_", "-")
			ET.SubElement(flow, fixed_key).text = str(value)

		data = ET.tostring(flow).decode("utf-8")
		return data
		# file = open("test_parser.xml", "w")
		# file.write(data)
		# file.close()

if __name__ == '__main__':
	flow = input()
	flow_id = input()
	data = flowParser(flow, flow_id, barrier="false", idle_timeout=100)
	file = open("test_parser.xml", "w")
	file.write(data)
	file.close()
