# latexmkrc - Global LaTeX build configuration
# Place in repository root or ~/.latexmkrc

# Default to PDF output
$pdf_mode = 1;

# Use pdflatex by default (most compatible with minted)
$pdflatex = 'pdflatex -interaction=nonstopmode -halt-on-error -shell-escape %O %S';

# Alternative: LuaLaTeX for better Unicode support
# Uncomment to use lualatex instead:
# $pdf_mode = 4;
# $lualatex = 'lualatex -interaction=nonstopmode -halt-on-error -shell-escape %O %S';

# Enable shell escape (required for minted package)
$ENV{'shell_escape'} = 1;

# Clean up these extensions
$clean_ext = 'aux bbl bcf blg fdb_latexmk fls log out run.xml synctex.gz toc lof lot';

# Custom clean patterns for minted
push @generated_exts, 'pyg';

# Add _minted-* directories to clean
$clean_full_ext = 'pdf dvi ps synctex.gz';

# Increase maximum number of runs to handle complex documents
$max_repeat = 5;

# Show command execution
$silent = 0;

# Use synctex for editor integration
$synctex = 1;

# Handle biber/bibtex automatically
$bibtex_use = 2;

# For documents using biber
$biber = 'biber --validate-datamodel %O %S';

# Custom dependency for minted package
# This ensures latexmk detects when minted cache needs rebuilding
add_cus_dep('pytxcode', 'tex', 0, 'pythontex');
sub pythontex {
    system("pythontex \"$_[0]\"");
}

# Ensure minted style files trigger rebuild
push @file_not_found, '^Package minted Error';

# Preview settings (for local development)
# Uncomment for your preferred PDF viewer:
# $pdf_previewer = 'evince %O %S';      # Linux (GNOME)
# $pdf_previewer = 'okular %O %S';      # Linux (KDE)
# $pdf_previewer = 'open -a Preview %S'; # macOS
# $pdf_previewer = 'start %S';          # Windows
