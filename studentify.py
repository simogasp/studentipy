#!/usr/bin/python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import sys, getopt, os, re, shutil
import argparse
from collections import namedtuple

langInfo = namedtuple('langInfo', 'name, extensions, token, startToken, endToken')
suppLang = [];
suppLang.append(langInfo('c/c++', ['.c','.cpp','.h','.hpp','.cc', '.cxx'],'//!!', '//<!!','//>!!'))
suppLang.append(langInfo('matlab', ['.m'],'\%\%!!', '\%\%<!!','\%\%>!!'))
suppLang.append(langInfo('javascript', ['.js'],'//!!', '//<!!','//>!!'))
suppLang.append(langInfo('python', ['.py'],'#!!', '#<!!','#>!!'))
suppLang.append(langInfo('java', ['.java'],'//!!', '//<!!','//>!!'))



def help(name):
    """ print the usage for the program
    """
    print('Usage:\n\t'+name+' -i <input file or dir> -o <output file or dir>')
    print("\nSupported languages:\nLanguage\t\ttoken\t\tstartToken\t\tendToken")
    for i in suppLang:
        print(i.name+"\t\t\t"+i.token+"\t\t"+i.startToken+"\t\t"+i.endToken)



def removeCode(inputfilename, outputfilename, token, startToken, endToken):
    """ create a copy of a file by removing the line of code ended by a comment containing the token
         inputfilename is the file to copy
         outputfilename is the destination file
         token is the commentary token to detect in order to remove the line    
    """

    if os.path.isfile(inputfilename):

        # any token without text in front, the token can be follow by text
        pattern = re.compile(r"[ \t]*" + token +".*[ \t]*$", re.UNICODE)
        # any tokenr without text in front, the token can be follow by text
        multiStart = re.compile(r'^[ \t]*'+startToken+'.*[ \t]*', re.UNICODE)
        # any token without text in front, the token can be follow by text
        multiEnd = re.compile(r'^[ \t]*'+endToken+'.*[ \t]*', re.UNICODE)
        # open the file
        with open(inputfilename) as fp:
            # create the new file
            dstfile = open(outputfilename,'w')

            # used to keep track of multiline 
            multi = False

            # parse line by line
            for line in fp:

                # if a start token has not been detected recently
                if not multi:

                    #try to detect a start token
                    s = multiStart.search(line)

                    if s == None:

                        # if the line do not match copy it to the destination file
                        r = pattern.search(line)
                        if r == None:
                            dstfile.write(line)
                        else:
                            dstfile.write('\n')

                    else:
                        print("Detected start token:"+line)
                        multi = True;
                        # do nothing
                else:

                    #try to detect a end token
                    s = multiEnd.search(line)

                    if s == None:
                        # do not copy the code and just add an empty line
                        dstfile.write('\n')
                    else:
                        # otherwise do nothing as we don't want to copy the line neither, 
                        # just add an empty line
                        multi = False
                        print("Detected end token:"+line)
                    # print line
            
            #close the files
            dstfile.close();



def parseDirectory(inputDir, outputDir):
    """ parse the input directory recursively and recreate the same repository
        in output parsing the files and removing the lines tagged with the proper token   
    """
    # create the output directory
    os.makedirs(outputDir)

    # list the elements in the input directory
    for dirname, dirnames, filenames in os.walk(inputDir):
        # print("\nDirectories in "+dirname)
        newbase = os.path.normpath(re.compile('^'+inputDir).sub(outputDir+os.sep,dirname))+os.sep
        # print newbase
        # print path to all subdirectories first.
        for subdirname in dirnames:
            # create the a copy of the directory
            os.makedirs(os.path.normpath(os.path.join(newbase, subdirname)))
            print(os.path.normpath(os.path.join(newbase, subdirname)))
        # print path to all filenames.
        # print("Filenames")
        for filename in filenames:
            # print os.path.normpath(os.path.join(newbase, filename))
            n, ext = os.path.splitext(filename)
            m = [x for x in suppLang if ext in x.extensions]
            if not m:
                print("No supported language found for file "+filename)
                shutil.copyfile(os.path.join(dirname, filename), os.path.normpath(os.path.join(newbase, filename)))
            else:
                # if it is a known language apply the transformation with the given token
                print("Detected "+m[0].name+" language for "+filename+"\tProcessing...")
                removeCode(os.path.join(dirname, filename), os.path.normpath(os.path.join(newbase, filename)), m[0].token, m[0].startToken, m[0].endToken)
            





if __name__ == "__main__":       

    parser = argparse.ArgumentParser(description='A simple script to generate theversion of a code to be given to the student.'+
                    'The script parses the input file and create a copy of it removing the lines tagged with a special comment tag.'+
                    'It automatically detects the language. More over it can be used on a directory to recursively create a copy of it parsing all the files in it.')
    parser.add_argument('-i', '--inputFile', required=True, help='The input file or directory to parse')
    parser.add_argument('-o', '--outputFile', required=True, help='The output file or directory')
    args = parser.parse_args()         

    # parse the input arguments
    inputfile = args.inputFile
    outputfile = args.outputFile

    os.path.normpath(inputfile)
    os.path.normpath(outputfile)
    # check the input arguments
    if inputfile == outputfile:
        print("Can't use the same file as input and output")
        sys.exit()

    print('Input is "', inputfile)
    print('Output is "', outputfile)

    # if it's a folder
    if os.path.isdir(inputfile):
        print("Parsing directory is not available (yet)")
        # check whether the outdir already exist
        if os.path.exists(outputfile):
            # if so ask the user what to do (delete or stop)
            answer = input("The output directory "+outputfile+" already exists. Do you want to remove it? [Y/n]: ")
            if answer.lower() in ["y", "yes"] or answer == "":
                shutil.rmtree(outputfile)
            else:
                print("Aborting...")
                sys.exit()
        parseDirectory(inputfile, outputfile) 

    # otherwise if it is a file
    elif os.path.isfile(inputfile):
        # get the extension
        base, ext = os.path.splitext(inputfile)
        m = [x for x in suppLang if ext in x.extensions]
        if not m:
            print("No supported language found for file "+inputfile)
            sys.exit()
        else:
            # if it is a known language apply the transformation with the given token
            print("Detected "+m[0].name+" language for "+inputfile+"\nProcessing...\n")
            removeCode(inputfile, outputfile, m[0].token, m[0].startToken, m[0].endToken)
    else:
        print('Cannot find the input folder/file!')