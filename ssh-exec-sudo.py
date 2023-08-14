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
debugging = False
loglevel = 0

def TIMESTAMP():
    return(datetime.now().strftime("%Y-%m-%d_%H%M%S"))
WIDTH=(get_terminal_size()[0])-1
STARTTIME=TIMESTAMP()
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

def logonly(string):
	with open(LOGFILE,'ab') as f:
		f.write(('\r\n%s' % (string)).encode('utf-8'))

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
	STATUS = 'Failed!'
	try:
		with open(LOGFILE,'ab') as f:
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
					logger("Attempting privilege escalation with password")
					p.logfile = None
					p.sendline(PASSWORD)
					p.logfile = f
					index3 = p.expect(['[#]','[$]'])
					if index3 == 0:
						logger("Privilege escalation granted\n")
					elif index3 == 1:
						logger("Privilege escalagion failed.")
						p.logfile = None
						p.sendline('\003')
						p.logfile = f
						p.sendline('exit')
						return(STATUS)
					else:
						logger("Unable to determine what happened. See error message for details.\n")
						return(STATUS)
				elif index2 == 1:
					logger("Privilege escalation without password")
				elif index2 == 2:
					p.sendline('\n\n\n')
					logger("Privilege escalagion failed. Exiting.\n")
					p.logout()
				elif index2 == 3:
					logger("SUDO access timed out\n")
					STATUS = 'Timeout'
				else:
					logger("Unable to determine the prompt")
					#p.expect(["[#]","[$]"])
					return('Undetermined')
				p.logfile = None
				p.sendline(COMMAND)
				p.logfile = f
				p.expect(["[#]","[$]"])
				p.logfile = None
				p.sendline("exit")
				p.expect("$")
				p.logout()
				p.logfile = f
				STATUS = 'Success!'
			else:
				logger("Cannot log into host: %s" %(HOSTNAME))
	except pxssh.ExceptionPxssh as e:
		logger("Error (PXSSH):")
		logger(str(e))
	except Exception as e:
		logger("Exception (General):")
		logger(str(e))
	return(STATUS)

# Password decoder:
def DeCoder(EncodedString):
	import base64
	output = base64.b64decode(EncodedString).decode('utf-8').strip()
	return output

# CSV Parser:
def CSVParser(CSVFile,Mode):
	if os.path.isfile(CSVFile):
		with open(CSVFile, 'r', encoding='utf-8') as C:
			CSVData = csv.reader(C)
			if verbosity:
				logger("Opened CSV: %s" % (CSVFile))
			COUNT=0
			CSVData = list(csv.reader(C))
			for CSVLine in CSVData:
				try:
					logger(LINE)
					CMDCOUNT = 0
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
							STATUS = 'Failed!'
							CMDCOUNT+=1
							COMMANDLOGSTRING = "Attempting to run the following command on '%s' via SSH: '%s'" % (HOSTNAME,COMMAND)
							with open(LOGFILE,'ab') as f:
								f.write(('\r\n%s' % (COMMANDLOGSTRING)).encode('utf-8'))
							print(COMMANDLOGSTRING)
							if Mode == True:
								logger("Dry run: (%d): %s" % (CMDCOUNT, COMMAND))
								STATUS = 'Success!'
							else:
								logger("Running command (%d):' %s'" % (CMDCOUNT, COMMAND))
								STATUS=(SSHSUDO(HOSTNAME,USERNAME,PASSWORD,COMMAND))
							if STATUS != 'Success!':
								logger('Unable to perform SSH/sudo tasks.\nSkipping...')
								break
							#f.write(('\r\n%s' % (STATUS)).encode('utf-8'))
							logonly("SSH access to %s status: %s" % (HOSTNAME, STATUS))
					else:
						if verbosity:
							logger("Skipping CSV file '%s' header" %(CSVFile))
				except:
					continue
				COUNT+=1

try:
	logger(LINE)
	logger("Start time: %s" % (TIMESTAMP()))
	logger(LINE)
	# GET ARGUMENTS using ARGPARSE
	parser = argparse.ArgumentParser(description='\nAutomate commands on remote Linux hosts\n\
	\t\tEnjoy! -a', formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument("-f", "--file", type=str, dest="file", action="store", help="CSV filename")
	parser.add_argument("-d", "--display", action="store_true", help="Display contents of CSV without running")
	parser.add_argument("--debug", action="store_true", help="Enable additional debug logging")
	parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output (may contain sensitive information)")

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
	if args.display:
		Mode = True
	else:
		Mode = False
	
	if args.debug:
		debugging = True
		logger("Log level set: %s" % (debugging))
	
	if args.verbose:
		verbosity = True
	
	CSVParser(CSVFile,Mode)
	
	logger(LINE)
	logger("Completed: %s" % (TIMESTAMP()))
	print("See logfile for more details: %s" % (LOGFILE))
except Exception as e:
	logger("An error occurred: ")
	logger(e)
logger(LINE)

