# MEME
Meme Encoding Markup Expressions - A grammar for generating memes.

The full language spec can be found [here](./language_specs.md). </br>
This repository contains a references implementation of the compiler ([`src/console.py`](./src/console.py))

## Generating Memes
The simplest memes can be generated from relavtively simple strings consisting of an image specifier and some text fields.</br>
For example, `/M:drake/T:WYSIWYG/T:Entering weird crap into your console/` generates: ![](docs/example_drake.png)
The language also supports placing text at arbitary locations, changing text color, font size, etc:
`/M:drake/T:WYSIWYG/T:Entering weird crap into your console/T:Green Text;CL:green;F:Arial:30/`
![](docs/custom_drake.png)
It even handles memes with weird text positions for you, like with this pigeon meme:
`/M:pigeon/T:Me/T:Meme Encoding Markup Expressions/T:Is this turing complete?/` (we're pretty sure its not) ![](docs/pigeon_custom_text_fields.png)

## Thanks
Thank you to [Jace Browning](https://github.com/jacebrowning) for his [memegen](https://github.com/jacebrowning/memegen) website which inspired this project. Additionally, his code was a very helpful reference.</br>
Thank you to pillow for being great and defining much of our default behaviour through their well chosen defaults.<br>
Spongebob, for being an endless font of fantastic memes.
