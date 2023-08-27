#!/usr/bin/env python3
# Version:  0.01.01
# Author:   AT Sowell
# Modified: 2023-08-20
##########################################################################
# Description
# Create user-defined CSV containing:
# 	host (IP)
# 	username
# 	password (base64-encoded)
# 	commands
# import requests
import json
import re

# from requests.exceptions import HTTPError
# from sys import argv
# user = argv[1]
# password = argv[2]
# url = 'https://127.0.0.1/api/v1/sensors?offset=0&limit=200'
jsonResponse = {'total_count': 2, 'results': [{'id': 4, 'name': 'Sensor 5.2', 'address': '', 'port': 0, 'type': 'PASSIVE', 'sensor_version': '5.2.1', 'state': 'OPERATIVE_ON', 'health_status': {'cpu_load_avg_1_min': {'name': '', 'level': 'NORMAL', 'current_value': '27.5%'}, 'memory_usage': {'name': '', 'level': 'NORMAL', 'current_value': '48.66%'}, 'throughput': {'name': '', 'level': 'NORMAL', 'current_value': '1936690.0 bps'}, 'dropped_packets': {'name': '', 'level': 'NORMAL', 'current_value': '0%'}, 'disk_usage': [{'name': '/', 'level': 'NORMAL', 'current_value': '72%'}, {'name': '/etc/timezone', 'level': 'NORMAL', 'current_value': '72%'}, {'name': '/opt/nids/state', 'level': 'NORMAL', 'current_value': '72%'}, {'name': '/usr/share/zoneinfo/Europe/Amsterdam', 'level': 'NORMAL', 'current_value': '72%'}], 'net_if_status': [{'name': 'br-7e6edf1eff12', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'ens160', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'ens192', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'veth04fa1ed', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'veth624471b', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'vethb1b3581', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'vethc97d639', 'level': 'NORMAL', 'current_value': 'Running'}], 'license_status': {'name': '', 'level': 'NORMAL', 'current_value': 'VALID'}, 'services': []}, 'is_reversed_conn': True}, {'id': 6, 'name': 'Sensor 5.1.3', 'address': '', 'port': 0, 'type': 'PASSIVE', 'sensor_version': '5.1.3', 'state': 'OPERATIVE_ON', 'health_status': {'cpu_load_avg_1_min': {'name': '', 'level': 'NORMAL', 'current_value': '37.3%'}, 'memory_usage': {'name': '', 'level': 'NORMAL', 'current_value': '41.31%'}, 'throughput': {'name': '', 'level': 'NORMAL', 'current_value': '936690.0 bps'}, 'dropped_packets': {'name': '', 'level': 'NORMAL', 'current_value': '0%'}, 'disk_usage': [{'name': '/', 'level': 'NORMAL', 'current_value': '62%'}, {'name': '/etc/timezone', 'level': 'NORMAL', 'current_value': '62%'}, {'name': '/opt/nids/state', 'level': 'NORMAL', 'current_value': '62%'}, {'name': '/usr/share/zoneinfo/America/New_York', 'level': 'NORMAL', 'current_value': '62%'}], 'net_if_status': [{'name': 'br-7e6edf1eff12', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'ens160', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'ens192', 'level': 'NORMAL', 'current_value': 'Not Running'}, {'name': 'veth04fa1ed', 'level': 'NORMAL', 'current_value': 'Not Running'}, {'name': 'veth624471b', 'level': 'NORMAL', 'current_value': 'Not Running'}, {'name': 'vethb1b3581', 'level': 'NORMAL', 'current_value': 'Not Running'}, {'name': 'vethc97d639', 'level': 'NORMAL', 'current_value': 'Running'}], 'license_status': {'name': '', 'level': 'NORMAL', 'current_value': 'VALID'}, 'services': []}, 'is_reversed_conn': True}, {'id': 5, 'name': 'Sensor 5.1', 'address': 'N/A', 'port': 0, 'type': 'PASSIVE', 'sensor_version': '5.1.2', 'state': 'DISCONNECTED', 'health_status': {'cpu_load_avg_1_min': {'name': '', 'level': '', 'current_value': ''}, 'memory_usage': {'name': '', 'level': '', 'current_value': ''}, 'throughput': {'name': '', 'level': '', 'current_value': ''}, 'dropped_packets': {'name': '', 'level': '', 'current_value': ''}, 'disk_usage': [], 'net_if_status': [], 'license_status': {'name': '', 'level': '', 'current_value': ''}, 'services': []}, 'is_reversed_conn': True}]}
# jsonResponse = [{'id': 4, 'name': 'Sensor 5.2', 'address': '', 'port': 0, 'type': 'PASSIVE', 'sensor_version': '5.2.1', 'state': 'OPERATIVE_ON', 'health_status': {'cpu_load_avg_1_min': {'name': '', 'level': 'NORMAL', 'current_value': '27.5%'}, 'memory_usage': {'name': '', 'level': 'NORMAL', 'current_value': '48.66%'}, 'throughput': {'name': '', 'level': 'NORMAL', 'current_value': '1936690.0 bps'}, 'dropped_packets': {'name': '', 'level': 'NORMAL', 'current_value': '0%'}, 'disk_usage': [{'name': '/', 'level': 'NORMAL', 'current_value': '72%'}, {'name': '/etc/timezone', 'level': 'NORMAL', 'current_value': '72%'}, {'name': '/opt/nids/state', 'level': 'NORMAL', 'current_value': '72%'}, {'name': '/usr/share/zoneinfo/Europe/Amsterdam', 'level': 'NORMAL', 'current_value': '72%'}], 'net_if_status': [{'name': 'br-7e6edf1eff12', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'ens160', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'ens192', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'veth04fa1ed', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'veth624471b', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'vethb1b3581', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'vethc97d639', 'level': 'NORMAL', 'current_value': 'Running'}], 'license_status': {'name': '', 'level': 'NORMAL', 'current_value': 'VALID'}, 'services': []}, 'is_reversed_conn': True}, {'id': 5, 'name': 'Sensor 5.1', 'address': 'N/A', 'port': 0, 'type': 'PASSIVE', 'sensor_version': '5.1.2', 'state': 'DISCONNECTED', 'health_status': {'cpu_load_avg_1_min': {'name': '', 'level': '', 'current_value': ''}, 'memory_usage': {'name': '', 'level': '', 'current_value': ''}, 'throughput': {'name': '', 'level': '', 'current_value': ''}, 'dropped_packets': {'name': '', 'level': '', 'current_value': ''}, 'disk_usage': [], 'net_if_status': [], 'license_status': {'name': '', 'level': '', 'current_value': ''}, 'services': []}, 'is_reversed_conn': True}]
# # response = requests.get(url, verify=False, auth=(user,password),timeout=10)
# # response.raise_for_status()
# access json content
# # jsonResponse = response.json()
# print("Entire JSON response")
# print(jsonResponse)
# # print("Response Type: ", type(jsonResponse))
print("Print each key-value pair from JSON response:")
for sensordata in jsonResponse['results']:
	#SENSORMEMUAGE = (sensordata['health_status']['memory_usage']['current_value'])
	#print(SENSORMEMUAGE)
    print("Sensor: \t", sensordata['name'])
    print("Version: \t", sensordata['sensor_version'])