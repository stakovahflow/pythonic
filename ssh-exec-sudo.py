#!/usr/bin/env python3
# Version:  0.01
# Author:   AT Sowell
# Modified: 2023-08-18

##########################################################################
# Description
# parse user-defined CSV for:
# 	host (IP)
# 	username
# 	password (base64-encoded)
# 	commands
# Loop through all hosts:
# 	Open SSH session to each host:
# 		Verify connection
# 		Run sudo
# 		Verify sudo access
# 		Run additional commands
# 
##########################################################################

import os
import pexpect
import csv
import time
import argparse
import sys
from sys import argv
from pexpect import pxssh
import logging as log
from datetime import datetime
from os import get_terminal_size

def TimeStamp():
	return(datetime.now().strftime("%Y-%m-%d_%H%M%S"))

def logger(string):
	with open(LogFile,'ab') as f:
		f.write(('\r\n%s' % (string)).encode('utf-8'))
		if verbosity:
			print(string)

def logonly(string):
	with open(LogFile,'ab') as f:
		f.write(('\r\n%s' % (string)).encode('utf-8'))

def SemicolonToArray(string):
	# Creat an array from a comma (,) separated string 
	output = list(string.split(";"))
	return output

def SSHsudo(HostName,UserName,PassWord,Command):
	commandoutput=[]
	ReturnStatus = 'Failed!'
	try:
		with open(LogFile,'ab') as f:
			p = pxssh.pxssh(options={"StrictHostKeyChecking": "no","UserKnownHostsFile": "/dev/null"})
			p.force_password = True
			p.login(HostName, UserName, PassWord, auto_prompt_reset=False, terminal_type='ansi', original_prompt='[#$]', login_timeout=10)
			p.setecho(False)
			p.waitnoecho()
			p.logfile = None
			index = p.expect(['$', pexpect.EOF])
			LoginUser = '\[sudo\] password for %s:' % (UserName)
			if index == 0:
				time.sleep(0.5)
				p.sendline('sudo -s')
				p.logfile=f
				logger("Logged into: %s\n" %(HostName))
				index2 = p.expect([LoginUser,'[#]','[$]',pexpect.TIMEOUT,pexpect.EOF])
				if index2 == 0:
					logger("Attempting privilege escalation with password")
					p.logfile = None
					p.sendline(PassWord)
					p.logfile = f
					index3 = p.expect(['[#]','[$]'])
					if index3 == 0:
						logger("Privilege escalation granted\n")
					elif index3 == 1:
						logger("Privilege escalagion failed.\n")
						p.logfile = None
						p.sendline('\003')
						p.logfile = f
						p.sendline('exit')
						return(ReturnStatus)
					else:
						logger("Unable to determine what happened. See error message for details.\n")
						return(ReturnStatus)
				elif index2 == 1:
					logger("Privilege escalation without password")
				elif index2 == 2:
					p.sendline('\n\n\n')
					logger("Privilege escalagion failed. Exiting.\n")
					p.logout()
				elif index2 == 3:
					logger("SUDO access timed out\n")
					ReturnStatus = 'Timeout'
				else:
					logger("Unable to determine the prompt")
					#p.expect(["[#]","[$]"])
					return('Undetermined')
				p.logfile = None
				p.sendline(Command)
				p.logfile = f
				p.expect(["[#]","[$]"])
				p.logfile = None
				p.sendline("exit")
				p.expect("$")
				p.logout()
				p.logfile = f
				ReturnStatus = 'Success!'
			else:
				logger("Cannot log into host: %s" %(HostName))
	except pxssh.ExceptionPxssh as e:
		logger("Error (PXSSH):")
		logger(str(e))
	except Exception as e:
		logger("Exception (General):")
		logger(str(e))
	return(ReturnStatus)

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
			Count=0
			CSVData = list(csv.reader(C))
			for CSVLine in CSVData:
				try:
					logger(PrintLine)
					CmdCount = 0
					if Count > 0:
						HostName = CSVLine[0]
						UserName = CSVLine[1]
						PassWord = DeCoder(CSVLine[2]).strip()
						CommandList = CSVLine[3]
						if debugging:
							logger("Hostname: %s" % (HostName))
							logger("Username: %s" % (UserName))
							logger("Commands: %s" % (SemicolonToArray(CommandList)))
						for Command in SemicolonToArray(CommandList):
							ReturnStatus = 'Failed!'
							CmdCount+=1
							CommandLogString = "Attempting to run the following command on '%s' via SSH: '%s'" % (HostName,Command)
							with open(LogFile,'ab') as f:
								f.write(('\r\n%s' % (CommandLogString)).encode('utf-8'))
							print(CommandLogString)
							if Mode == True:
								logger("Dry run: (%d): %s" % (CmdCount, Command))
								ReturnStatus = 'Success!'
							else:
								logger("Running command (%d):' %s'" % (CmdCount, Command))
								ReturnStatus=(SSHsudo(HostName,UserName,PassWord,Command))
							if ReturnStatus != 'Success!':
								logger('Unable to perform SSH/sudo tasks.\nSkipping...')
								break
							#f.write(('\r\n%s' % (ReturnStatus)).encode('utf-8'))
							logonly("SSH access to %s status: %s" % (HostName, ReturnStatus))
					else:
						if verbosity:
							logger("Skipping CSV file '%s' header" %(CSVFile))
				except:
					continue
				Count+=1
def main():
	try:
		logger(PrintLine)
		logger("Start time: %s" % (TimeStamp()))
		logger(PrintLine)
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
		
		logger(PrintLine)
		logger("Completed: %s" % (TimeStamp()))
		print("See logfile for more details: %s" % (LogFile))
	except Exception as e:
		logger("An error occurred: ")
		logger(e)
	logger(PrintLine)

# Set global variables:
verbosity = False
debugging = False
loglevel = 0
ScreenWidth=(get_terminal_size()[0])-1
StartTime=TimeStamp()
PrintLine='-'*ScreenWidth
LogFile=('ssh-exec-sudo.log')

# Kick off main():
main()