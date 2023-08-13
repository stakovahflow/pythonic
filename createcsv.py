#!/usr/bin/env python3
import sys
import os
import getpass
import csv
import argparse
from datetime import datetime
from os import get_terminal_size

# Setting Global Variables:
WIDTH=(get_terminal_size()[0])-1
STARTTIME=datetime.now().strftime("%Y-%m-%d_%H%M%S")
LINE='-'*WIDTH
verbosity=False

# Password decoder:
def DeCoder(EncodedString):
	import base64
	output = base64.b64decode(EncodedString).decode('utf-8').strip()
	return output

# Password encoder:
def EnCoder(UnencodedString):
	import base64
	output = base64.b64encode(UnencodedString.encode('utf-8'))
	return output

# CSV Parser:
def CSVParser(CSVFile):
	if os.path.isfile(CSVFile):
		with open(CSVFile, 'r', encoding='utf-8') as C:
			CSVData = csv.reader(C)
			print("Opened CSV: %s" % (CSVFile))
			print("Data:")
			COUNT=0
			CSVData = list(csv.reader(C))
			for CSVLine in CSVData:
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
				COUNT+=1

def CSVWriter(CSVFile,HOSTNAME,USERNAME,ENCODED,COMMANDS):
	if not os.path.isfile(CSVFile):
		if verbosity:
			print("Appending existing file: %s" % (CSVFile))
		with open(CSVFile, 'a', encoding='UTF8') as f:
			writer = csv.writer(f)
			header = ['HOSTNAME','USERNAME','PASSWORD','COMMANDS']
			row = [HOSTNAME,USERNAME,ENCODED,COMMANDS]
			writer.writerow(header)
			writer.writerow(row)
			f.close()
	else:
		if verbosity:
			print("Creating new file: %s" % (CSVFile))
		with open(CSVFile, 'a', encoding='UTF8') as f:
			writer = csv.writer(f)
			row = [HOSTNAME,USERNAME,ENCODED,COMMANDS]
			writer.writerow(row)
			f.close()

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
	#if not os.path.isfile(CSVFile):
	#	print("Unable to open file: %s" % (CSVFile))
	#	parser.print_help(sys.stderr)
	#	exit(0)
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
	HOSTNAME = input("Hostname: ")
	USERNAME = input("Username: ")
	PASSWORD = getpass.getpass(prompt="Password: ")
	ENCODED = EnCoder(PASSWORD)
	DECODED = DeCoder(ENCODED)
	COMMANDS = input("Commands (Separated by ';'): \n")
	CSVWriter(CSVFile,HOSTNAME,USERNAME,ENCODED.decode('utf-8'),COMMANDS)
	if verbosity == True:
		print(HOSTNAME)
		print(USERNAME)
		print(ENCODED)
