#!/usr/bin/env python3
# Version:  0.01.01
# Author:   AT Sowell
# Modified: 2023-08-18

##########################################################################
# Description
# Create user-defined CSV containing:
# 	host (IP)
# 	username
# 	password (base64-encoded)
# 	commands
import os
import csv
import argparse
import getpass
import sys
from datetime import datetime
from os import get_terminal_size


# Setting Global Variables:
ScreenWidth=(get_terminal_size()[0])-1
StartTime=datetime.now().strftime("%Y-%m-%d_%H%M%S")
PrintLine='-'*ScreenWidth
verbosity=False

def DeCoder(EncodedString):
	# Password decoder:
	import base64
	output = base64.b64decode(EncodedString).decode('utf-8').strip()
	return output

def EnCoder(UnencodedString):
	# Password encoder:
	import base64
	output = base64.b64encode(UnencodedString.encode('utf-8'))
	return output

def CSVParser(CSVFile):
	# CSV Parser:
	if os.path.isfile(CSVFile):
		with open(CSVFile, 'r', encoding='utf-8') as C:
			CSVData = csv.reader(C)
			print("Opened CSV: %s" % (CSVFile))
			print("Data:")
			Count=0
			CSVData = list(csv.reader(C))
			for CSVPrintLine in CSVData:
				if Count > 0:
					HostName = CSVPrintLine[0]
					UserName = CSVPrintLine[1]
					PassWord = DeCoder(CSVPrintLine[2]).strip()
					CommandList = CSVPrintLine[3]
					if verbosity:
						print("HostName: %s" % (HostName))
						print("UserName: %s" % (UserName))
						print("Encoded Password: %s" % (PassWord))
						print("Command: %s" % (CommandList))
				Count+=1

def CSVWriter(CSVFile,HostName,UserName,EncodedString,CommandList):
	if not os.path.isfile(CSVFile):
		if verbosity:
			print("Appending existing file: %s" % (CSVFile))
		with open(CSVFile, 'a', encoding='UTF8') as f:
			writer = csv.writer(f)
			header = ['HostName','UserName','PassWord','CommandList']
			row = [HostName,UserName,EncodedString,CommandList]
			writer.writerow(header)
			writer.writerow(row)
			f.close()
	else:
		if verbosity:
			print("Creating new file: %s" % (CSVFile))
		with open(CSVFile, 'a', encoding='UTF8') as f:
			writer = csv.writer(f)
			row = [HostName,UserName,EncodedString,CommandList]
			writer.writerow(row)
			f.close()

try:
	# GET ARGUMENTS using ARGPARSE
	parser = argparse.ArgumentParser(description='\n Create, append, or view\n\
	 a CSV file for use in automating commands sent to Linux hosts\n\
	 \t\tEnjoy! -a', formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument("-f", "--file", type=str, dest="file", action="store", help="CSV filename")
	parser.add_argument("-v", "--verbose", help="Enable verbose output (may contain sensitive information)", action="store_true")
	parser.add_argument("-d", "--display", help="Display data from CSV file", action="store_true")
	parser.add_argument("-a", "--append", help="Append new entries to CSV file", action="store_true")

	# COLLECT ARGPARSE RESULTS
	results = args = parser.parse_args()

	# CHECK RESULTS
	if args.file:
		CSVFile=args.file
	else:
		print("No CSV file specified (--file)")
		parser.print_help(sys.stderr)
		exit(0)
	if args.verbose:
		verbosity = True
	if args.display:
		CSVParser(CSVFile)
	if args.append:
		# Get input from user:
		HostName = input("HostName: ")
		UserName = input("UserName: ")
		PassWord = getpass.getpass(prompt="Password: ")
		EncodedString = EnCoder(PassWord)
		DECODED = DeCoder(EncodedString)
		CommandList = input("Commands (Separated by ';'): \n")
		CSVWriter(CSVFile,HostName,UserName,EncodedString.decode('utf-8'),CommandList)
		if verbosity:
			print('Writing line to CSV "%s"\n"%s","%s","%s","%s"' % (CSVFile, HostName, UserName, EncodedString.decode(), CommandList))
except KeyboardInterrupt:
	print('User cancelled process')
except Exception as e:
	print('An exception occurred:')
	print(e)