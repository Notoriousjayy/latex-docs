# latexmkrc - Global LaTeX build configuration for CI and local builds
# Place in repository root
# ============================================================================

# ============================================================================
# PDF Output Mode
# ============================================================================
$pdf_mode = 1;

# ============================================================================
# Engine Configurations with -shell-escape for minted/Pygments
# ============================================================================
# pdflatex - most documents
$pdflatex = 'pdflatex -interaction=nonstopmode -halt-on-error -shell-escape %O %S';

# lualatex - for documents using fontspec, Unicode, etc.
$lualatex = 'lualatex -interaction=nonstopmode -halt-on-error -shell-escape %O %S';

# xelatex - alternative Unicode engine
$xelatex = 'xelatex -interaction=nonstopmode -halt-on-error -shell-escape %O %S';

# ============================================================================
# Build Behavior
# ============================================================================
# Run enough passes to resolve all references, TOC, and minted code blocks
$max_repeat = 5;

# Show commands being run (useful for CI debugging)
$silent = 0;

# Use synctex for editor integration (local development)
$synctex = 1;

# ============================================================================
# Bibliography Support
# ============================================================================
$bibtex_use = 2;
$biber = 'biber --validate-datamodel %O %S';

# ============================================================================
# File Cleanup - Standard LaTeX auxiliary files
# ============================================================================
$clean_ext = 'aux bbl bcf blg fdb_latexmk fls log out run.xml synctex.gz toc lof lot loa nav snm vrb';

# ============================================================================
# Minted-Specific Configuration (Critical for CI)
# ============================================================================
# Add minted auxiliary file extensions to cleanup
push @generated_exts, qw(pyg pygtex pygstyle);

# Track _minted-* directories for cleanup
$clean_full_ext = 'pdf dvi ps synctex.gz';

# Custom dependency: tell latexmk to track .pyg files
# This ensures proper rebuilds when source code blocks change
add_cus_dep('pyg', 'pygtex', 0, 'run_pygmentize');
sub run_pygmentize {
    # Pygments is called automatically by minted with -shell-escape
    # This dependency just ensures proper rebuild tracking
    return 0;
}

# Detect minted errors and trigger rebuild
push @file_not_found, '^Package minted Error';

# ============================================================================
# Custom Rules for Recursive Directory Cleanup
# ============================================================================
# Clean _minted-* cache directories (they can cause issues between builds)
$cleanup_includes_cusdep_generated = 1;
$cleanup_includes_generated = 1;

# Add hook to clean _minted-* directories
# This runs during `latexmk -c` or `latexmk -C`
END {
    if ($cleanup_mode > 0) {
        # Find and remove _minted-* directories in current directory
        my @minted_dirs = glob("_minted-*");
        foreach my $dir (@minted_dirs) {
            if (-d $dir) {
                print "Cleaning minted cache: $dir\n";
                system("rm -rf \"$dir\"");
            }
        }
    }
}

# ============================================================================
# PythonTeX Support (if using pythontex package)
# ============================================================================
add_cus_dep('pytxcode', 'tex', 0, 'pythontex');
sub pythontex {
    system("pythontex \"$_[0]\"");
}

# ============================================================================
# Glossary Support (if using glossaries package)
# ============================================================================
add_cus_dep('glo', 'gls', 0, 'makeglo2gls');
sub makeglo2gls {
    system("makeindex -s \"$_[0].ist\" -t \"$_[0].glg\" -o \"$_[0].gls\" \"$_[0].glo\"");
}
push @generated_exts, qw(glo gls glg);

# ============================================================================
# Index Support
# ============================================================================
add_cus_dep('idx', 'ind', 0, 'makeindex');
sub makeindex {
    system("makeindex \"$_[0].idx\"");
}
push @generated_exts, qw(idx ind ilg);

# ============================================================================
# Preview Settings (uncomment for local development)
# ============================================================================
# Linux (GNOME):
# $pdf_previewer = 'evince %O %S';
# Linux (KDE):
# $pdf_previewer = 'okular %O %S';
# macOS:
# $pdf_previewer = 'open -a Preview %S';
# Windows:
# $pdf_previewer = 'start %S';
# WSL with Windows PDF viewer:
# $pdf_previewer = 'cmd.exe /c start "" %S';
