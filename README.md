
pandoc-eqnos
=============

*pandoc-eqnos* is a [pandoc] filter for numbering equations and equation references.

Demonstration: Using [`demo.md`] as input gives output files in [pdf], [tex], [html], [epub], [md] and other formats.

This version of pandoc-eqnos was tested using pandoc 1.14.0.1.

See also: [pandoc-fignos]

[pandoc]: http://pandoc.org/
[`demo.md`]: https://raw.githubusercontent.com/tomduck/pandoc-eqnos/master/demos/demo.md
[pdf]: https://raw.githubusercontent.com/tomduck/pandoc-eqnos/master/demos/out/demo.pdf
[tex]: https://raw.githubusercontent.com/tomduck/pandoc-eqnos/master/demos/out/demo.tex
[html]: https://rawgit.com/tomduck/pandoc-eqnos/master/demos/out/demo.html
[epub]: https://raw.githubusercontent.com/tomduck/pandoc-eqnos/master/demos/out/demo.epub
[md]: https://github.com/tomduck/pandoc-eqnos/blob/master/demos/out/demo.md
[pandoc-fignos]: https://github.com/tomduck/pandoc-fignos


Contents
--------

 1. [Rationale](#rationale)
 2. [Markdown Syntax](#markdown-syntax)
 3. [Usage](#usage)
 4. [Details](#details)
 5. [Installation](#installation)


Rationale
---------

Equation numbers and references are required for academic writing, but are not currently supported by pandoc.  It is anticipated that this will eventually change.  Pandoc-eqnos is a transitional package for those who need equation numbers and references now.

The syntax for equation numbers and references was worked out in [pandoc issue #813].  It seems likely that this will be close to what pandoc ultimately adopts.

By doing one thing -- and one thing only -- my hope is that pandoc-eqnos will permit a relatively painless switch when pandoc provides native support for equation numbers and references.

Installation of the filter is straight-forward, with minimal dependencies.  It is simple to use and has been tested extensively.

[pandoc issue #813]: https://github.com/jgm/pandoc/issues/813


Markdown Syntax
---------------

To tag an equation with the label `eq:description`, use

    $$ y = mx + b $$ {#eq:description}

The prefix `#eq:` is required whereas `description` can be replaced with any combination of letters, numbers, dashes, slashes and underscores.

To reference the equation, use

    @eq:description

or

    {@eq:description}

Curly braces around a reference are stripped from the output.


Usage
-----

To apply the filter, use the following option with pandoc:

    --filter pandoc-eqnos

Note that any use of the `--filter pandoc-citeproc` or `--bibliography=FILE` options with pandoc should come *after* the pandoc-eqnos filter call.


Details
-------

For tex/pdf output, LaTeX's native `equation` environment and `\label` and `\ref` macros are used; for all others the numbers are hard-coded.

Links are *not* constructed -- just the equation numbers.


Installation
------------

Install pandoc-eqnos as root using the bash command

    pip install pandoc-eqnos

To upgrade to the most recent release, use

    pip install --upgrade pandoc-eqnos 

If you have any difficulties with it, please [file an issue] on github so that we can help.

[file an issue]: https://github.com/tomduck/pandoc-eqnos/issues
