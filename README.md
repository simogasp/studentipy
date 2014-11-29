TP Tool(s)
===========================================

------------
Introduction
------------

A simple script to generate the version of a code to be given to the student. The script parses the input file and create a copy of it removing the lines tagged with a special comment tag. As yet, it only works with `C/C++` code, but soon enough...

--------
Usage
--------

```shell
studentify.py -i <inputfile> -o <outputfile>
```
The script will remove any line from the original input file that ends with a `C/C++` comment `//!!`, e.g.:

```c
    glBegin( GL_QUADS );
    glTexCoord2f( 0, 1 );  //!! this line will be removed
    glVertex2f( -1, -1 );    //!! even this one    
    glTexCoord2f( 0, 0 );   //!!   
    glVertex2f( -1, 1 );
    glTexCoord2f( 1, 0 );
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