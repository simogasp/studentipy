#!/usr/bin/env python2

# check python version newer than 2.7
import sys
v = sys.version_info
assert v.major > 2 or (v.major == 2 and v.minor >= 7), "Minimal version required is 2.7"

# useful imports
import argparse, os, shutil, tempfile
from functools import partial
from collections import namedtuple

langInfo = namedtuple('langInfo', 'name, extensions, token, startToken, endToken')
suppLang = [];
suppLang.append(langInfo('c/c++', ['.c','.cpp','.h','.hpp','.cc', '.cxx'],'//!!', '//<!!','//>!!'))
suppLang.append(langInfo('matlab', ['.m'],'%%!!', '%%<!!','%%>!!'))
suppLang.append(langInfo('javascript', ['.js'],'//!!', '//<!!','//>!!'))
suppLang.append(langInfo('python', ['.py'],'#!!', '#<!!','#>!!'))
suppLang.append(langInfo('java', ['.java'],'//!!', '//<!!','//>!!'))


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
    """ Process a file to remove lines containing some token.

    filePath must be an absolute path.

    1. Check if file is to be processed (matching filtypes in suppLang)
    2. Open a temporary file
    3. Process each line and write result in temporary file
    4. Rename temporary file into original file
    """
    assert os.path.isabs(filePath), "use an absolute path instead: " + filePath
    base, ext = os.path.splitext(filePath)
    l = [lang for lang in suppLang if ext in lang.extensions]
    if not l:
        print("No supported language found for file " + filePath)
    else:
        lang = l[0]
        # open a temporary file
        with open(filePath, 'r+b') as f, tempfile.NamedTemporaryFile(delete=False) as ftemp:
            tempPath = ftemp.name
            inCommentBlock = False
            # process each line of the file
            for line in f:
                newLine, inCommentBlock = processLine(
                        line, lang.token, lang.startToken, lang.endToken, inCommentBlock)
                ftemp.write(newLine)
        # rename temp file into original
        shutil.copystat(filePath, tempPath)
        shutil.move(tempPath, filePath)

def processLine(line, token, startToken, endToken, inCommentBlock):
    """ Search for the token in the line.
    """
    newLine = line
    replacementLine = "\n"
    if inCommentBlock:
        newLine = replacementLine
        inCommentBlock = not endToken in line
    else:
        inCommentBlock = startToken in line
        tokenDetected = token in line
        if inCommentBlock or tokenDetected:
            newLine = replacementLine
    return newLine, inCommentBlock

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
