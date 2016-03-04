TP Tool(s)
===========================================

------------
Introduction
------------

A simple script to generate the version of a code to be given to the students.
The script parses the input files and folders and removes the lines tagged
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
The script will remove any line from the original input files
that ends with a particular comment tag.

Supported languages:

| Language   |   token   |   startToken   |   endToken   |
| ---------------- | ------------- | ------------- | ------------- |
| c/c++        |    `//!!`      |    `//<!!`      |    `//>!!`      |
| matlab       |    `%%!!`   |    `%%<!!`      |    `%%>!!`      |
| javascript   |    `//!!`      |    `//<!!`      |    `//>!!`      |
| python       |    `#!!`      |    `#<!!`      |    `#>!!`      |
| java           |    `//!!`      |    `//<!!`      |    `//>!!`      |

For example in the following piece of C code a total of 6 lines will be removed

```c
glBegin( GL_QUADS );
glTexCoord2f( 0, 1 );  //!! this line will be removed
glVertex2f( -1, -1 );  //!! even this one
glTexCoord2f( 0, 0 );  //!!
glVertex2f( -1, 1 );
glTexCoord2f( 1, 0 );
//<!! All these lines will be removed
glTexCoord2f( 1, 1 );
glVertex2f( 1, -1 );
glEnd( );
//>!! just until this one

// reset the projection matrix
glMatrixMode( GL_PROJECTION );
glPopMatrix( );
glMatrixMode( GL_MODELVIEW );
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
