# MEME Specs and Language Standard

## A Meme Expression

A meme expression is formed from blocks. As of now there are three block hierarchies in the standard:

- C: Composite (this contains memes)
- M: Meme (denotes an image and its text)
- T: Text (a text block)

Scoping is C -> M -> T.

Formatting can be either included in a block or a block of its own. If it is its own block, it applies until the current scope is ended, if it is defined on the block, it applies throughout the scope.

<!-- TODO: Make the documentation self-hosting -->

For example, the following meme:

[![Horribly inefficiently created by WYSIWYG editor](hotline-bling-deprecated.jpg)]

Is properly encoded as:

```meme
/M:drake;FF:Helvetica/T<r1>:WYSIWYG/T<r2>:Handwritten Markup/
```

Where the termination of the M block is emplied by the end of the encoding.