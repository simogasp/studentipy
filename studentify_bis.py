#!/usr/bin/env python2

# check python version newer than 2.7
import sys
v = sys.version_info
assert v.major > 2 or (v.major == 2 and v.minor >= 7), "Minimal version required is 2.7"

# useful imports
import argparse, os, shutil
from functools import partial

def studentify_main(args):
    """ Studentify the files given in arguments.

        args is a namespace containing the following variables
            func: (function) this very function
            input: ([string]) the files/folder to studentify
            output: (None or string) the output file/folder

        we have 3 basic cases depending on the output variable:
        None   -> Modify files and/or folders in place
        file   -> Input must contain only one file
        folder -> Copy inputs in this folder
    """
    outPath = args.output
    inPaths = args.input

    if outPath == None:
        for i in inPaths:
            isFile = os.path.isfile(i)
            studentify_one(i, i, isFile)
    elif len(inPaths)==1:
        isFile = os.path.isfile(outPath) if os.path.exists(outPath) else os.path.isfile(inPaths[0])
        studentify_one(inPaths[0], outPath, isFile)
    else:
        studentify_multiple(inPaths, outPath)

def studentify_one(inputPath, outputPath, outputIsFile):
    inputPath = os.path.abspath(inputPath)
    outputPath = os.path.abspath(outputPath)
    # if we studentify in place
    if inputPath == outputPath:
        if os.path.isfile(inputPath):
            assert outputIsFile, outputPath + " is actually an existing file"
            print(inputPath + " -> " + inputPath)
            processFile(inputPath)
        if os.path.isdir(inputPath):
            assert not outputIsFile, outputPath + " is actually an existing directory"
            lst = os.listdir(inputPath)
            inputPaths = [os.path.join(inputPath, i) for i in lst]
            studentify_multiple(inputPaths, outputPath)
    # if the input is a file, it depends on if output is a file also
    elif os.path.isfile(inputPath):
        if outputIsFile:
            outputDir = os.path.dirname(outputPath)
            if not os.path.exists(outputDir):
                os.makedirs(outputDir)
            shutil.copy(inputPath, outputPath)
            print(inputPath + " -> " + outputPath)
            processFile(outputPath)
        else:
            outputFile = os.path.join(outputPath, os.path.basename(inputPath))
            studentify_one(inputPath, outputFile, True)
    # else the input is a folder
    else:
        assert not outputIsFile
        lst = os.listdir(inputPath)
        inputPaths = [os.path.join(inputPath, i) for i in lst]
        newOutputDir = os.path.join(outputPath, os.path.basename(inputPath))
        studentify_multiple(inputPaths, newOutputDir)

def studentify_multiple(inputPaths, outputDir):
    for i in inputPaths:
        studentify_one(i, outputDir, False)

def processFile(filePath):
    pass

# check that a path (file or folder) exists or not and return it
def checkPath(path, shouldExist):
    path = os.path.normpath(path)
    if shouldExist != os.path.exists(path):
        msg = "path " + ("does not" if shouldExist else "already") + " exist: " + path
        raise argparse.ArgumentTypeError(msg)
    return path

# arguments configuration
parser = argparse.ArgumentParser()
parser.set_defaults(func=studentify_main)
parser.add_argument('-v', '--version', action='version', version='2.0')
parser.add_argument('input', type=partial(checkPath, shouldExist=True), nargs='+',
        help='file or folder to studentify')
parser.add_argument('-o', '--output', type=partial(checkPath, shouldExist=False),
        help='output file or folder (if input is a folder or contains more than 1 file, this must be a folder)')

if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)
