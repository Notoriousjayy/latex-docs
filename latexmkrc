# .latexmkrc -- repo root
# Purpose: make custom LaTeX style packages (latex-docs-*.sty) discoverable
# by pdflatex/latexmk regardless of which subdirectory a leaf .tex is built from.
#
# Why this exists:
#   Leaf documents under src/architecture/**/ \usepackage{latex-docs-*}, but the
#   .sty files live under src/architecture/style-system/ (and possibly sty/, tex/).
#   kpathsea won't find them unless TEXINPUTS includes those trees recursively.
#
# Notes:
#   - '//' at the end of a path is kpathsea's recursive-descent marker.
#   - Leading and trailing ':' preserve the system TEXINPUTS so core packages
#     (article.cls, geometry.sty, etc.) still resolve.
#   - We anchor paths to this file's directory (the repo root) so builds work
#     no matter what CWD latexmk is invoked from.

use strict;
use warnings;

use File::Basename qw(dirname);
use Cwd            qw(abs_path);

my $root = dirname(abs_path(__FILE__));

# Recursive search paths for custom .sty / .cls / .tex includes.
my @texinputs = (
    "$root/src/architecture/style-system//",
    "$root/src//",     # catches any other in-tree .sty co-located with docs
    "$root/sty//",     # harmless if absent
    "$root/tex//",     # harmless if absent
);

$ENV{TEXINPUTS} = ':' . join(':', @texinputs) . ':' . ($ENV{TEXINPUTS} // '') . ':';

# Same treatment for BibTeX inputs and styles (no-op until you add bibs).
$ENV{BIBINPUTS} = ":$root/src//:" . ($ENV{BIBINPUTS} // '') . ':';
$ENV{BSTINPUTS} = ":$root/src//:" . ($ENV{BSTINPUTS} // '') . ':';

# Engine: pdflatex (matches your CI matrix).
$pdf_mode = 1;

# Build hygiene.
$silent      = 0;
$emulate_aux = 1;

# Track .synctex.gz as a generated artifact so 'latexmk -c' cleans it.
push @generated_exts, 'synctex.gz';
