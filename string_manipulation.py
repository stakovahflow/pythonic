#!/usr/bin/env python3
import sys 
import re
import string
verbosity=False
#verbosity=True

def StripSpaces(string):
	output = []

def SSHSession(HOSTNAME,USERNAME,PASSWORD,COMMAND):
	print(HOSTNAME,USERNAME,PASSWORD,COMMAND)
	print("Work in progress")

def CommaToArray(string):
	# Creat an array from a comma (,) separated string 
	output = list(string.split(","))
	return output

def StripSpecial(string):
	# Only allow alphanumeric & spaces (\s):
	pattern = "[^0-9a-zA-Z\s]+"
	output = re.sub(pattern, "", string)
	return output

def SearchLine(SearchFile,MatchString,x):
	output = []
	file = open(SearchFile)
	filecontents = file.readlines()
	#for MatchString in MatchStrings:
	MatchTerm = MatchString.strip()
	if verbosity == True:
		print("Searching for '%s' in file: %s" % (MatchString,SearchFile))
	for line in filecontents:
		if MatchTerm in line.strip():
			newline = re.sub("\s\s+",",", line.strip())
			if verbosity == True:
				print("String Match: %s" % (newline))
			matchArray=CommaToArray(newline)
			#output.append(StripSpecial(matchArray[x]))
			output = StripSpecial(matchArray[x])
	return output

def DeCoder(EncodedString):
	import base64
	output = base64.b64decode(EncodedString).decode('utf-8').strip()
	return output

def EnCoder(UnencodedString):
	import base64
	output = base64.encode(UnencodedString).decode('utf-8').strip()
	return output

def CSVParser(CSVFile):
	import csv 
	with open(CSVFile, newline='') as C:
		COUNT=0
		COLUMNS=[]
		CSVData = list(csv.reader(C))
		for CSVLine in CSVData:
			if COUNT == 0:
				COLUMNS.append(CSVLine)
				#print("Column Headers: ", COLUMNS)
				print("%s:\t%20s:\t%20s:\t%20s:\t%s:" % ("COUNT", "HOSTNAME", "PASSWORD", "CLEARTEXT", "COMMAND"))
			else:
				HOSTNAME = CSVLine[0]
				PASSWORD = DeCoder(CSVLine[1])
				CLEARTEXT = CSVLine[2]
				COMMAND = CSVLine[3]
				if verbosity == True:
					print("Hostname: %s" % (HOSTNAME))
					print("Encoded Password: %s" % (PASSWORD))
					print("Cleartext Password: %s" % (CLEARTEXT))
					print("Command: %s" % (COMMAND))
				print("%03d\t%20s\t%20s\t%20s\t%s" % (COUNT, HOSTNAME, PASSWORD, CLEARTEXT, COMMAND))
				#SSHSession(HOSTNAME,USERNAME,PASSWORD,COMMAND)
			COUNT+=1

SearchFile=sys.argv[1]
InputStrings=sys.argv[2]
x=int(sys.argv[3])
for InputString in CommaToArray(InputStrings):
	print('%s:\t%s' % (InputString,SearchLine(SearchFile,InputString,x)))
print("Complete.")

ParsedData = []
CSVParser('dummy.csv')