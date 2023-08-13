#!/usr/bin/env python3
# Version:  0.01
# Author:   AT Sowell
# Modified: 2023-08-11
import os
import pexpect
import csv
import time
import argparse
import sys
from sys import argv
from pexpect import pxssh
import logging as log
import getpass
from datetime import datetime
from os import get_terminal_size
verbosity = False
loglevel = 'INFO'
WIDTH=(get_terminal_size()[0])-1
STARTTIME=datetime.now().strftime("%Y-%m-%d_%H%M%S")
LINE='-'*WIDTH
#LOGFILE=('ssh-exec-sudo-%s.log' %(STARTTIME))
LOGFILE=('ssh-exec-sudo.log')
# parse csv for:
# 	host
# 	username
# 	password (base64)
# 	commands
# open ssh session:
# verify connection
# run sudo
# verify sudo access
# run additional commands
# loop through all hosts


def SemicolonToArray(string):
	# Creat an array from a comma (,) separated string 
	output = list(string.split(";"))
	return output

def CommaToArray(string):
	# Creat an array from a comma (,) separated string 
	output = list(string.split(","))
	return output

def SSHSUDO(HOSTNAME,USERNAME,PASSWORD,COMMAND,LOGFILE):
	with open(LOGFILE,'ab') as f:
		commandoutput=[]
		try:
			print("Attempting connection to %s via SSH" % (HOSTNAME))
			p = pxssh.pxssh(options={"StrictHostKeyChecking": "no","UserKnownHostsFile": "/dev/null"})
			p.force_password = True
			p.login(HOSTNAME, USERNAME, PASSWORD, auto_prompt_reset=False, terminal_type='ansi', original_prompt='[#$]', login_timeout=10)
			p.waitnoecho()
			p.setecho(False)
			index = p.expect(['$', pexpect.EOF])
			if index == 0:
				p.sendline('sudo -s')
				print("Logged into: %s" %(HOSTNAME))
				f.write(("Logged into: %s\n" %(HOSTNAME)).encode('utf-8'))
				LoginUser = '\[sudo\] password for %s:' % (USERNAME)
				index2 = p.expect([LoginUser,'[#]',pexpect.EOF])
				if index2 == 0:
					print("Logged in with sudo password")
					f.write(('Logged in with sudo password\n').encode('utf-8'))
					p.sendline(PASSWORD)
					p.expect("[#]")
				elif index2 == 1:
					print("Logged in without sudo password")
					f.write(('Logged in without sudo password\n').encode('utf-8'))
				else:
					print("Unable to determine the prompt")
					f.write(('Unable to determine the prompt\n').encode('utf-8'))
				p.expect(["[#]","[$]"])
				p.logfile=f
				f.write(('Running: ',COMMAND,'\n').encode('utf-8'))
				p.sendline(COMMAND,encoding='utf-8')
				p.expect(["[#]","[$]"])
				output=p.after.splitlines()
				for line in output:
					commandoutput.append(line)
					print("OUTPUT: ", line)
					f.write((line,'\n').encode('utf-8'))
				p.sendline("exit")
				p.expect("$")
				p.logout()
			elif index == 1:
				print("Timed out.")
				f.write(('End of File received').encode('utf-8'))
			else:
				print("Cannot log into host: %s" %(HOSTNAME))
		except pxssh.ExceptionPxssh as e:
			f.write(("Error (PXSSH):\n").encode('utf-8'))
			f.write(((e),'\n').encode('utf-8'))
			print("Error:")
			print(str(e))
		except Exception as e:
			f.write(("Error (General):\n").encode('utf-8'))
			f.write(((e),'\n').encode('utf-8'))
			print("Exception:")
			print(str(e))
		if commandoutput == []:
			print("No output")
			f.write(("No output\n").encode('utf-8'))
			return('Failed!')
		else:
			print("Command execution successful %s" % (COMMAND))
		return('Success!')

# Password decoder:
def DeCoder(EncodedString):
	import base64
	output = base64.b64decode(EncodedString).decode('utf-8').strip()
	return output

# CSV Parser:
def CSVParser(CSVFile,LOGFILE):
	with open(LOGFILE,'ab') as f:
		if os.path.isfile(CSVFile):
			with open(CSVFile, 'r', encoding='utf-8') as C:
				CSVData = csv.reader(C)
				if verbosity:
					print("Opened CSV: %s" % (CSVFile))
					print("Data:")
				COUNT=0
				CSVData = list(csv.reader(C))
				for CSVLine in CSVData:
					try:
						print(CSVLine)
						CMDCOUNT = 0
						if COUNT > 0:
							HOSTNAME = CSVLine[0]
							USERNAME = CSVLine[1]
							PASSWORD = DeCoder(CSVLine[2]).strip()
							COMMANDS = CSVLine[3]
							if verbosity == True:
								print("Hostname: %s" % (HOSTNAME))
								print("Username: %s" % (USERNAME))
								print("Encoded Password: %s" % (PASSWORD))
								print("Command: %s" % (COMMANDS))
							for COMMAND in SemicolonToArray(COMMANDS):
								print("Command: %s" % (COMMAND))
								CMDCOUNT=CMDCOUNT+1
								STATUS=(SSHSUDO(HOSTNAME,USERNAME,PASSWORD,COMMAND,f))
								if STATUS == 'Failed!':
									print('Remote system unavailable.\nSkipping...')
									f.write(('Remote system unavailable.\nSkipping...\n'))
									break
								if verbosity:
									print(STATUS)
						else:
							if verbosity:
								print("Skipping header")
					except:
						continue
					COUNT+=1

with open(LOGFILE,'ab') as f:
	f.write((LINE+'\n').encode('utf-8'))
	f.write((STARTTIME+'\n').encode('utf-8'))
	f.write((LINE+'\n').encode('utf-8'))
	try:
		# GET ARGUMENTS using ARGPARSE
		parser = argparse.ArgumentParser(description='\nAutomate commands on remote Linux hosts\n\
		\t\tEnjoy! -a', formatter_class=argparse.RawTextHelpFormatter)
		parser.add_argument("-f", "--file", type=str, dest="file", action="store", help="CSV filename")
		parser.add_argument("-v", "--verbose", help="Enable verbose output (may contain sensitive information)", action="store_true")
		parser.add_argument("-d", "--display", help="Display data from CSV file", action="store_true")
		parser.add_argument("-l", "--log", help="Set logging level (disabled(0), debug(1), info(2), warning(3), error(4), critical(5))")

		# COLLECT ARGPARSE RESULTS
		results = args = parser.parse_args()

		# CHECK RESULTS
		if args.file:
			CSVFile=args.file
			if not os.path.isfile(CSVFile):
				print("Unable to open file: %s" % (CSVFile))
				parser.print_help(sys.stderr)
				exit(0)
		else:
			print("No CSV file specified (--file)")
			parser.print_help(sys.stderr)
			exit(0)
		if args.verbose:
			verbosity = True
		if args.display:
			CSVParser(CSVFile,LOGFILE)

		print("Completed")
		#print("See logfile for more details: %s" % (LOGFILE))
	except Exception as e:
		print("An error occurred: ")
		print(e)


