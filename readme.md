# GenSON

GenSON is a simple experimental extension to JSON syntax for specifying collections of JSON objects sampled from arbitrary spaces.  The primary use case for such a tool would be performing parameter searches / optimization, where each parameter set is allowed to be arbitrarily structured data.  Did I mention it was experimental?  It's only a few hundred lines of code, and I'm still feeling around for the right level of complexity (and if this is worthwhile in the first place)

## API

The API is roughly meant to follow that of the Python `simplejson` module.  You can load a GenSON document from a file by calling `genson.load(f)`, and from a string by calling `genson.loads(s)`.  The returned object is an iterator over dictionary objects suitable for dumping as JSON (e.g. using `simplejson`).

## Basic Generator Syntax

GenSON is a strict superset of JSON, insofar as every JSON object is a valid GenSON object that resolves to itself. Additional syntax in GenSON allows for compactly specifying the generation of many JSON objects according to various sampling rules.  For instance,

    { "parameter1": gaussian(0, 1, draws=6) }

resolves to six objects with `parameter1` drawn from a zero mean, unit variance gaussian distribution.  Furthermore,

    { "parameter2": < 1, 2, 3 > }
    
resolves to three objects with `parameter2` equal to 1, 2, and 3, respectively, in each resulting object.  The `< >` operator is a shortcut for the `grid` generator function.  Combinations of sampling operations result in exhaustive crosses, such that

    { "parameter3": <1, 2, 3>,
      "parameter4": <4, 5, 6> }

results in nine objects ( i.e. [1,4], [1,5], [1,6], [2,4] ... ).

GenSON also introduces tuple keys to JSON as a mechanism for specifying sampling dependencies:

    { ("p6","p7","p8"): < (1,2,3), (4,5,6) > }
    
produces two objects, wherein the first `p6`, `p7`, and `p8` are equal to 1,2 and 3, and in the second they are equal to 4,5, and 6, respectively. 

As in JSON, values can be arbitrarily deeply nested, such that constructs like:

    { ("p1", "p2") : < ( uniform(-1,1), 4), ({"nested":"dictionary"}, 6)> }

are valid, and do what you'd "expect".

## Internal References

GenSON values can make reference to other keys elsewhere in the object.  Any GenSON value can take a Javascript-style object member reference (e.g. `this.parameter1`).  The keywords `this`, `parent`, and `root` allow references to other object members elsewhere in the object hierarchy.

Currently, reference resolution is done "in order," meaning that a key cannot refer to another one defined later in the document.  This may change in the future, but for now this obviates having to worry about reference cycles, etc.

## Expressions

GenSON also supports algebraic expressions in any "value" slot within the GenSON document.  Thus, the following GenSON:

    { "x": <1,2,3>, "y": 2.2*sin(this.x) }

will generate three dictionaries with the value of `y` equal to 2.2 times the sin of `x`.

Expression syntax is also allowed within generator functions, and this can provide a convenient means for generating joint distributions.  For instance, if you wanted `x` and `y` to be sampled from an upper-triangular distribution, this can be achieved with the following document:

    { "x": uniform(0, 1), "y": uniform(this.x, 1) }

## Text editor support

(courtesy of Zak Stone)

The included gson-mode.el file provides basic syntax highlighting and indentation support for GenSON. To use this file, place it somewhere on your Emacs load path and then activate it with the following lines:

    (require 'gson-mode)
    (add-to-list 'auto-mode-alist '("\\.gson$" . gson-mode))

You may wish to create a ~/.elisp directory for .el files and add the entire directory to your Emacs load path as follows:

    (add-to-list 'load-path "~/.elisp/")

  