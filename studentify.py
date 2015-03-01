#!/usr/bin/python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import sys, getopt, os, re, shutil
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
        print(i.name+"\t\t\t"+i.token+"\t\t"+i.startToken)+"\t\t"+i.endToken



def removeCode(inputfilename, outputfilename, token, startToken, endToken):
    """ create a copy of a file by removing the line of code ended by a comment containing the token
         inputfilename is the file to copy
         outputfilename is the destination file
         token is the commentary token to detect in order to remove the line    
    """

    if os.path.isfile(inputfilename):

        # any toker without text in front, the token can be follow by text
        pattern = re.compile(ur'[ \t]*'+token+'.*[ \t]*$')
        # any toker without text in front, the token can be follow by text
        multiStart = re.compile(ur'^[ \t]*'+startToken+'.*[ \t]*')
        # any toker without text in front, the token can be follow by text
        multiEnd = re.compile(ur'^[ \t]*'+endToken+'.*[ \t]*')
        # open the file
        with open(inputfilename) as fp:
            # create the new file
            dstfile = open(outputfilename,'w')

            # used to keep track of multiline 
            multi = False

            # parse line by line
            for line in fp:

                # if a start token has not be detecte recently
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
                        # otherwise do nothing as we don't want to copy the line neither add an empty line
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
            print os.path.normpath(os.path.join(newbase, subdirname))
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

    # minimum arguments required
    if len(sys.argv) != 5:
        help(sys.argv[0])
        sys.exit()

    # parse the input arguments
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hi:o:",["ifile=","ofile=","help"])
    except getopt.GetoptError:
        print 'test.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == ('-h', '--help'):
            help(sys.argv[0])
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    os.path.normpath(inputfile)
    os.path.normpath(outputfile)
    # check the input arguments
    if inputfile == '' or outputfile == '':
        print('Missing argument(s)')
        help(sys.argv[0])
        sys.exit()
    elif inputfile == outputfile:
        print("Can't use the same file as input and output")
        help(sys.argv[0])
        sys.exit()

    print 'Input is "', inputfile
    print 'Output is "', outputfile

    # if it's a folder
    if os.path.isdir(inputfile):
        print("Parsing directory is not available (yet)")
        # check whether the outdir already exist
        if os.path.exists(outputfile):
            # if so ask the user what to do (delete or stop)
            answer = raw_input("The output directory "+outputfile+" already exists. Do you want to remove it? [Y/n]: ")
            if answer.lower() in ["y", "yes"] or answer == "":
                shutil.rmtree(outputfile)
            else:
                print("Aborting...")
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

