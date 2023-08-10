#!/usr/bin/env python3
# Version:  0.01
# Author:   AT Sowell
# Modified: 2023-08-09

import os
import pexpect
import re
import time
from pexpect import pxssh
import logging as log
import sys
from sys import argv
import getpass
from datetime import datetime
from os import get_terminal_size

WIDTH=(get_terminal_size()[0])-1
STARTTIME=datetime.now().strftime("%Y-%m-%d_%H%M%S")
LINE='-'*WIDTH
LOGFILE=('./tmp/sensor-restart-docker-%s.log' %(STARTTIME))
USERNAME='silentdefense'
USERPASS=getpass.getpass("Sensor Silentdefense Password: ")
HOSTFILE=argv[1]
print("Hosts File: %s" % (HOSTFILE))
hostlist=open(HOSTFILE,'r')
print("Kick it!\n")

COMMANDS=['docker-compose -f /opt/nids-docker/config/nids-compose.yml restart','docker ps | grep nids-main']

with open(HOSTFILE) as H:
	HOSTS=H.readlines()
	with open(LOGFILE,'ab') as f:
		print("Started: %s" % (STARTTIME))
		f.write(('Started: %s\n' % (STARTTIME)).encode('utf-8'))
		f.write((LINE+'\n').encode('utf-8'))
		def SSHSUDO(ip,user,password,command):
			commandoutput=[]
			try:
				print("Attempting connection to %s via SSH" % (ip))
				p = pxssh.pxssh(options={"StrictHostKeyChecking": "no","UserKnownHostsFile": "/dev/null"})
				p.force_password = True
				p.login(ip, user, password, auto_prompt_reset=False, terminal_type='ansi', original_prompt='[#$]', login_timeout=10)
				p.waitnoecho()
				p.setecho(False)
				index = p.expect(['$', pexpect.EOF])
				if index == 0:
					p.sendline('sudo -s')
					print("Logged into: %s" %(ip))
					f.write(("Logged into: %s\n" %(ip)).encode('utf-8'))
					index2 = p.expect(['\[sudo\] password for silentdefense:','[#]',pexpect.EOF])
					if index2 == 0:
						print("Logging in with sudo password")
						f.write(("Logging in with sudo password\n").encode('utf-8'))
						p.sendline(password)
						p.expect("[#]")
					elif index2 == 1:
						print("Logging in without sudo password")
						f.write(("Logging in without sudo password\n").encode('utf-8'))
					else:
						print("Unable to determine the prompt")
						f.write(("Unable to determine the prompt\n").encode('utf-8'))
						p.expect("[#]")
					p.logfile=f
					p.sendline(command)
					p.expect("[#]")
					output=p.after.decode('utf-8').splitlines()
					for line in output:
						commandoutput.append(line)
					p.sendline("exit")
					p.expect("$")
					p.sendline("exit")
					#p.logout()
					#print("Success!")
					#f.write(("Success!\n").encode('utf-8'))
				else:
					print("Cannot log into host: %s" %(ip))
					f.write(("Cannot log into host: %s\n" %(ip)).encode('utf-8'))
			except Exception as e:
				print(str(e))
			except pxssh.ExceptionPxssh as e:
				print("Error")
				print(str(e))
			if commandoutput == []:
				print("No output")
				f.write(("No output\n").encode('utf-8'))
				return('Failed!')
			else:
				print("Command execution success! (%s)" % (COMMAND))
				f.write(("Command execution success! (%s)\n" % (COMMAND)).encode('utf-8'))
			return('Success!')
		for HOST in HOSTS:
			SENSOR=HOST.strip()
			count=1
			PRESSON=True
			print(LINE)
			f.write((LINE+'\n').encode('utf-8'))
			print('HOST: %s' % (SENSOR))
			f.write(('HOST: %s\n' % (SENSOR)).encode('utf-8'))
			for COMMAND in COMMANDS:
				count=count+1
				if(SSHSUDO(SENSOR,USERNAME,USERPASS,COMMAND) == 'Failed!'):
					print('Sensor unavailable.\nSkipping...')
					f.write(('Sensor unavailable.\nSkipping...\n').encode('utf-8'))
					break

			time.sleep(1)
		print(LINE)
		f.write((LINE+'\n').encode('utf-8'))
		STOPTIME=datetime.now().strftime("%Y-%m-%d_%H%M%S")
		print("Completed: %s" % (STOPTIME))
		f.write(('Completed: %s\n' % (STOPTIME)).encode('utf-8'))
		f.write((LINE+'\n').encode('utf-8'))

print("Completed")
print("See logfile for more details: %s" % (LOGFILE))
