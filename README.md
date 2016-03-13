TP Tool(s)
===========================================

------------
Introduction
------------

A simple script to generate the version of a code to be given to the students.
The script parses the input files and folders and removes/comment the lines tagged
with a special comment tag.
It automatically detects the language.
Folders given in input are recursively parsed.

--------
Requirements
--------

The script has been developed and tested using Python 2 (>=2.7).

--------
Usage
--------

```shell
studentify.py input [input ...] [-o OUTPUT]
```
The script will remove/comment any line from the original input files
that ends with a particular comment tag.

In a C file, the usable tags are:

* Deleting tags:
	* `//!!` : inline delete tag: this line will be removed
	* `//<!!` : start block delete tag: all lines will be removed until closing tag
	* `//>!!` : end block delete tag: end the delete block
* Commenting tags:
	* `//??` : inline comment tag: this line will be commented
	* `//<??` : start block comment tag: all lines will be commented until closing tag
	* `//>??` : end block comment tag: end the comment block
* Student tags:
	* `//::` : inline student tag: keep line in student mode but delete in clean mode
	* `//<::` : start block student tag
	* `//>::` : end block student tag

In other supported languages, just change the `//` (C comment style)
by the comment of the language (`%` in matlab, `#` in python, ...).
The supported languages are:

| Language   | Comment symbol | example with delete tag |
| ---------- | -----------    | ----------------------  |
| c/c++      |    `//`        |    `//!!`               |
| javascript |    `//`        |    `//!!`               |
| java       |    `//`        |    `//!!`               |
| matlab     |    `%`         |    `%!!`                |
| python     |    `#`         |    `#!!`                |

For example in the following piece of code:

```c
normal line
inline delete //!!
normal line
start delete block //<!!
normal line
end delete block //>!!

normal line
inline comment //??
normal line
start comment block //<??
normal line
end comment block //>??

normal line
// inline student //::
normal line
// start student block //<::
normal line
// end student block //>::
```

will be transformed by the command `studentify.py the_c_file` into:

```c
normal line

normal line




normal line
// inline comment
normal line
// start comment block
// normal line
// end comment block

normal line
// inline student
normal line
// start student block
normal line
// end student block
```

And by the command `studentify.py the_c_file --clean` into:

```c
normal line
inline delete
normal line
start delete block
normal line
end delete block

normal line
inline comment
normal line
start comment block
normal line
end comment block

normal line

normal line



```

To have a complete list of the functionalities available,
just print the help of the command with:

```shell
studentify.py -h
```

-------
License
-------

See [LICENSE](LICENSE) text file

-------
Authors
-------

* Simone Gasparini
* Matthieu Pizenberg


---------
Contact
---------

* Simone Gasparini simone.gasparini@enseeiht.fr
* Matthieu Pizenberg matthieu.pizenberg@gmail.com
