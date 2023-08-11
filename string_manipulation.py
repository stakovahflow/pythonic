#!/usr/bin/env python3
import sys 
import re
import string
verbosity=False
#verbosity=True

def StripSpaces(string):
    output = []
    
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

def CSVParser(CSVFile):
    import csv 
    with open(CSVFile, newline='') as C:
        CSVData = list(csv.reader(C))
        for CSVLine in CSVData:
            hostname = CSVLine[0]
            password = DeCoder(CSVLine[1])
            text = CSVLine[2]
            if verbosity == True:
                print("Hostname: %s" % (hostname))
                print("Encoded Password: %s" % (password))
                print("Cleartext Password: %s" % (text))
            print("%s:\t%s\t(%s)" % (hostname, password, text))
        return(password)

SearchFile=sys.argv[1]
InputStrings=sys.argv[2]
x=int(sys.argv[3])
for InputString in CommaToArray(InputStrings):
    print('%s:\t%s' % (InputString,SearchLine(SearchFile,InputString,x)))
print("Complete.")

ParsedData = []
for line in CSVParser('dummy.csv'):
    for ParsedData in line:
        print("CSV Output: %s" % (ParsedData))
