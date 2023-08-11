#!/usr/bin/env python3
import re
verbosity=False
def findline(searchfile,matchstrings):
	file = open(searchfile)
	filecontents = file.readlines()
	for matchstring in matchstrings:
		matchterm = matchstring.strip()
		if verbosity == True:
			print("Searching for '%s' in file: %s" % (matchstring,searchfile))
		for line in filecontents:
			if matchterm in line.strip():
				newline = re.sub("\s\s+",",", line.strip())
				
				print(newline)
matchstrings=['Pages free','Pages active']
searchfile='memtest.txt'
findline(searchfile,matchstrings)
