#!/usr/bin/env python2

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# check python version newer than 2.7
import sys
v = sys.version_info
assert v.major > 2 or (v.major == 2 and v.minor >= 7), "Minimal version required is 2.7"

# useful imports
import argparse, os, shutil, tempfile
from functools import partial
from collections import namedtuple

langInfo = namedtuple('langInfo', 'name, extensions, commentSymbol, deleteTokens, commentTokens')
suppLang = [];
suppLang.append(langInfo('c/c++', ['.c','.cpp','.h','.hpp','.cc', '.cxx'],
    '//', ['//!!', '//<!!', '//>!!'], ['//!//', '//<!//', '//>!//']))
suppLang.append(langInfo('matlab', ['.m'],
    '%', ['%%!!', '%%<!!', '%%>!!'], ['%%!%%', '%%<!%%', '%%>!%%']))
suppLang.append(langInfo('javascript', ['.js'],
    '//', ['//!!', '//<!!', '//>!!'], ['//!//', '//<!//', '//>!//']))
suppLang.append(langInfo('python', ['.py'],
    '#', ['#!!', '#<!!', '#>!!'], ['#!#', '#<!#', '#>!#']))
suppLang.append(langInfo('java', ['.java'],
    '//', ['//!!', '//<!!', '//>!!'], ['//!//', '//<!//', '//>!//']))


def studentify_main(args):
    """ Studentify the files given in arguments.

        args is a namespace containing at least the following variables
            func: (function) this very function
            input: ([string]) the files/folder to studentify
            output: (None or string) the output file/folder

        all other variables in the namespace (for new features)
        are going to be stored en the "flags" dictionary.

        we have 3 basic cases depending on the output variable:
        None   -> Modify files and/or folders in place
        file   -> Input must contain only one file
        folder -> Copy inputs in this folder
    """
    outPath = args.output
    inPaths = args.input
    # flags is the dictionary containing all other flags
    flags = {k:v for k,v in args.__dict__.iteritems() if k not in ['func','input','output']}

    if outPath == None:
        if not flags['nobackup']:
            backupPath = os.path.abspath("studentify_backup")
            if flags['debug']: print("backing up files in: " + backupPath)
            os.makedirs(backupPath)
            for i in inPaths:
                if os.path.isfile(i):
                    shutil.copy(i, backupPath)
                else:
                    shutil.copytree(i, os.path.join(backupPath, os.path.basename(i)))
            if flags['debug']: print("backup done.")
            print("if you do not want backup, use the --nobackup flags")
        for i in inPaths:
            isFile = os.path.isfile(i)
            studentify_one(i, i, isFile, flags)
    elif len(inPaths)==1:
        isFile = os.path.isfile(outPath) if os.path.exists(outPath) else os.path.isfile(inPaths[0])
        studentify_one(inPaths[0], outPath, isFile, flags)
    else:
        studentify_multiple(inPaths, outPath, flags)

def studentify_one(inputPath, outputPath, outputIsFile, flags):
    inputPath = os.path.abspath(inputPath)
    outputPath = os.path.abspath(outputPath)
    # if we studentify in place
    if inputPath == outputPath:
        if os.path.isfile(inputPath):
            assert outputIsFile, outputPath + " is actually an existing file"
            if flags['debug']: print(inputPath + " -> " + inputPath)
            processFile(inputPath, flags)
        if os.path.isdir(inputPath):
            assert not outputIsFile, outputPath + " is actually an existing directory"
            lst = os.listdir(inputPath)
            inputPaths = [os.path.join(inputPath, i) for i in lst]
            studentify_multiple(inputPaths, outputPath, flags)
    # if the input is a file, it depends on if output is a file also
    elif os.path.isfile(inputPath):
        if outputIsFile:
            outputDir = os.path.dirname(outputPath)
            if not os.path.exists(outputDir):
                os.makedirs(outputDir)
            shutil.copy(inputPath, outputPath)
            if flags['debug']: print(inputPath + " -> " + outputPath)
            processFile(outputPath, flags)
        else:
            outputFile = os.path.join(outputPath, os.path.basename(inputPath))
            studentify_one(inputPath, outputFile, True, flags)
    # else the input is a folder
    else:
        assert not outputIsFile
        lst = os.listdir(inputPath)
        inputPaths = [os.path.join(inputPath, i) for i in lst]
        newOutputDir = os.path.join(outputPath, os.path.basename(inputPath))
        studentify_multiple(inputPaths, newOutputDir, flags)

def studentify_multiple(inputPaths, outputDir, flags):
    for i in inputPaths:
        studentify_one(i, outputDir, False, flags)

def processFile(filePath, flags):
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
        if flags['debug']: print("No supported language found for file " + filePath)
    else:
        lang = l[0]
        # open a temporary file
        with open(filePath, 'r+b') as f, tempfile.NamedTemporaryFile(delete=False) as ftemp:
            tempPath = ftemp.name
            inCommentBlock = False
            # process each line of the file
            for line in f:
                newLine, inCommentBlock = processLine(
                        line, lang, inCommentBlock,
                        flags)
                ftemp.write(newLine)
        # rename temp file into original
        shutil.copystat(filePath, tempPath)
        shutil.move(tempPath, filePath)

def processLine(line, lang, inCommentBlock, flags):
    """ Search for the tokens in the line.
    """
    newLine = line
    replacementLine = "\n" if not flags['remove'] else ""
    if inCommentBlock:
        newLine = replacementLine
        inCommentBlock = not lang.deleteTokens[2] in line
    else:
        inCommentBlock = lang.deleteTokens[1] in line
        tokenDetected = lang.deleteTokens[0] in line
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
parser.add_argument('-d', '--debug', action='store_true',
        help='activate debug mode')
parser.add_argument('--remove', action='store_true',
        help='remove lines instead of keeping empty lines')
parser.add_argument('--nobackup', action='store_true',
        help='do not create backup when studentifying in place')

if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)
    #flags = {k:v for k,v in args.__dict__.iteritems() if k not in ['func','input','output']}
    #print(flags)
