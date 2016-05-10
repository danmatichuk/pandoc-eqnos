#! /usr/bin/env python

"""pandoc-eqnos: a pandoc filter that inserts equation nos. and refs."""

# Copyright 2015, 2016 Thomas J. Duck.
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# OVERVIEW
#
# The basic idea is to scan the AST twice in order to:
#
#   1. Insert text for the equation number in each equation.
#      For LaTeX, change to a numbered equation and use \label{...}
#      instead.  The equation labels and associated equation numbers
#      are stored in the global references tracker.
#
#   2. Replace each reference with an equation number.  For LaTeX,
#      replace with \ref{...} instead.
#
# There is also an initial scan to do some preprocessing.

# pylint: disable=invalid-name

import re
import functools
import argparse
import json
import uuid

from pandocfilters import walk
from pandocfilters import RawInline, elt

import pandocfiltering
from pandocfiltering import STRTYPES, STDIN, STDOUT
from pandocfiltering import get_meta
from pandocfiltering import repair_refs, use_refs_factory, replace_refs_factory
from pandocfiltering import use_attrs_factory, filter_attrs_factory

from pandocattributes import PandocAttributes


# Read the command-line arguments
parser = argparse.ArgumentParser(description='Pandoc equations numbers filter.')
parser.add_argument('fmt')
parser.add_argument('--pandocversion', help='The pandoc version.')
args = parser.parse_args()

# Set/get PANDOCVERSION
pandocfiltering.init(args.pandocversion)
PANDOCVERSION = pandocfiltering.PANDOCVERSION

# Patterns for matching labels and references
LABEL_PATTERN = re.compile(r'(eq:[\w/-]*)')

Nreferences = 0  # The numbered references count (i.e., excluding tags)
references = {}  # Global references tracker

# Meta variables; may be reset elsewhere
plusname = ['eq.', 'eqs.']            # Used with \cref
starname = ['Equation', 'Equations']  # Used with \Cref
cleveref_default = False              # Default setting for clever referencing


# Helper functions ----------------------------------------------------------

def is_attrmath(key, value):
    """True if this is an attributed equation; False otherwise."""
    return key == 'Math' and len(value) == 3

def parse_attrmath(key, value):
    """Parses an attributed equation."""
    assert key == 'Math'
    attrs, env, equation = value
    if attrs[0] == 'eq:': # Make up a unique description
        attrs[0] = attrs[0] + str(uuid.uuid4())
    return attrs, env, equation


# Actions --------------------------------------------------------------------

use_attrs_math = use_attrs_factory('Math', allow_space=True)
filter_attrs_math = filter_attrs_factory('Math', 2)

# pylint: disable=unused-argument,too-many-branches
def process_equations(key, value, fmt, meta):
    """Processes the attributed equations."""

    # pylint: disable=global-statement
    global Nreferences

    if is_attrmath(key, value):

        # Parse the equation
        # pylint: disable=unused-variable
        attrs, env, equation = parse_attrmath(key, value)
        attrs = PandocAttributes(attrs, 'pandoc')

        # Bail out if the label does not conform
        if not attrs.id or not LABEL_PATTERN.match(attrs.id):
            return

        # Save the reference
        if 'tag' in attrs.kvs:
            # Remove any surrounding quotes
            if attrs['tag'][0] == '"' and attrs['tag'][-1] == '"':
                attrs['tag'] = attrs['tag'].strip('"')
            elif attrs['tag'][0] == "'" and attrs['tag'][-1] == "'":
                attrs['tag'] = attrs['tag'].strip("'")
            references[attrs.id] = attrs['tag']
        else:
            Nreferences += 1
            references[attrs.id] = Nreferences

        # Adjust equation depending on the output format
        if fmt == 'latex':
            if 'tag' in attrs.kvs:
                equation += r'\tag{%s}\label{%s}' % \
                  (references[attrs.id].replace(' ', r'\ '), attrs.id)
            else:
                equation += r'\label{%s}'%attrs.id
        elif type(references[attrs.id]) is int:
            equation += r'\qquad (%d)' % references[attrs.id]
        else:  # It is a str
            assert type(references[attrs.id]) in STRTYPES
            # Handle both math and text
            text = references[attrs.id].replace(' ', r'\ ')
            if text.startswith('$') and text.endswith('$'):
                label = text[1:-1]
            else:
                label = r'\text{%s}' % text
            equation += r'\qquad (%s)' % label

        # Return the replacement
        if fmt == 'latex':
            return RawInline('tex',
                             r'\begin{equation}%s\end{equation}'%equation)
        else:
            value[-1] = equation

        if fmt in ('html', 'html5'):  # Insert anchor
            anchor = RawInline('html', '<a name="%s"></a>'%attrs.id)
            math = elt('Math', 3)(*value)  # pylint: disable=star-args
            math['c'] = list(math['c'])
            return [anchor, math]


# Main program ---------------------------------------------------------------

def process(meta):
    """Saves metadata fields in global variables and returns a few
    computed fields."""

    # pylint: disable=global-statement
    global cleveref_default, plusname, starname

    # Read in the metadata fields and do some checking

    if 'cleveref' in meta:
        cleveref_default = get_meta(meta, 'cleveref')
        assert cleveref_default in [True, False]

    if 'eqnos-cleveref' in meta:
        cleveref_default = get_meta(meta, 'eqnos-cleveref')
        assert cleveref_default in [True, False]

    if 'eqnos-plus-name' in meta:
        tmp = get_meta(meta, 'eqnos-plus-name')
        if type(tmp) is list:
            plusname = tmp
        else:
            plusname[0] = tmp
        assert len(plusname) == 2
        for name in plusname:
            assert type(name) in STRTYPES

    if 'eqnos-star-name' in meta:
        tmp = get_meta(meta, 'eqnos-star-name')
        if type(tmp) is list:
            starname = tmp
        else:
            starname[0] = tmp
        assert len(starname) == 2
        for name in starname:
            assert type(name) in STRTYPES


def main():
    """Filters the document AST."""

    # Get the output format, document and metadata
    fmt = args.fmt
    doc = json.loads(STDIN.read())
    meta = doc[0]['unMeta']

    # Process the metadata variables
    process(meta)

    # First pass
    altered = functools.reduce(lambda x, action: walk(x, action, fmt, meta),
                               [repair_refs, use_attrs_math, process_equations,
                                filter_attrs_math], doc)

    # Second pass
    use_refs = use_refs_factory(references.keys())
    replace_refs = replace_refs_factory(references, cleveref_default,
                                        'equation', plusname, starname)
    altered = functools.reduce(lambda x, action: walk(x, action, fmt, meta),
                               [use_refs, replace_refs], altered)

    # Dump the results
    json.dump(altered, STDOUT)

    # Flush stdout
    STDOUT.flush()

if __name__ == '__main__':
    main()
