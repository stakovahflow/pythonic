#!/usr/bin/env python3
# Version:  0.01
# Author:   AT Sowell
# Modified: 2023-08-11
import os
import pexpect
import csv
#import getpass
import time
import argparse
import sys
from sys import argv
from pexpect import pxssh
import logging as log
from datetime import datetime
from os import get_terminal_size

verbosity = False
#debugging = False
loglevel = 0

WIDTH=(get_terminal_size()[0])-1
STARTTIME=datetime.now().strftime("%Y-%m-%d_%H%M%S")
LINE='-'*WIDTH
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

def logger(string):
	with open(LOGFILE,'ab') as f:
		f.write(('\r\n%s' % (string)).encode('utf-8'))
		if verbosity:
			print(string)

def SemicolonToArray(string):
	# Creat an array from a comma (,) separated string 
	output = list(string.split(";"))
	return output

def CommaToArray(string):
	# Creat an array from a comma (,) separated string 
	output = list(string.split(","))
	return output

def SSHSUDO(HOSTNAME,USERNAME,PASSWORD,COMMAND):
	commandoutput=[]
	try:
		with open(LOGFILE,'ab') as f:
			print("Attempting connection to %s via SSH" % (HOSTNAME))
			p = pxssh.pxssh(options={"StrictHostKeyChecking": "no","UserKnownHostsFile": "/dev/null"})
			p.force_password = True
			p.login(HOSTNAME, USERNAME, PASSWORD, auto_prompt_reset=False, terminal_type='ansi', original_prompt='[#$]', login_timeout=10)
			p.setecho(False)
			p.waitnoecho()
			p.logfile = None
			index = p.expect(['$', pexpect.EOF])
			LoginUser = '\[sudo\] password for %s:' % (USERNAME)
			#FailedUser = USERNAME+' is not in the sudoers file.  This incident will be reported.'
			if index == 0:
				time.sleep(0.5)
				p.sendline('sudo -s')
				p.logfile=f
				logger("Logged into: %s\n" %(HOSTNAME))
				index2 = p.expect([LoginUser,'[#]','[$]',pexpect.TIMEOUT,pexpect.EOF])
				if index2 == 0:
					logger("Logging in with sudo password\n")
					p.logfile = None
					p.sendline(PASSWORD)
					p.logfile = f
					index3 = p.expect(['[#]','[$]'])
					if index3 == 0:
						logger("SUDO access granted\n")
					elif index3 == 1:
						logger("Privilege escalagion failed. Exiting.\n")
						p.logfile = None
						p.sendline('\003')
						p.logfile = f
						p.sendline('exit')
						return('Failed!')
					else:
						logger("Unable to determine what happened. See error message for details.\n")
						return('Failed!')
				elif index2 == 1:
					logger("Logged in without sudo password\n")
				elif index2 == 2:
					p.sendline('\n\n\n')
					logger("Privilege escalagion failed. Exiting.\n")
					p.logout()
					return('Failed!')
				elif index2 == 3:
					logger("SUDO access timed out\n")
					return('Failed!')
				else:
					logger("Unable to determine the prompt")
					p.expect(["[#]","[$]"])
					return('Failed!')
				p.logfile = None
				p.sendline(COMMAND)
				p.logfile = f
				p.expect(["[#]","[$]"])
				output=p.after.decode('utf-8').splitlines()
				for line in output:
					commandoutput.append(line)
				p.logfile = None
				p.sendline("exit")
				p.expect("$")
				p.logout()
			else:
				logger("Cannot log into host: %s" %(HOSTNAME))
	except pxssh.ExceptionPxssh as e:
		logger("Error (PXSSH):")
		logger(str(e))
	except Exception as e:
		logger("Exception (General):")
		logger(str(e))
	if commandoutput == []:
		logger("No output")
		return('Failed!')
	else:
		logger("Command execution successful: '%s'" % (COMMAND))
		logger('Success!\n')
	logger(LINE)
	return('Success!')

# Password decoder:
def DeCoder(EncodedString):
	import base64
	output = base64.b64decode(EncodedString).decode('utf-8').strip()
	return output

# CSV Parser:
def CSVParser(CSVFile):
	if os.path.isfile(CSVFile):
		with open(CSVFile, 'r', encoding='utf-8') as C:
			CSVData = csv.reader(C)
			if verbosity:
				logger("Opened CSV: %s" % (CSVFile))
			COUNT=0
			CSVData = list(csv.reader(C))
			for CSVLine in CSVData:
				try:
					CMDCOUNT = 1
					if COUNT > 0:
						HOSTNAME = CSVLine[0]
						USERNAME = CSVLine[1]
						PASSWORD = DeCoder(CSVLine[2]).strip()
						COMMANDS = CSVLine[3]
						if debugging:
							logger("Hostname: %s" % (HOSTNAME))
							logger("Username: %s" % (USERNAME))
							logger("Commands: %s" % (SemicolonToArray(COMMANDS)))
						for COMMAND in SemicolonToArray(COMMANDS):
							logger("Command (%d): %s" % (CMDCOUNT, COMMAND))
							CMDCOUNT+=1
							STATUS=(SSHSUDO(HOSTNAME,USERNAME,PASSWORD,COMMAND))
							if STATUS == 'Failed!':
								logger('Remote system unavailable.\nSkipping...')
								break
							if verbosity:
								logger(STATUS)
					else:
						if verbosity:
							logger("Skipping header")
				except:
					continue
				COUNT+=1

try:
	logger(LINE)
	logger(STARTTIME)
	logger(LINE)
	# GET ARGUMENTS using ARGPARSE
	parser = argparse.ArgumentParser(description='\nAutomate commands on remote Linux hosts\n\
	\t\tEnjoy! -a', formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument("-f", "--file", type=str, dest="file", action="store", help="CSV filename")
	parser.add_argument("-v", "--verbose", help="Enable verbose output (may contain sensitive information)", action="store_true")
	parser.add_argument("-d", "--display", help="Display data from CSV file", action="store_true")
	parser.add_argument("-l", "--log", type=int, dest="log", help="Set logging level (disabled(0), debug(1))")

	# COLLECT ARGPARSE RESULTS
	results = args = parser.parse_args()

	# CHECK RESULTS
	if args.file:
		CSVFile=args.file
		if not os.path.isfile(CSVFile):
			logger("Unable to open file: %s" % (CSVFile))
			parser.print_help(sys.stderr)
			exit(0)
	else:
		logger("No CSV file specified (--file)")
		parser.print_help(sys.stderr)
		exit(0)
	if args.log:
		if args.log == 1:
			loglevel = 'DEBUG'
			debugging = True
		else:
			debugging = False
		logger("Log level set: %s" % (log))
		
	if args.verbose:
		verbosity = True
	if args.display:
		CSVParser(CSVFile)
	logger(LINE)
	logger("Completed")
	print("See logfile for more details: %s" % (LOGFILE))
except Exception as e:
	logger("An error occurred: ")
	logger(e)
logger(LINE)

