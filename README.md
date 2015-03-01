TP Tool(s)
===========================================

------------
Introduction
------------

A simple script to generate the version of a code to be given to the student. The script parses the input file and create a copy of it removing the lines tagged with a special comment tag. It automatically detects the language. More over it can be used on a directory to recursively create a copy of it parsing all the files in it.

--------
Requirements
--------

The script has been developed and tested using Python 2.7.3. It has been tested on Python 3.x yet, in any case using the `2to3` tool the script can be eseasily ported to recent versions of Python.

--------
Usage
--------

```shell
python studentify.py -i <input[file,directory]> -o <output[file,directory]>
```
The script will remove any line from the original input file(s) that ends with a particular comment tag.

Supported languages:

| Language   |   token   |   startToken   |   endToken   |
| ---------------- | ------------- | ------------- | ------------- |
| c/c++        |    `//!!`      |    `//<!!`      |    `//>!!`      |
| matlab       |    `%%!!`   |    `%%<!!`      |    `%%>!!`      |
| javascript   |    `//!!`      |    `//<!!`      |    `//>!!`      |
| python       |    `#!!`      |    `#<!!`      |    `#>!!`      |
| java           |    `//!!`      |    `//<!!`      |    `//>!!`      |

For example in the following piece of C code the three lines will be removed

```c
    glBegin( GL_QUADS );
    glTexCoord2f( 0, 1 );  //!! this line will be removed
    glVertex2f( -1, -1 );    //!! even this one    
    glTexCoord2f( 0, 0 );   //!!   
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

Simone Gasparini


---------
Contact
---------

Simone Gasparini simone.gasparini@enseeiht.fr