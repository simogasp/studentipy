#!/usr/bin/python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import sys, getopt, os, re

def help(name):
    """ print the usage for the program
    """
    print('Usage:\n\t'+name+' -i <inputfile> -o <outputfile>')

def removeCode(inputfilename, outputfilename, token):
    """ create a copy of a file by removing the line of code ended by a comment containing the token
         inputfilename is the file to copy
         outputfilename is the destination file
         token is the commentary token to detect in order to remove the line    
    """

    if os.path.isfile(inputfilename):

        pattern = re.compile(ur'[ \t]*'+token+'.*[ \t]*$')
        # open the file
        with open(inputfilename) as fp:
            # create the new file
            dstfile = open(outputfilename,'w')
            # parse line by line
            for line in fp:
                # if the line do not match copy it to the destination file
                r = pattern.search(line)
                if r == None:
                    dstfile.write(line)
                else:
                    dstfile.write('\n')
                    print line
            
            #close the files
            dstfile.close();


                

# minimum arguments required
if len(sys.argv) != 5:
    help(sys.argv[0])
    sys.exit()

# parse the input arguments
inputfile = ''
outputfile = ''
try:
    opts, args = getopt.getopt(sys.argv[1:],"hi:o:",["ifile=","ofile="])
except getopt.GetoptError:
    print 'test.py -i <inputfile> -o <outputfile>'
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        help(sys.argv[0])
        sys.exit()
    elif opt in ("-i", "--ifile"):
        inputfile = arg
    elif opt in ("-o", "--ofile"):
        outputfile = arg

print 'Input file is "', inputfile
print 'Output file is "', outputfile

removeCode(inputfile, outputfile, '//!!')
