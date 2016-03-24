#!/usr/bin/env python2

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

""" Studentify code for practical work.
"""

# pylint configuration
# pylint: disable=bad-whitespace, line-too-long, multiple-imports, multiple-statements

# useful imports
from __future__ import print_function
import sys, argparse, os, shutil, tempfile
from functools import partial
from collections import namedtuple

# check python version newer than 2.7
V = sys.version_info
assert V.major > 2 or (V.major == 2 and V.minor >= 7), "Minimal version required is 2.7"

TOKEN_TYPES = {'delete':'!!', 'comment':'??', 'student':'::'}
LangInfo = namedtuple('LangInfo', 'name, extensions, comment_symbol, tokens')
SUPP_LANG = [
    LangInfo('c/c++', ['.c', '.cpp', '.h', '.hpp', '.cc', '.cxx'], '//', {}),
    LangInfo('matlab', ['.m'], '%', {}),
    LangInfo('javascript', ['.js'], '//', {}),
    LangInfo('python', ['.py'], '#', {}),
    LangInfo('java', ['.java'], '//', {})]

# generate tokens for one language
def generate_tokens(comment_symbol, types):
    """ Generate all types of tokens for one comment symbol.
    """
    return {k:[
        comment_symbol + v,       # inline token
        comment_symbol + '<' + v, # start block token
        comment_symbol + '>' + v  # end block token
        ] for k, v in types.items()}

# generate tokens of all languages
TEMP = list(SUPP_LANG)
SUPP_LANG = [LangInfo(l.name, l.extensions, l.comment_symbol,
                      generate_tokens(l.comment_symbol, TOKEN_TYPES)) for l in TEMP]


def studentify_main(arguments):
    """ Studentify the files given in arguments.

        arguments is a namespace containing at least the following variables
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
    out_path = arguments.output
    in_paths = arguments.input
    # flags is the dictionary containing all other flags
    flags = {k:v for k, v in arguments.__dict__.items() if k not in ['func', 'input', 'output']}

    if out_path is None:
        if not flags['noBackup']:
            backup_path = os.path.abspath("studentify_backup")
            if flags['debug']: print("backing up files in: " + backup_path)
            os.makedirs(backup_path)
            for i in in_paths:
                if os.path.isfile(i):
                    shutil.copy(i, backup_path)
                else:
                    shutil.copytree(i, os.path.join(backup_path, os.path.basename(i)))
            if flags['debug']: print("backup done.")
            print("if you do not want backup, use the --noBackup flags")
        for i in in_paths:
            is_file = os.path.isfile(i)
            studentify_one(i, i, is_file, flags)
    elif len(in_paths) == 1:
        is_file = os.path.isfile(out_path) if os.path.exists(out_path) else os.path.isfile(in_paths[0])
        studentify_one(in_paths[0], out_path, is_file, flags)
    else:
        studentify_multiple(in_paths, out_path, flags)

def studentify_one(input_path, output_path, output_is_file, flags):
    """ Studentify the only file or folder given in input_path.
    """
    input_path = os.path.abspath(input_path)
    output_path = os.path.abspath(output_path)
    # if we studentify in place
    if input_path == output_path:
        if os.path.isfile(input_path):
            assert output_is_file, output_path + " is actually an existing file"
            if flags['debug']: print(input_path + " -> " + input_path)
            process_file(input_path, flags)
        if os.path.isdir(input_path):
            assert not output_is_file, output_path + " is actually an existing directory"
            lst = os.listdir(input_path)
            input_paths = [os.path.join(input_path, i) for i in lst]
            studentify_multiple(input_paths, output_path, flags)
    # if the input is a file, it depends on if output is a file also
    elif os.path.isfile(input_path):
        if output_is_file:
            output_dir = os.path.dirname(output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            shutil.copy(input_path, output_path)
            if flags['debug']: print(input_path + " -> " + output_path)
            process_file(output_path, flags)
        else:
            output_file = os.path.join(output_path, os.path.basename(input_path))
            studentify_one(input_path, output_file, True, flags)
    # else the input is a folder
    else:
        assert not output_is_file
        lst = os.listdir(input_path)
        input_paths = [os.path.join(input_path, i) for i in lst]
        newoutput_dir = os.path.join(output_path, os.path.basename(input_path))
        studentify_multiple(input_paths, newoutput_dir, flags)

def studentify_multiple(input_paths, output_dir, flags):
    """ Studentify every input given in argument to the output directory.
    """
    for i in input_paths:
        studentify_one(i, output_dir, False, flags)

def process_file(file_path, flags):
    """ Process a file to remove lines containing some token.

    file_path must be an absolute path.

    1. Check if file is to be processed (matching filtypes in SUPP_LANG)
    2. Open a temporary file
    3. Process each line and write result in temporary file
    4. Rename temporary file into original file
    """
    assert os.path.isabs(file_path), "use an absolute path instead: " + file_path
    dummy_base, ext = os.path.splitext(file_path)
    file_lang = [lang for lang in SUPP_LANG if ext in lang.extensions]
    if not file_lang:
        if flags['debug']: print("No supported language found for file " + file_path)
    else:
        lang = file_lang[0]
        # open a temporary file
        with open(file_path, 'r+b') as original_file, tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
            in_delete_block = False
            in_comment_block = False
            in_student_block = False
            # process each line of the file
            for line in original_file:
                new_line, in_delete_block, in_comment_block, in_student_block = process_line(
                    line, lang, in_delete_block, in_comment_block, in_student_block,
                    flags)
                temp_file.write(new_line)
        # rename temp file into original
        shutil.copystat(file_path, temp_path)
        shutil.move(temp_path, file_path)

def process_line(line, lang, in_delete_block, in_comment_block, in_student_block, flags):
    """ Search for the tokens in the line.
    """
    replacementLine = "\n" if not flags['noBlankLine'] else ""
    deleteLine = partial(replaceLine, replacementLine)
    clean = flags['clean']

    # process a potential delete block structure
    tokens = lang.tokens['delete']
    f_inline      = partial(removeEnd, tokens[0]) if clean else deleteLine
    f_start_block = partial(removeEnd, tokens[1]) if clean else deleteLine
    f_in_block    = identity                      if clean else deleteLine
    f_end_block   = partial(removeEnd, tokens[2]) if clean else deleteLine
    new_line, in_delete_block, modified = processBlockStructure(
        line, in_delete_block, tokens,
        f_inline, f_start_block, f_in_block, f_end_block)

    # process a potential comment bloc structure
    if not modified:
        tokens = lang.tokens['comment']
        comment_symbol = lang.comment_symbol
        f_inline      = partial(removeEnd, tokens[0]) if clean else partial(addStartAndRemoveEnd, comment_symbol, tokens[0])
        f_start_block = partial(removeEnd, tokens[1]) if clean else partial(addStartAndRemoveEnd, comment_symbol, tokens[1])
        f_in_block    = identity                      if clean else partial(addStart, comment_symbol)
        f_end_block   = partial(removeEnd, tokens[2]) if clean else partial(addStartAndRemoveEnd, comment_symbol, tokens[2])
        new_line, in_comment_block, modified = processBlockStructure(
            line, in_comment_block, tokens,
            f_inline, f_start_block, f_in_block, f_end_block)

    # process a potential student bloc structure
    if not modified:
        tokens = lang.tokens['student']
        f_inline      = deleteLine if clean else partial(removeEnd, tokens[0])
        f_start_block = deleteLine if clean else partial(removeEnd, tokens[1])
        f_in_block    = deleteLine if clean else identity
        f_end_block   = deleteLine if clean else partial(removeEnd, tokens[2])
        new_line, in_student_block, modified = processBlockStructure(
            line, in_student_block, tokens,
            f_inline, f_start_block, f_in_block, f_end_block)

    return new_line, in_delete_block, in_comment_block, in_student_block


# a generic function to process a line in a block structure (delete, comment, student, ...)
def processBlockStructure(
        line,         # the line to be processed
        in_block,      # global knowledge if current line is inside a block
        tokens,       # the tokens to detect [inlineToken, startToken, endToken]
        f_inline,     # function transforming the line in inlineToken is detected
        f_start_block, # function transforming the line at the start of a block
        f_in_block,    # function transforming the line inside a block
        f_end_block):  # function transforming the line at the end of a block
        # -> new_line, in_block, modified

    inline = tokens[0] in line
    start_block = tokens[1] in line
    end_block = tokens[2] in line
    modified = True
    new_line = line

    if in_block:
        if end_block:
            new_line = f_end_block(line)
            in_block = False
        else:
            new_line = f_in_block(line)
    elif start_block:
        new_line = f_start_block(line)
        in_block = True
    elif inline:
        new_line = f_inline(line)
    else:
        modified = False

    return new_line, in_block, modified

def replaceLine(replacement, line):
    return replacement

# remove the end of a line, starting at some detected token
def removeEnd(token, line):
    return line.split(token)[0].rstrip() + '\n'

# add the token at the start of the line with a space
def addStart(token, line):
    return token + ' ' + line

def addStartAndRemoveEnd(startToken, endToken, line):
    return addStart(startToken, removeEnd(endToken, line))

# a function the compose multiple functions
def compose(*functions):
    return functools.reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)

# identity function
def identity(x):
    return x

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
parser.add_argument('--noBlankLine', action='store_true',
                    help='remove lines instead of keeping empty lines')
parser.add_argument('--noBackup', action='store_true',
                    help='do not create backup when studentifying in place')
parser.add_argument('--clean', action='store_true',
                    help='create clean version of the file')

if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)
    #flags = {k:v for k,v in args.__dict__.items() if k not in ['func','input','output']}
    #print(flags)
