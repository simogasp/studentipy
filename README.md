# Studentipy

[![CodeQL](https://github.com/simogasp/studentipy/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/simogasp/studentipy/actions/workflows/github-code-scanning/codeql) [![Codacy Badge](https://app.codacy.com/project/badge/Grade/46add6ebc63a4d16b6893550da420387)](https://app.codacy.com/gh/simogasp/studentipy/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

## Introduction

A simple script to generate the version of a code to be given to the students.
The script parses the input files and folders and removes/comment the lines tagged
with a special comment tag.
It automatically detects the language.
Folders given in input are recursively parsed.

## Requirements

The script has been developed and tested using Python 3.

## Usage

```shell
studentify.py input [input ...] [-o OUTPUT]
```

The script will remove/comment/replace any line from the original input files
that ends with a particular comment tag.

In a C file, the usable tags are:

* Deleting tags: these tags remove the line(s) of code in the student version.
  * `//!!` : inline delete tag: this line will be removed
  * `//<!!` : start block delete tag: all lines will be removed until end tag
  * `//>!!` : end block delete tag: end the delete block

* Commenting tags: these tags comment out the line(s) of code in the student version.
  * `//??` : inline comment tag: this line will be commented
  * `//<??` : start block comment tag: all lines will be commented until end tag
  * `//>??` : end block comment tag: end the comment block

* Student tags:
  * `//::` : inline student tag: keep line in student mode but delete in clean mode
  * `//<::` : start block student tag
  * `//>::` : end block student tag

* Replacing tags: these tags replace the line(s) with alternative code in the student version.
  * `//++` : inline replacing tag: remove the code before the tag and replace it with what comes after the tag
  * `//<++` : start block replacing tag
  * `//>++` : end block replacing tag

In other supported languages, just change the `//` (C comment style)
by the comment of the language (`%` in matlab, `#` in python, ...).
The supported languages are:

| Language   | Comment symbol | deleting tag | commenting tag | student tag | replacing tag |
| ---------- | -----------    | ------------ | -------------- | ----------- | ------------- |
| c/c++      |    `//`        |    `//!!`    |    `//??`      |    `//::`   |    `//++`     |
| javascript |    `//`        |    `//!!`    |    `//??`      |    `//::`   |    `//++`     |
| java       |    `//`        |    `//!!`    |    `//??`      |    `//::`   |    `//++`     |
| matlab     |    `%`         |    `%!!`     |    `%??`       |    `%::`    |    `%++`      |
| python     |    `#`         |    `#!!`     |    `#??`       |    `#::`    |    `#++`      |

For example in the following piece of code:

```c
// example of deleting tag
normal line
inline delete //!!
normal line
start delete block //<!!
normal line
end delete block //>!!

// example of commenting tag
normal line
inline comment //??
normal line
start comment block //<??
normal line
end comment block //>??

// example of student tag
normal line
// inline student //::
normal line
// start student block //<::
normal line
// end student block //>::

// example of replacing tag
normal line
line that changes //++ line visible to student // why not a comment here
normal line
first line to change //<++ first
second line to change //++ second
third line to change  //++ third
fourth line to change //>++ fourth
```

will be transformed by the command `studentify.py the_c_file` into:

```c
// example of deleting tag
normal line

normal line




// example of commenting tag
normal line
// inline comment
normal line
// start comment block
// normal line
// end comment block

// example of student tag
normal line
// inline student
normal line
// start student block
normal line
// end student block

// example of replacing tag
normal line
line visible to student // why not a comment here
normal line
first
second
third
fourth
```

And by the command `studentify.py the_c_file --clean` into:

```c
// example of deleting tag
normal line
inline delete
normal line
start delete block
normal line
end delete block

// example of commenting tag
normal line
inline comment
normal line
start comment block
normal line
end comment block

// example of student tag
normal line

normal line




// example of replacing tag
normal line
line that changes
normal line
first line to change
second line to change
third line to change
fourth line to change
```

To have a complete list of the functionalities available,
just print the help of the command with:

```shell
studentify.py -h
```

## License

See [LICENSE](LICENSE) text file

## Authors

* Simone Gasparini
* Matthieu Pizenberg

## Contact

* Simone Gasparini <simone.gasparini@enseeiht.fr>
* Matthieu Pizenberg <matthieu.pizenberg@gmail.com>
