# MEME
Meme Encoding Markup Expression - A grammar for generating memes.

The language spec can be found [here](./language_specs.md). </br>
This repository contains a references implementation of the compiler ([`src/console.py`](./src/console.py))

## Generating Memes
The simplest memes can be generated from relavtively simple strings consisting of an image specifier and some text fields.</br>
For example, `/M:drake/T:WYSIWYG/T:Entering weird crap into your console/` generates: ![](docs/example_drake.png)
The language also supports placing text at arbitary locations, changing text color, font size, etc:
`/M:drake/T:WYSIWYG/T:Entering weird crap into your console/T:Green Text;C:green;F:Arial:30/`
