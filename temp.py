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

import string, random, sys, argparse
from argparse import RawTextHelpFormatter

typo = ''
counter = 0
line = '-' * 40

# GET ARGUMENTS using ARGPARSE
parser = argparse.ArgumentParser(description='\n Create a random password\n\
 Special characters, numbers, UPPERCASE -"Oscar",\n\
 and lowercase -"lima" to avoid confusion.\n\
 Default options (no arguments): -c 16 -a\n\
 \t\tEnjoy! --stakovahflow666@gmail.com', formatter_class=argparse.RawTextHelpFormatter)
# Timeout for commands
parser.add_argument("-t", "--timeout", type=int, dest="timeout", action="store", help="Timeout duration")
parser.add_argument("-a", "--all", help="same as -l -n -s -u", action="store_true")
parser.add_argument("-l", "--lower", help="include lowercase characters", action="store_true")
parser.add_argument("-n", "--number", help="include 0-9", action="store_true")
parser.add_argument("-s", "--special", help="include special characters", action="store_true")
parser.add_argument("-u", "--upper", help="include uppercase characters", action="store_true")
parser.add_argument("-p", "--license", help="print license and exit", action="store_true")

# COLLECT ARGPARSE RESULTS
results = args = parser.parse_args()

# CHECK RESULTS
# Check that a length was given.
# If not, gripe and exit.
try:
    timeout=int(args.timeout)
except:
    timeout=0.1
if timeout < 0:
    print ("Input error:\nCannot create a negative length password.\nExiting")
    exit (0)
# check character results and add to counter if
# selection is made.
if args.lower:
    typo = typo + 'l'
    counter = counter + 1
if args.number:
    typo = typo + 'n'
    counter = counter + 1
if args.special:
    typo = typo + 's'
    counter = counter + 1
if args.upper:
    typo = typo + 'u'
    counter = counter + 1
if args.all:
    typo = 'a'
if args.license:
    print (license)
    exit (0)



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
