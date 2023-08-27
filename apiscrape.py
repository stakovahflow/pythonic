#!/usr/bin/env python3
from ipaddress import ip_address
import requests, os, sys, json, ssl, time, argparse, csv, getpass, subprocess
from re import search
from collections import OrderedDict
from datetime import date
from requests.packages.urllib3.exceptions import InsecureRequestWarning
t = time.localtime()
current_time = time.strftime('%H-%M-%S', t)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
today = date.today()
itl_modules = []
jsonResponse = {'total_count': 2, 'results': [{'id': 4, 'name': 'Sensor 5.2', 'address': '', 'port': 0, 'type': 'PASSIVE', 'sensor_version': '5.2.1', 'state': 'OPERATIVE_ON', 'health_status': {'cpu_load_avg_1_min': {'name': '', 'level': 'NORMAL', 'current_value': '27.5%'}, 'memory_usage': {'name': '', 'level': 'NORMAL', 'current_value': '48.66%'}, 'throughput': {'name': '', 'level': 'NORMAL', 'current_value': '1936690.0 bps'}, 'dropped_packets': {'name': '', 'level': 'NORMAL', 'current_value': '0%'}, 'disk_usage': [{'name': '/', 'level': 'NORMAL', 'current_value': '72%'}, {'name': '/etc/timezone', 'level': 'NORMAL', 'current_value': '72%'}, {'name': '/opt/nids/state', 'level': 'NORMAL', 'current_value': '72%'}, {'name': '/usr/share/zoneinfo/Europe/Amsterdam', 'level': 'NORMAL', 'current_value': '72%'}], 'net_if_status': [{'name': 'br-7e6edf1eff12', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'ens160', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'ens192', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'veth04fa1ed', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'veth624471b', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'vethb1b3581', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'vethc97d639', 'level': 'NORMAL', 'current_value': 'Running'}], 'license_status': {'name': '', 'level': 'NORMAL', 'current_value': 'VALID'}, 'services': []}, 'is_reversed_conn': True}, {'id': 6, 'name': 'Sensor 5.1.3', 'address': '', 'port': 0, 'type': 'PASSIVE', 'sensor_version': '5.1.3', 'state': 'OPERATIVE_ON', 'health_status': {'cpu_load_avg_1_min': {'name': '', 'level': 'NORMAL', 'current_value': '37.3%'}, 'memory_usage': {'name': '', 'level': 'NORMAL', 'current_value': '41.31%'}, 'throughput': {'name': '', 'level': 'NORMAL', 'current_value': '936690.0 bps'}, 'dropped_packets': {'name': '', 'level': 'NORMAL', 'current_value': '0%'}, 'disk_usage': [{'name': '/', 'level': 'NORMAL', 'current_value': '62%'}, {'name': '/etc/timezone', 'level': 'NORMAL', 'current_value': '62%'}, {'name': '/opt/nids/state', 'level': 'NORMAL', 'current_value': '62%'}, {'name': '/usr/share/zoneinfo/America/New_York', 'level': 'NORMAL', 'current_value': '62%'}], 'net_if_status': [{'name': 'br-7e6edf1eff12', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'ens160', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'ens192', 'level': 'NORMAL', 'current_value': 'Not Running'}, {'name': 'veth04fa1ed', 'level': 'NORMAL', 'current_value': 'Not Running'}, {'name': 'veth624471b', 'level': 'NORMAL', 'current_value': 'Not Running'}, {'name': 'vethb1b3581', 'level': 'NORMAL', 'current_value': 'Not Running'}, {'name': 'vethc97d639', 'level': 'NORMAL', 'current_value': 'Running'}], 'license_status': {'name': '', 'level': 'NORMAL', 'current_value': 'VALID'}, 'services': []}, 'is_reversed_conn': True}, {'id': 5, 'name': 'Sensor 5.1', 'address': 'N/A', 'port': 0, 'type': 'PASSIVE', 'sensor_version': '5.1.2', 'state': 'DISCONNECTED', 'health_status': {'cpu_load_avg_1_min': {'name': '', 'level': '', 'current_value': ''}, 'memory_usage': {'name': '', 'level': '', 'current_value': ''}, 'throughput': {'name': '', 'level': '', 'current_value': ''}, 'dropped_packets': {'name': '', 'level': '', 'current_value': ''}, 'disk_usage': [], 'net_if_status': [], 'license_status': {'name': '', 'level': '', 'current_value': ''}, 'services': []}, 'is_reversed_conn': True}]}
#jsonResponse = {'total_count': 2, 'results': [{'id': 4, 'name': 'Sensor 5.2', 'address': '', 'port': 0, 'type': 'PASSIVE', 'sensor_version': '5.2.1', 'state': 'OPERATIVE_ON', 'health_status': {'cpu_load_avg_1_min': {'name': '', 'level': 'NORMAL', 'current_value': '27.5%'}, 'memory_usage': {'name': '', 'level': 'NORMAL', 'current_value': '48.66%'}, 'throughput': {'name': '', 'level': 'NORMAL', 'current_value': '1936690.0 bps'}, 'dropped_packets': {'name': '', 'level': 'NORMAL', 'current_value': '0%'}, 'disk_usage': [{'name': '/', 'level': 'NORMAL', 'current_value': '72%'}, {'name': '/etc/timezone', 'level': 'NORMAL', 'current_value': '72%'}, {'name': '/opt/nids/state', 'level': 'NORMAL', 'current_value': '72%'}, {'name': '/usr/share/zoneinfo/Europe/Amsterdam', 'level': 'NORMAL', 'current_value': '72%'}], 'net_if_status': [{'name': 'br-7e6edf1eff12', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'ens160', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'ens192', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'veth04fa1ed', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'veth624471b', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'vethb1b3581', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'vethc97d639', 'level': 'NORMAL', 'current_value': 'Running'}], 'license_status': {'name': '', 'level': 'NORMAL', 'current_value': 'VALID'}, 'services': []}, 'is_reversed_conn': True}, {'id': 5, 'name': 'Sensor 5.1', 'address': 'N/A', 'port': 0, 'type': 'PASSIVE', 'sensor_version': '5.1.2', 'state': 'DISCONNECTED', 'health_status': {'cpu_load_avg_1_min': {'name': '', 'level': '', 'current_value': ''}, 'memory_usage': {'name': '', 'level': '', 'current_value': ''}, 'throughput': {'name': '', 'level': '', 'current_value': ''}, 'dropped_packets': {'name': '', 'level': '', 'current_value': ''}, 'disk_usage': [], 'net_if_status': [], 'license_status': {'name': '', 'level': '', 'current_value': ''}, 'services': []}, 'is_reversed_conn': True}]}
#jsonResponse = [{'id': 4, 'name': 'Sensor 5.2', 'address': '', 'port': 0, 'type': 'PASSIVE', 'sensor_version': '5.2.1', 'state': 'OPERATIVE_ON', 'health_status': {'cpu_load_avg_1_min': {'name': '', 'level': 'NORMAL', 'current_value': '27.5%'}, 'memory_usage': {'name': '', 'level': 'NORMAL', 'current_value': '48.66%'}, 'throughput': {'name': '', 'level': 'NORMAL', 'current_value': '1936690.0 bps'}, 'dropped_packets': {'name': '', 'level': 'NORMAL', 'current_value': '0%'}, 'disk_usage': [{'name': '/', 'level': 'NORMAL', 'current_value': '72%'}, {'name': '/etc/timezone', 'level': 'NORMAL', 'current_value': '72%'}, {'name': '/opt/nids/state', 'level': 'NORMAL', 'current_value': '72%'}, {'name': '/usr/share/zoneinfo/Europe/Amsterdam', 'level': 'NORMAL', 'current_value': '72%'}], 'net_if_status': [{'name': 'br-7e6edf1eff12', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'ens160', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'ens192', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'veth04fa1ed', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'veth624471b', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'vethb1b3581', 'level': 'NORMAL', 'current_value': 'Running'}, {'name': 'vethc97d639', 'level': 'NORMAL', 'current_value': 'Running'}], 'license_status': {'name': '', 'level': 'NORMAL', 'current_value': 'VALID'}, 'services': []}, 'is_reversed_conn': True}, {'id': 5, 'name': 'Sensor 5.1', 'address': 'N/A', 'port': 0, 'type': 'PASSIVE', 'sensor_version': '5.1.2', 'state': 'DISCONNECTED', 'health_status': {'cpu_load_avg_1_min': {'name': '', 'level': '', 'current_value': ''}, 'memory_usage': {'name': '', 'level': '', 'current_value': ''}, 'throughput': {'name': '', 'level': '', 'current_value': ''}, 'dropped_packets': {'name': '', 'level': '', 'current_value': ''}, 'disk_usage': [], 'net_if_status': [], 'license_status': {'name': '', 'level': '', 'current_value': ''}, 'services': []}, 'is_reversed_conn': True}]
for sensordata in jsonResponse['results']:
	try:
		SENSORNAME=(sensordata['name']).strip()
	except:
		SENSORNAME=""
	try:
		SENSORID=(sensordata['id']).strip()
	except:
		SENSORID=""
	try:
		SENSORADDR=(sensordata['address']).strip()
	except:
		SENSORADDR=""
	try:
		SENSORVER=(sensordata['sensor_version']).strip()
	except:
		SENSORVER=""
	try:
		SENSORTYPE=(sensordata['type']).strip()
	except:
		SENSORTYPE=""
	try:
		SENSORPORT=(sensordata['port']).strip()
	except:
		SENSORPORT=""
	try:
		SENSORSTATE=(sensordata['state']).strip()
	except:
		SENSORSTATE=""
	try:
		SENSORCPULOAD=(sensordata['health_status']['cpu_load_avg_1_min']['level']).strip()
	except:
		SENSORCPULOAD=""
	try:
		SENSORCPUPERCENT=(sensordata['health_status']['cpu_load_avg_1_min']['current_value']).strip()
	except:
		SENSORCPUPERCENT=""
	try:
		SENSORMEMLEVEL=(sensordata['health_status']['memory_usage']['level']).strip()
	except:
		SENSORMEMLEVEL=""
	try:
		SENSORMEMUAGE=(sensordata['health_status']['memory_usage']['current_value']).strip()
	except:
		SENSORMEMUAGE=""
	try:
		SENSORTHRULEVEL=(sensordata['health_status']['throughput']['level']).strip()
	except:
		SENSORTHRULEVEL=""
	try:
		SENSORTHRUVALUE=(sensordata['health_status']['throughput']['current_value']).strip()
	except:
		SENSORTHRUVALUE=""
	try:
		DROPPEDPKTLEVEL=(sensordata['health_status']['dropped_packets']['level']).strip()
	except:
		DROPPEDPKTLEVEL=""
	try:
		DROPPEDPKTVALUE=(sensordata['health_status']['dropped_packets']['current_value']).strip()
	except:
		DROPPEDPKTVALUE=""

zoneinfo=[]
nidsstate=[]
licensing=[]
reversedconn=[]
print(SENSORMEMUAGE, SENSORNAME, SENSORID, SENSORADDR, SENSORVER, SENSORTYPE, SENSORPORT, SENSORSTATE, SENSORCPULOAD, SENSORCPUPERCENT, SENSORMEMLEVEL, SENSORMEMUAGE, SENSORTHRULEVEL, SENSORTHRUVALUE, DROPPEDPKTLEVEL, DROPPEDPKTVALUE)
"""
for disk in (sensordata['health_status']['disk_usage']):
	rootspace=[]
	nidsstate=[]
	zoneinfo=[]
	try:
		if disk['name']=='/':
			try:
				rootspace.append(disk['name'])
			except:
				rootspace.append("")
			try:
				rootspace.append(disk['level'])
			except:
				rootspace.append("")
			try:
				rootspace.append(disk['current_value'])
			except:
				rootspace.append("")
	except Exception as e:
		print('Exception occurred: %s' % (e))
	for rootattribute in rootspace:
		print(rootattribute)
	try:
		if search ('/usr/share/zoneinfo',disk['name']):
			try:
				print(disk['name'])
			except:
				print("")
	except Exception as e:
		print('Exception occurred: %s' % (e))
	for zoneattribute in zoneinfo:
		print(zoneattribute)
	try:
		if search ('/opt/nids/state',disk['name']):
			nidsstate.append(disk['level'])
		for nidsattribute in nidsstate:
			print(nidsattribute)
	except Exception as e:
		print('Exception occurred: %s' % (e))
	try:
		for iface in (sensordata['health_status']['net_if_status']):
			try:
				interfaces.append(iface['name'])
			except:
				interfaces.append("")
			try:
				intstatus.append(iface['level'])
			except:
				intstatus.append("")
			try:
				intvalue.append(iface['current_value'])
			except:
				intvalue.append("")
	except Exception as e:
		print('Exception occurred: %s' % (e))

SENSORMEMUAGE, SENSORNAME, SENSORID, SENSORADDR, SENSORVER, SENSORTYPE, SENSORPORT, SENSORSTATE, SENSORCPULOAD, SENSORCPUPERCENT, SENSORMEMLEVEL, SENSORMEMUAGE, SENSORTHRULEVEL, SENSORTHRUVALUE, DROPPEDPKTLEVEL, DROPPEDPKTVALUE
"""