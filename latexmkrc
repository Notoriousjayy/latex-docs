# .latexmkrc -- repo root
# Purpose: make custom LaTeX style packages (*.sty) discoverable
# by pdflatex/latexmk regardless of which subdirectory a leaf .tex is built from.
#
# Why this exists:
#   Leaf documents under src/architecture/**/ \usepackage{*}, but the
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

# Search paths for custom .sty / .cls / .tex includes.
#
# PERFORMANCE: these paths must stay narrow. A recursive "$root/src//" entry
# used to live here. Because kpathsea re-walks every recursive entry on each
# lookup (and latexmk performs one lookup per recorded dependency), that single
# entry made kpathsea stat the whole 4,900-file src/ tree thousands of times per
# document: 63s/document instead of 2s/document. There are zero .sty/.cls files
# under src/, so it never resolved anything. Keep style trees explicit here and
# never add a recursive path over a large content directory.
my @texinputs = (
    "$root/tooling/latex//",         # canonical house style (style.sty + helpers)
    "$root/tooling/styles/latex//",  # domain modules (technical-*, financial, hr, ...)
    "$root/sty//",     # harmless if absent
    "$root/tex//",     # harmless if absent
);

$ENV{TEXINPUTS} = ':' . join(':', @texinputs) . ':' . ($ENV{TEXINPUTS} // '') . ':';

# BibTeX inputs/styles are resolved relative to each document directory; no
# recursive repository-wide entry (same kpathsea cost as above).
$ENV{BIBINPUTS} = ':' . ($ENV{BIBINPUTS} // '') . ':';
$ENV{BSTINPUTS} = ':' . ($ENV{BSTINPUTS} // '') . ':';

# Engine: pdflatex (matches your CI matrix).
my $pdf_mode = 1;

# Build hygiene.
my $silent      = 0;
my $emulate_aux = 1;

# Track .synctex.gz as a generated artifact so 'latexmk -c' cleans it.
my @generated_exts = ('synctex.gz');

# Expose the values expected by newer latexmk versions.
$silent      = $silent;
$emulate_aux = $emulate_aux;
push @generated_exts, @generated_exts;
