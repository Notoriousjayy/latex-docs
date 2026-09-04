#!/usr/bin/env python3
"""
Migrate 104 cybersecurity cornell-notes documents from root level to
organized topical structure with style modernization.
"""

import os
import re
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# Define topical groupings
TOPICAL_GROUPS = {
    "foundations-and-core-defense": (1, 10),
    "platform-network-and-iot": (11, 23),
    "governance-risk-and-resilience": (24, 40),
    "forensics-and-incident-response": (41, 46),
    "cryptography-identity-and-privacy": (47, 58),
    "network-cloud-and-virtualization": (59, 70),
    "physical-operational-and-assurance": (71, 83),
    "critical-infrastructure-and-emerging-threats": (84, 104),
}

def get_topical_group(chapter_num: int) -> str:
    """Determine topical group for chapter number."""
    for group, (start, end) in TOPICAL_GROUPS.items():
        if start <= chapter_num <= end:
            return group
    raise ValueError(f"Chapter {chapter_num} out of range")

def extract_title_from_filename(filename: str) -> str:
    """Extract human-readable title from filename.
    
    Example: 001-information-security-in-the-modern-enterprise-cornell-notes.tex
    -> 'information-security-in-the-modern-enterprise'
    """
    # Remove leading chapter number
    name = re.sub(r'^\d{3}-', '', filename)
    # Remove -cornell-notes.tex suffix
    name = name.replace('-cornell-notes.tex', '')
    return name

def create_canonical_filename(chapter_num: int, title_slug: str) -> str:
    """Create canonical filename: chNN-<slug>-cornell-notes.tex, max 50 chars.
    
    Canonical format: chNN-<slug>-cornell-notes.tex
    Maximum 50 characters total.
    """
    base = f"ch{chapter_num:02d}-{title_slug}"
    suffix = "-cornell-notes.tex"
    
    # Ensure total length <= 50
    max_slug_len = 50 - len(f"ch{chapter_num:02d}-") - len(suffix)
    if len(base) + len(suffix) > 50:
        base = base[:max_slug_len]
    
    canonical = base + suffix
    if len(canonical) > 50:
        raise ValueError(f"Canonical name too long: {canonical} ({len(canonical)} chars)")
    
    return canonical

def extract_chapter_number(filename: str) -> int:
    """Extract chapter number from filename."""
    match = re.match(r'^(\d{3})-', filename)
    if not match:
        raise ValueError(f"Cannot extract chapter number from {filename}")
    return int(match.group(1))

def find_all_root_files(repo_root: Path) -> List[Path]:
    """Find all root-level [0-9][0-9][0-9]-*-cornell-notes.tex files."""
    pattern = re.compile(r'^\d{3}-.*-cornell-notes\.tex$')
    files = []
    for item in sorted(repo_root.glob('[0-9][0-9][0-9]-*-cornell-notes.tex')):
        if pattern.match(item.name):
            files.append(item)
    return files

def transform_latex_content(content: str, chapter_num: int, full_title: str) -> str:
    """Apply comprehensive LaTeX transformation to document content.
    
    Transformations:
    - Replace preamble with new cornell-notes-based preamble
    - Remove color definitions
    - Remove old title and fancy header
    - Add standard metadata contract
    - Convert custom boxes to canonical versions
    - Update table structures
    """
    
    # 1. Find and replace preamble (everything before \begin{document})
    # The preamble includes documentclass and all \usepackage commands
    
    # Extract content after \begin{document}
    doc_match = re.search(r'\\begin\{document\}', content)
    if not doc_match:
        raise ValueError("No \\begin{document} found")
    
    doc_start = doc_match.start()
    
    # Extract everything before \begin{document}
    preamble_section = content[:doc_start]
    body_and_end = content[doc_start:]
    
    # Build new preamble
    new_preamble = r"""\documentclass[11pt,letterpaper]{article}
\usepackage{cornell-notes}
"""
    
    # Keep \usepackage{needspace} if it exists in original
    if r'\usepackage{needspace}' in preamble_section:
        new_preamble += r'\usepackage{needspace}' + '\n'
    
    new_preamble += '\n'
    
    # Add metadata contract
    chapter_title = full_title.replace('_', ' ').title()
    
    metadata = f"""\\newcommand{{\\CornellDocumentTitle}}{{Chapter {chapter_num}: {full_title}}}
\\title{{\\CornellDocumentTitle}}
\\author{{}}
\\date{{}}
\\setDocTitle{{\\CornellDocumentTitle}}
\\setDocSubtitle{{Cybersecurity Cornell Notes}}
\\setCornellCollection{{Cybersecurity Reference Notes}}
\\setCornellUnitType{{Chapter}}
\\setCornellUnitNumber{{{chapter_num}}}
\\setCornellUnitTitle{{{full_title}}}
\\setCornellCompanionLabel{{Cybersecurity study companion}}

"""
    
    new_preamble += metadata
    
    # Reconstruct content
    result = new_preamble + body_and_end
    
    # 2. Remove color definitions (Navy, Teal, CueGray, etc.)
    color_patterns = [
        r'\\definecolor\{Navy\}\{.*?\}(?:\n)?',
        r'\\definecolor\{Teal\}\{.*?\}(?:\n)?',
        r'\\definecolor\{CueGray\}\{.*?\}(?:\n)?',
        r'\\definecolor\{SoftBlue\}\{.*?\}(?:\n)?',
        r'\\definecolor\{SoftGreen\}\{.*?\}(?:\n)?',
        r'\\definecolor\{SoftAmber\}\{.*?\}(?:\n)?',
        r'\\definecolor\{RuleGray\}\{.*?\}(?:\n)?',
        r'\\definecolor\{TextGray\}\{.*?\}(?:\n)?',
    ]
    for pattern in color_patterns:
        result = re.sub(pattern, '', result, flags=re.DOTALL)
    
    # 3. Remove \thispagestyle{fancy}
    result = re.sub(r'\\thispagestyle\{fancy\}\s*\n?', '', result)
    
    # 4. Remove negative spacing after \maketitle (e.g., \vspace{-2em})
    result = re.sub(r'\\maketitle\s*\\vspace\{-[^}]*\}', r'\\maketitle', result)
    
    # 5. Convert custom box environments to canonical versions
    # orientationbox -> CornellOverviewBox{Chapter Orientation}
    result = re.sub(
        r'\\begin\{orientationbox\}(.*?)\\end\{orientationbox\}',
        r'\\begin{CornellOverviewBox}{Chapter Orientation}\1\\end{CornellOverviewBox}',
        result,
        flags=re.DOTALL
    )
    
    # topicsummary[optional arg] -> CornellSummaryBox{Topic Summary}
    result = re.sub(
        r'\\begin\{topicsummary\}(?:\[[^\]]*\])?(.*?)\\end\{topicsummary\}',
        r'\\begin{CornellSummaryBox}{Topic Summary}\1\\end{CornellSummaryBox}',
        result,
        flags=re.DOTALL
    )
    
    # defensebox -> CornellOverviewBox{Defensive Guidance}
    result = re.sub(
        r'\\begin\{defensebox\}(.*?)\\end\{defensebox\}',
        r'\\begin{CornellOverviewBox}{Defensive Guidance}\1\\end{CornellOverviewBox}',
        result,
        flags=re.DOTALL
    )
    
    # historybox -> CornellWarningBox{Historical Context}
    result = re.sub(
        r'\\begin\{historybox\}(.*?)\\end\{historybox\}',
        r'\\begin{CornellWarningBox}{Historical Context}\1\\end{CornellWarningBox}',
        result,
        flags=re.DOTALL
    )
    
    # synthesisbox -> CornellSummaryBox{Chapter Synthesis}
    result = re.sub(
        r'\\begin\{synthesisbox\}(.*?)\\end\{synthesisbox\}',
        r'\\begin{CornellSummaryBox}{Chapter Synthesis}\1\\end{CornellSummaryBox}',
        result,
        flags=re.DOTALL
    )
    
    # takeawaybox -> CornellExamBox{One-Sentence Takeaway}
    result = re.sub(
        r'\\begin\{takeawaybox\}(.*?)\\end\{takeawaybox\}',
        r'\\begin{CornellExamBox}{One-Sentence Takeaway}\1\\end{CornellExamBox}',
        result,
        flags=re.DOTALL
    )
    
    # 6. Convert \CornellRow to \CornellNoteRow in tables
    result = re.sub(r'\\CornellRow', r'\\CornellNoteRow', result)
    
    # 7. Remove local definitions of \CornellHeader, \CornellRow, \ChapterMark if they exist
    result = re.sub(r'\\newcommand\{\\CornellHeader\}.*?\n', '', result)
    result = re.sub(r'\\newcommand\{\\CornellRow\}.*?\n', '', result)
    result = re.sub(r'\\newcommand\{\\ChapterMark\}.*?\n', '', result)
    result = re.sub(r'\\renewcommand\{\\CornellRow\}.*?\n', '', result)
    
    return result

def process_file(
    source_path: Path,
    dest_dir: Path,
    chapter_num: int,
    topical_group: str,
    manifest_entries: List[Dict]
) -> Tuple[str, str]:
    """Process a single file: read, transform, write to new location.
    
    Returns: (original_filename, canonical_filename)
    """
    # Extract title
    title_slug = extract_title_from_filename(source_path.name)
    
    # Create canonical filename
    canonical_name = create_canonical_filename(chapter_num, title_slug)
    
    # Read original content
    original_content = source_path.read_text(encoding='utf-8')
    
    # Transform LaTeX content
    transformed_content = transform_latex_content(original_content, chapter_num, title_slug.replace('-', ' '))
    
    # Determine destination path
    dest_path = dest_dir / topical_group / canonical_name
    
    # Write transformed content
    dest_path.write_text(transformed_content, encoding='utf-8')
    
    # Record in manifest
    manifest_entries.append({
        "original_filename": source_path.name,
        "canonical_filename": canonical_name,
        "topical_group": topical_group,
        "chapter_number": chapter_num,
        "title": title_slug.replace('-', ' ').title()
    })
    
    return source_path.name, canonical_name

def migrate_collection(repo_root: Path, dry_run: bool = False) -> Dict:
    """Execute the complete migration.
    
    Returns: results dictionary with statistics
    """
    # Find all root-level files
    root_files = find_all_root_files(repo_root)
    
    if not root_files:
        raise ValueError("No root-level cornell-notes files found")
    
    print(f"Found {len(root_files)} files to migrate")
    
    # Destination base directory
    dest_base = repo_root / "src" / "cornell-notes" / "security" / "cybersecurity-reference"
    
    if not dest_base.exists():
        raise ValueError(f"Destination base {dest_base} does not exist")
    
    # Track results
    manifest_entries = []
    processed = []
    missing_chapters = []
    
    # Process each file
    for source_file in root_files:
        try:
            chapter_num = extract_chapter_number(source_file.name)
            topical_group = get_topical_group(chapter_num)
            
            if dry_run:
                title_slug = extract_title_from_filename(source_file.name)
                canonical_name = create_canonical_filename(chapter_num, title_slug)
                print(f"  [{chapter_num:3d}] {source_file.name} -> {topical_group}/{canonical_name}")
                
                manifest_entries.append({
                    "original_filename": source_file.name,
                    "canonical_filename": canonical_name,
                    "topical_group": topical_group,
                    "chapter_number": chapter_num,
                    "title": extract_title_from_filename(source_file.name).replace('-', ' ').title()
                })
                processed.append(source_file.name)
            else:
                original, canonical = process_file(
                    source_file,
                    dest_base,
                    chapter_num,
                    topical_group,
                    manifest_entries
                )
                processed.append(original)
                print(f"  ✓ [{chapter_num:3d}] {original} -> {canonical}")
        
        except Exception as e:
            print(f"  ✗ Error processing {source_file.name}: {e}", file=sys.stderr)
            raise
    
    # Identify missing chapters (if any)
    processed_numbers = sorted([extract_chapter_number(f) for f in processed])
    all_expected = set(range(1, 105))
    missing = sorted(all_expected - set(processed_numbers))
    
    # Build results
    results = {
        "total_files": len(root_files),
        "processed": len(processed),
        "destination_base": str(dest_base),
        "manifest_entries_count": len(manifest_entries),
        "chapter_range": f"001-104",
        "missing_chapters": missing,
        "processed_chapters": processed_numbers,
        "manifest": {
            "metadata": {
                "collection_name": "Cybersecurity Reference Notes",
                "chapter_count": len(manifest_entries),
                "chapter_range": f"{min(processed_numbers):03d}-{max(processed_numbers):03d}",
                "intake_date": "2026-09-04",
                "missing_chapters": missing
            },
            "chapters": sorted(manifest_entries, key=lambda x: x["chapter_number"])
        }
    }
    
    return results

def main():
    repo_root = Path("/home/jordan/latex-docs")
    
    if not repo_root.exists():
        print(f"Repository root not found: {repo_root}", file=sys.stderr)
        sys.exit(1)
    
    # Check if we should do a dry run
    dry_run = "--dry-run" in sys.argv
    
    if dry_run:
        print("DRY RUN - no files will be modified\n")
    
    results = migrate_collection(repo_root, dry_run=dry_run)
    
    print(f"\nMigration Summary:")
    print(f"  Total files processed: {results['total_files']}")
    print(f"  Chapters: {results['chapter_range']}")
    print(f"  Missing: {results['missing_chapters'] if results['missing_chapters'] else 'none'}")
    print(f"  Destination: {results['destination_base']}")
    
    # Write manifest to disk unless dry run
    if not dry_run:
        manifest_path = repo_root / "tooling" / "manifests" / "cybersecurity-reference-intake.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(manifest_path, 'w') as f:
            json.dump(results['manifest'], f, indent=2)
        
        print(f"  Manifest written to: {manifest_path}")
    
    return 0 if not dry_run else 1

if __name__ == "__main__":
    sys.exit(main())
