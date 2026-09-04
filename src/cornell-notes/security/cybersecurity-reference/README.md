# Cybersecurity Reference Notes Collection

## Overview

This collection contains 104 comprehensive Cornell-style study notes covering cybersecurity theory, practice, and applied security engineering. The material spans foundational security concepts through emerging threats and advanced technologies.

## Collection Metadata

- **Total Chapters**: 104 (ch01–ch104)
- **Intake Date**: 2026-09-04
- **Semantic Style**: cornell-notes LaTeX package
- **Publication Format**: PDF (via `make`)

## Organization by Topical Group

The 104 chapters are organized into 8 topical groups based on subject matter domains:

### 1. Foundations and Core Defense (Chapters 1–10)
Establishes fundamental security concepts, enterprise security foundations, cryptographic principles, identity verification, intrusion detection, web application security, and core defensive strategies.

### 2. Platform, Network, and IoT (Chapters 11–23)
Covers Unix/Linux platform security, internet security, botnets, intranets, local area networks (including LAN in chapter 16), wireless security, sensor networks, IoT security, cellular networks, RFID, and optical networks.

### 3. Governance, Risk, and Resilience (Chapters 24–40)
Addresses security management, policy frameworks, information technology security management, social engineering, vulnerability assessment, security metrics, disaster recovery, business continuity for SMBs, security certifications, and compliance planning.

### 4. Forensics and Incident Response (Chapters 41–46)
Focuses on cybersecurity forensics, incident response, e-discovery, network forensics, metadata forensics, and hard drive imaging techniques.

### 5. Cryptography, Identity, and Privacy (Chapters 47–58)
Explores encryption, key management, digital signatures, cryptographic protocols, identity management, privacy mechanisms, and authentication systems.

### 6. Network, Cloud, and Virtualization (Chapters 59–70)
Examines network security architectures, cloud computing security (private, virtual, and hybrid clouds), software-defined networking, network function virtualization, and virtual infrastructure protection.

### 7. Physical, Operational, and Assurance (Chapters 71–83)
Covers physical security, biometrics, user and identity management, intrusion prevention/detection systems, packet analysis, firewalls, penetration testing, system security, access controls, endpoint security, assessments, audits, and infrastructure security.

### 8. Critical Infrastructure and Emerging Threats (Chapters 84–104)
Addresses critical infrastructure cybersecurity, smart cities, autonomous vehicles, cyber warfare, cyberattacks on power grids, maritime security, healthcare cybersecurity, AI and machine learning security, data loss protection, and future threat landscapes.

## Building the Collection

### Single Document Build
```bash
latexmk -xelatex -interaction=nonstopmode src/cornell-notes/security/cybersecurity-reference/foundations-and-core-defense/ch01-*.tex
```

### Batch Compilation
The repository's build system discovers and compiles all documents:
```bash
make roots      # List all discovered documents (includes these 104)
make list-roots # Show filtered root discovery
```

### Build Infrastructure
- **Engine**: xelatex with latexmk
- **LaTeX Package**: `cornell-notes` (shared, source-anonymous)
- **Output**: `public/pdfs/security/cybersecurity-reference/<topical-group>/<filename>.pdf`
- **Logs**: `public/logs/security/cybersecurity-reference/<topical-group>/<filename>.{log.txt,stdout.txt,stderr.txt}`

## Canonical Filenames

Each document follows the canonical naming convention:
- **Pattern**: `ch<NN>-<slug>-cornell-notes.tex`
- **Constraints**: 
  - `<NN>` = zero-padded 2-digit chapter number (01–104)
  - `<slug>` = kebab-case, alphanumeric + hyphens, maximum 50 characters total
  - All lowercase, no version/upload suffixes

### Filename Examples
- `ch01-information-security-i-cornell-notes.tex` (Information Security in the Modern Enterprise)
- `ch16-local-area-network-security-cornell-notes.tex` (Local Area Network Security, included)
- `ch104-future-trends-in-mar-cornell-notes.tex` (Future Trends in Maritime Cybersecurity)

## Document Structure

Each transformed document:
1. **Preamble**: `\documentclass{article}` + `\usepackage{cornell-notes}`
2. **Metadata Contract**: Standard `\setCornellCollection`, `\setCornellUnitType`, `\setCornellUnitNumber`, etc.
3. **Content Sections**:
   - Learning Objectives (itemized)
   - Cornell Cue-and-Notes (longtables with `\CornellNoteRow` entries)
   - Topic Summaries in canonical box environments
   - Threat-and-Control Tables (industry-standard format)
   - Self-Test Questions and Answers
   - Key Terms and Glossary
   - Chapter Synthesis (canonical box)
   - One-Sentence Takeaway (canonical box)

## Style Transformations Applied

The migration transformed each source document from a legacy standalone preamble to the shared `cornell-notes` package:

1. **Preamble Modernization**
   - Removed 20 individual `\usepackage` declarations
   - Replaced with single `\usepackage{cornell-notes}`
   - Preserved `\usepackage{needspace}` where present

2. **Color Definitions**
   - Removed local color declarations (Navy, Teal, CueGray, SoftBlue, SoftGreen, SoftAmber, RuleGray, TextGray)
   - Colors now managed by `cornell-notes.sty`

3. **Box Environments**
   - `orientationbox` → `CornellOverviewBox{Chapter Orientation}`
   - `topicsummary` → `CornellSummaryBox{Topic Summary}`
   - `defensebox` → `CornellOverviewBox{Defensive Guidance}`
   - `historybox` → `CornellWarningBox{Historical Context}`
   - `synthesisbox` → `CornellSummaryBox{Chapter Synthesis}`
   - `takeawaybox` → `CornellExamBox{One-Sentence Takeaway}`

4. **Table Structures**
   - `\CornellRow` → `\CornellNoteRow` (preserving table structure and content)
   - Removed local macro definitions to rely on package-level implementation

5. **Metadata Contract**
   - Added standardized `\setDocTitle`, `\setDocSubtitle`, `\setCornellCollection`, `\setCornellUnitType`, `\setCornellUnitNumber`, `\setCornellUnitTitle`, `\setCornellCompanionLabel`
   - Supports dynamic page headers, ToC generation, and collection indexing

## Content Preservation

**All substantive content is preserved**:
- Learning objectives and educational framing
- Cornell note-taking structure (cue and notes columns)
- Topic summaries and synthesis sections
- Threat landscape and control guidance
- Checklists and procedural content
- Key terms and definitions
- Self-assessment questions and model answers
- Domain-specific context and case studies

**No content was truncated, reworded, or removed** — only structural LaTeX metadata and styling were modernized.

## Intake Manifest

The complete source-to-destination mapping is recorded in:
```
tooling/manifests/cybersecurity-reference-intake.json
```

Structure:
- `metadata`: Collection-level facts (104 chapters, all present, 2026-09-04 intake)
- `chapters`: Array of 104 objects, each with:
  - `original_filename`: Source root-level filename
  - `canonical_filename`: Destination filename
  - `topical_group`: Directory under cybersecurity-reference/
  - `chapter_number`: 1–104
  - `title`: Human-readable chapter title

## Testing and Validation

Comprehensive tests in `tests/test_cybersecurity_reference_collection.py` validate:
- Manifest completeness (104 entries, all chapters 001–104)
- File existence (all 104 canonical files in correct topical groups)
- Filename compliance (kebab-case, max 50 characters, no suffixes)
- LaTeX structure (exactly one `\maketitle`, required metadata setters)
- Content preservation (learning objectives, tables, summaries, all sections present)
- Style compliance (only `cornell-notes` semantic module used, no `listings` package)

Run tests:
```bash
python3 -m unittest tests/test_cybersecurity_reference_collection.py -v
```

## Known Chapters

All 104 chapters are present, including:
- **Chapter 16** (Local Area Network Security) — included in platform-network-and-iot group

## Source and Attribution

This collection is organized as Cornell-notes reference material. All documents have been transformed to use the shared `cornell-notes` LaTeX package and organized by topical domain for structured learning and reference.

---

**Last Updated**: 2026-09-04  
**Canonical Path**: `src/cornell-notes/security/cybersecurity-reference/`
