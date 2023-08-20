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
ScreenWidth = (get_terminal_size()[0]) - 1
StartTime = datetime.now().strftime("%Y-%m-%d_%H%M%S")
PrintLine = '-' * ScreenWidth
verbosity = False


def decoder(decodeinput):
	# Password decoder:
	import base64
	decodedoutput = base64.b64decode(decodeinput).decode('utf-8').strip()
	return decodedoutput


def encoder(encodeinput):
	# Password encoder:
	import base64
	encodedoutput = base64.b64encode(encodeinput.encode('utf-8'))
	return encodedoutput


def csvdisplay(csvfilename):
	# CSV Parser:
	if os.path.isfile(csvfilename):
		# with open(csvfilename, 'rb') as c:
		# with open(csvfilename, 'r', encoding='utf-8') as c:
		with open(csvfilename, 'r', newline='', encoding='utf-8') as f:
			print("Opened CSV: %s" % csvfilename)
			print("Data:")
			count = 0
			csvdatalist = list(csv.reader(f))
			for csvprintline in csvdatalist:
				if count == 0:
					print('%s, %s, %s, %s' % (csvprintline[0], csvprintline[1], csvprintline[2], csvprintline[3]))
				else:
					csvhostname = csvprintline[0].strip()
					csvusername = csvprintline[1].strip()
					csvpassword = csvprintline[2].strip()
					csvcommandlist = csvprintline[3].strip()
					if verbosity:
						print('%s, %s, %s, %s' % (csvhostname, csvusername, decoder(csvpassword), csvcommandlist))
					else:
						print('%s, %s, %s, %s' % (csvhostname, csvusername, csvpassword, csvcommandlist))
				count += 1


def csvwriter(csvfilename, csvhostname, csvusername, csvencodedstring, csvcommandlist):
	if not os.path.isfile(csvfilename):
		if verbosity:
			print("Creating new file: %s" % csvfile)
		with open(csvfilename, 'a', newline='', encoding='utf-8') as f:
			writer = csv.writer(f)
			header = ['Hostname:', 'Username:', 'Password:', 'Command(s):']
			writer.writerow(header)
		f.close()
	else:
		if verbosity:
			print("Appending existing file: %s" % csvfilename)
	with open(csvfile, 'a', encoding='utf-8') as f:
		writer = csv.writer(f)
		row = [csvhostname, csvusername, csvencodedstring, csvcommandlist]
		writer.writerow(row)
		f.close()


try:
	# GET ARGUMENTS using ARGPARSE
	parser = argparse.ArgumentParser(description='\n Create, append, or view a CSV file for use in automating commands sent to Linux hosts\n\t\tEnjoy! -a', formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument('-f', '--file', type=str, dest="file", action='store', help='CSV filename')
	parser.add_argument('-o', '--overwrite', help='Overwrite existing file', action="store_true")
	parser.add_argument('-v', '--verbose', help='Enable verbose output (may contain sensitive information)', action="store_true")
	parser.add_argument('-d', '--display', help='Display data from CSV file', action='store_true')
	parser.add_argument('-a', '--append', help='Append new entries to CSV file', action='store_true')
	parser.add_argument('-H', '--hostname', type=str, dest="hostname", action='store', help='Remote hostname')
	parser.add_argument('-U', '--username', type=str, dest="username", action='store', help='Remote username')
	parser.add_argument('-C', '--commands', type=str, dest="commands", action='store', help='Remote username')
	# COLLECT ARGPARSE RESULTS
	results = args = parser.parse_args()
	# CHECK RESULTS
	if args.file:
		csvfile = args.file
	else:
		print('No CSV file specified (--file)')
		parser.print_help(sys.stderr)
		exit(0)
	if args.overwrite:
		print('Deleting: %s' % csvfile)
		if os.path.isfile(csvfile):
			os.remove(csvfile)
		else:
			print("File does not exist: %s" % csvfile)
	if args.verbose:
		verbosity = True
	if args.display:
		csvdisplay(csvfile)
		exit(0)
	if args.append:
		# Get input from user:
		if args.hostname:
			hostname = args.hostname
		else:
			hostname = input('Host:     ')
		if args.username:
			username = args.username
		else:
			username = input('Username: ')
		if args.commands:
			commandlist = args.commands
		else:
			commandlist = input("Commands (Separated by ';'): \n")
		password = getpass.getpass(prompt='Password: ')
		encodedstring = encoder(password)
		decodedstring = decoder(encodedstring)
		if verbosity:
			print("Writing line to CSV: %s" % csvfile)
			print('Writing line to CSV \"%s\":\n\"%s\",\"%s\",\"%s\",\"%s\"' % (csvfile, hostname, username, encodedstring, commandlist))
		csvwriter(csvfile, hostname, username, encodedstring.decode('utf-8'), commandlist)
except KeyboardInterrupt:
	print('Cancelled by user')
except Exception as e:
	print('An exception occurred:')
	print(e)
