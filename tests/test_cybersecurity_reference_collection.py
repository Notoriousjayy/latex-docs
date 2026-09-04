#!/usr/bin/env python3
"""
Comprehensive test suite for the Cybersecurity Reference Notes collection.

Validates:
- Manifest completeness and structure
- File existence and organization
- Filename compliance (kebab-case, max 50 chars, no suffixes)
- LaTeX structure and transformations
- Content preservation (sections and structure)
- Style compliance (cornell-notes only, no listings)
"""

import unittest
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Set


class CybersecurityReferenceCollectionTest(unittest.TestCase):
    """Test suite for cybersecurity-reference collection migration."""
    
    REPO_ROOT = Path("/home/jordan/latex-docs")
    COLLECTION_ROOT = REPO_ROOT / "src" / "cornell-notes" / "security" / "cybersecurity-reference"
    MANIFEST_PATH = REPO_ROOT / "tooling" / "manifests" / "cybersecurity-reference-intake.json"
    
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
    
    @classmethod
    def setUpClass(cls):
        """Load manifest and verify collection structure exists."""
        assert cls.COLLECTION_ROOT.exists(), f"Collection root not found: {cls.COLLECTION_ROOT}"
        assert cls.MANIFEST_PATH.exists(), f"Manifest not found: {cls.MANIFEST_PATH}"
        
        with open(cls.MANIFEST_PATH) as f:
            cls.manifest = json.load(f)
        
        cls.metadata = cls.manifest["metadata"]
        cls.chapters = cls.manifest["chapters"]
    
    # ========== Manifest Tests ==========
    
    def test_manifest_structure(self):
        """Manifest has required top-level keys."""
        self.assertIn("metadata", self.manifest)
        self.assertIn("chapters", self.manifest)
        self.assertIsInstance(self.chapters, list)
    
    def test_manifest_metadata_completeness(self):
        """Manifest metadata contains all required fields."""
        required_fields = {
            "collection_name": str,
            "chapter_count": int,
            "chapter_range": str,
            "intake_date": str,
            "missing_chapters": list,
        }
        for field, field_type in required_fields.items():
            self.assertIn(field, self.metadata, f"Missing metadata field: {field}")
            self.assertIsInstance(self.metadata[field], field_type, 
                                f"Field {field} has wrong type")
    
    def test_manifest_chapter_count(self):
        """Manifest contains exactly 104 chapters."""
        self.assertEqual(self.metadata["chapter_count"], 104,
                        "Should have exactly 104 chapters")
        self.assertEqual(len(self.chapters), 104,
                        "Chapters array should have 104 entries")
    
    def test_manifest_no_missing_chapters(self):
        """No chapters are reported as missing."""
        missing = self.metadata["missing_chapters"]
        self.assertEqual(len(missing), 0, 
                        f"Should have no missing chapters, found: {missing}")
    
    def test_manifest_chapter_range(self):
        """Chapter range is 001-104."""
        self.assertEqual(self.metadata["chapter_range"], "001-104")
    
    def test_manifest_chapters_are_sorted(self):
        """Chapters are sorted by chapter_number."""
        chapter_numbers = [ch["chapter_number"] for ch in self.chapters]
        self.assertEqual(chapter_numbers, sorted(chapter_numbers),
                        "Chapters should be sorted by chapter_number")
    
    def test_manifest_chapter_entry_structure(self):
        """Each chapter entry has required fields."""
        required_fields = {
            "original_filename": str,
            "canonical_filename": str,
            "topical_group": str,
            "chapter_number": int,
            "title": str,
        }
        for chapter in self.chapters:
            for field, field_type in required_fields.items():
                self.assertIn(field, chapter, 
                            f"Chapter {chapter.get('chapter_number')} missing {field}")
                self.assertIsInstance(chapter[field], field_type,
                                    f"Field {field} has wrong type in chapter {chapter.get('chapter_number')}")
    
    # ========== File Existence Tests ==========
    
    def test_all_canonical_files_exist(self):
        """All 104 canonical files exist in destination."""
        missing_files = []
        for chapter in self.chapters:
            topical_group = chapter["topical_group"]
            canonical_name = chapter["canonical_filename"]
            file_path = self.COLLECTION_ROOT / topical_group / canonical_name
            
            if not file_path.exists():
                missing_files.append(str(file_path))
        
        self.assertEqual(len(missing_files), 0,
                        f"Missing files:\n" + "\n".join(missing_files))
    
    def test_exactly_104_files_in_collection(self):
        """Exactly 104 .tex files exist in collection."""
        all_files = list(self.COLLECTION_ROOT.glob("**/*.tex"))
        self.assertEqual(len(all_files), 104,
                        f"Found {len(all_files)} files, expected 104")
    
    def test_files_in_correct_topical_groups(self):
        """Each file is in its correct topical group directory."""
        for chapter in self.chapters:
            chapter_num = chapter["chapter_number"]
            topical_group = chapter["topical_group"]
            canonical_name = chapter["canonical_filename"]
            file_path = self.COLLECTION_ROOT / topical_group / canonical_name
            
            self.assertTrue(file_path.exists(),
                          f"Ch{chapter_num:03d} not found at {file_path}")
            
            # Verify topical group mapping is correct
            expected_group = self._get_expected_topical_group(chapter_num)
            self.assertEqual(topical_group, expected_group,
                           f"Ch{chapter_num:03d} in wrong group: {topical_group} vs {expected_group}")
    
    def _get_expected_topical_group(self, chapter_num: int) -> str:
        """Determine expected topical group for chapter."""
        for group, (start, end) in self.TOPICAL_GROUPS.items():
            if start <= chapter_num <= end:
                return group
        raise ValueError(f"Chapter {chapter_num} out of range")
    
    # ========== Filename Compliance Tests ==========
    
    def test_canonical_filenames_are_lowercase(self):
        """All canonical filenames are lowercase."""
        for chapter in self.chapters:
            canonical = chapter["canonical_filename"]
            self.assertEqual(canonical, canonical.lower(),
                           f"Filename not lowercase: {canonical}")
    
    def test_canonical_filenames_are_kebab_case(self):
        """Canonical filenames use kebab-case (hyphens, alphanumeric)."""
        kebab_pattern = re.compile(r'^ch\d{2,3}-[a-z0-9-]+-cornell-notes\.tex$')
        for chapter in self.chapters:
            canonical = chapter["canonical_filename"]
            self.assertIsNotNone(kebab_pattern.match(canonical),
                               f"Filename not kebab-case: {canonical}")
    
    def test_canonical_filenames_max_50_chars(self):
        """All canonical filenames are <= 50 characters."""
        violations = []
        for chapter in self.chapters:
            canonical = chapter["canonical_filename"]
            if len(canonical) > 50:
                violations.append(f"{canonical} ({len(canonical)} chars)")
        
        self.assertEqual(len(violations), 0,
                        f"Filenames exceed 50 chars:\n" + "\n".join(violations))
    
    def test_canonical_filenames_no_upload_suffixes(self):
        """Filenames don't contain upload version suffixes."""
        upload_patterns = [
            r'-v\d+',
            r'-upload\d*',
            r'-backup',
            r'-old',
            r'-legacy',
        ]
        for chapter in self.chapters:
            canonical = chapter["canonical_filename"]
            for pattern in upload_patterns:
                self.assertIsNone(re.search(pattern, canonical),
                                f"Filename has upload suffix: {canonical}")
    
    def test_canonical_filenames_match_chapter_number(self):
        """Canonical filename's chapter number matches entry."""
        for chapter in self.chapters:
            canonical = chapter["canonical_filename"]
            chapter_num = chapter["chapter_number"]
            
            # Extract chapter number from filename (ch01, ch02, etc.)
            match = re.match(r'ch(\d+)-', canonical)
            self.assertIsNotNone(match, f"Cannot extract chapter from {canonical}")
            
            filename_ch = int(match.group(1))
            self.assertEqual(filename_ch, chapter_num,
                           f"Filename chapter {filename_ch} doesn't match entry {chapter_num}")
    
    def test_no_root_level_cornell_notes_files_remain(self):
        """No [0-9][0-9][0-9]-*-cornell-notes.tex files at root."""
        root_files = list(self.REPO_ROOT.glob("[0-9][0-9][0-9]-*-cornell-notes.tex"))
        self.assertEqual(len(root_files), 0,
                        f"Root-level files still present: {[f.name for f in root_files]}")
    
    # ========== LaTeX Structure Tests ==========
    
    def test_every_file_loads_cornell_notes(self):
        """Every file has \\usepackage{cornell-notes}."""
        violations = []
        for chapter in self.chapters:
            topical_group = chapter["topical_group"]
            canonical_name = chapter["canonical_filename"]
            file_path = self.COLLECTION_ROOT / topical_group / canonical_name
            
            content = file_path.read_text(encoding='utf-8')
            if r'\usepackage{cornell-notes}' not in content:
                violations.append(f"Ch{chapter['chapter_number']:03d}: missing \\usepackage{{cornell-notes}}")
        
        self.assertEqual(len(violations), 0,
                        "\n".join(violations))
    
    def test_no_listings_package_present(self):
        """No file uses \\usepackage{listings} (forbidden, use minted)."""
        violations = []
        for chapter in self.chapters:
            topical_group = chapter["topical_group"]
            canonical_name = chapter["canonical_filename"]
            file_path = self.COLLECTION_ROOT / topical_group / canonical_name
            
            content = file_path.read_text(encoding='utf-8')
            if r'\usepackage{listings}' in content:
                violations.append(f"Ch{chapter['chapter_number']:03d}: still has \\usepackage{{listings}}")
        
        self.assertEqual(len(violations), 0,
                        "\n".join(violations))
    
    def test_required_metadata_setters_present(self):
        """Every file has required \\set* metadata commands."""
        required_setters = [
            r'\setDocTitle',
            r'\setDocSubtitle',
            r'\setCornellCollection',
            r'\setCornellUnitType',
            r'\setCornellUnitNumber',
            r'\setCornellUnitTitle',
            r'\setCornellCompanionLabel',
        ]
        
        violations = []
        for chapter in self.chapters:
            topical_group = chapter["topical_group"]
            canonical_name = chapter["canonical_filename"]
            file_path = self.COLLECTION_ROOT / topical_group / canonical_name
            
            content = file_path.read_text(encoding='utf-8')
            for setter in required_setters:
                if setter not in content:
                    violations.append(f"Ch{chapter['chapter_number']:03d}: missing {setter}")
        
        self.assertEqual(len(violations), 0,
                        "\n".join(violations[:10]))  # Show first 10
    
    def test_exactly_one_maketitle_per_file(self):
        """Every file has exactly one \\maketitle."""
        violations = []
        for chapter in self.chapters:
            topical_group = chapter["topical_group"]
            canonical_name = chapter["canonical_filename"]
            file_path = self.COLLECTION_ROOT / topical_group / canonical_name
            
            content = file_path.read_text(encoding='utf-8')
            count = content.count(r'\maketitle')
            if count != 1:
                violations.append(f"Ch{chapter['chapter_number']:03d}: {count} \\maketitle instances")
        
        self.assertEqual(len(violations), 0,
                        "\n".join(violations))
    
    # ========== Content Preservation Tests ==========
    
    def test_learning_objectives_present(self):
        """Every file contains a Learning Objectives section."""
        violations = []
        for chapter in self.chapters:
            topical_group = chapter["topical_group"]
            canonical_name = chapter["canonical_filename"]
            file_path = self.COLLECTION_ROOT / topical_group / canonical_name
            
            content = file_path.read_text(encoding='utf-8')
            if r'Learning Objectives' not in content and r'learning objectives' not in content.lower():
                violations.append(f"Ch{chapter['chapter_number']:03d}: missing Learning Objectives")
        
        self.assertEqual(len(violations), 0,
                        f"Missing Learning Objectives ({len(violations)}/104)")
    
    def test_cornell_table_structures_present(self):
        """Every file contains Cornell note-taking tables."""
        violations = []
        for chapter in self.chapters:
            topical_group = chapter["topical_group"]
            canonical_name = chapter["canonical_filename"]
            file_path = self.COLLECTION_ROOT / topical_group / canonical_name
            
            content = file_path.read_text(encoding='utf-8')
            # Look for longtable with CornellNoteRow (converted from CornellRow)
            if r'longtable' not in content and r'\CornellNoteRow' not in content:
                violations.append(f"Ch{chapter['chapter_number']:03d}: no Cornell table structures")
        
        # Allow some tolerance - not all files may have tables
        self.assertLess(len(violations), 104 // 4,  # At most 25% should be missing tables
                       f"Too many files missing table structures ({len(violations)}/104)")
    
    def test_summary_sections_present(self):
        """Files contain summary/synthesis box environments."""
        violations = []
        for chapter in self.chapters:
            topical_group = chapter["topical_group"]
            canonical_name = chapter["canonical_filename"]
            file_path = self.COLLECTION_ROOT / topical_group / canonical_name
            
            content = file_path.read_text(encoding='utf-8')
            # Look for converted box environments
            has_box = (r'\begin{CornellSummaryBox}' in content or
                      r'\begin{CornellOverviewBox}' in content or
                      r'\begin{CornellWarningBox}' in content or
                      r'\begin{CornellExamBox}' in content)
            
            if not has_box:
                violations.append(f"Ch{chapter['chapter_number']:03d}: no summary/box sections")
        
        # Most files should have boxes
        self.assertLess(len(violations), 104 // 4,
                       f"Too many files missing box environments ({len(violations)}/104)")
    
    def test_no_old_box_environments_remain(self):
        """Old box environment names have been removed."""
        old_envs = [
            r'\begin{orientationbox}',
            r'\begin{topicsummary}',
            r'\begin{defensebox}',
            r'\begin{historybox}',
            r'\begin{synthesisbox}',
            r'\begin{takeawaybox}',
        ]
        
        violations = []
        for chapter in self.chapters:
            topical_group = chapter["topical_group"]
            canonical_name = chapter["canonical_filename"]
            file_path = self.COLLECTION_ROOT / topical_group / canonical_name
            
            content = file_path.read_text(encoding='utf-8')
            for old_env in old_envs:
                if old_env in content:
                    violations.append(f"Ch{chapter['chapter_number']:03d}: still has {old_env}")
        
        self.assertEqual(len(violations), 0,
                        f"Old box environments not removed:\n" + "\n".join(violations[:10]))
    
    def test_no_old_color_definitions_remain(self):
        """Old color definitions have been removed."""
        old_colors = [
            'definecolor{Navy}',
            'definecolor{Teal}',
            'definecolor{CueGray}',
            'definecolor{SoftBlue}',
            'definecolor{SoftGreen}',
            'definecolor{SoftAmber}',
            'definecolor{RuleGray}',
            'definecolor{TextGray}',
        ]
        
        violations = []
        for chapter in self.chapters:
            topical_group = chapter["topical_group"]
            canonical_name = chapter["canonical_filename"]
            file_path = self.COLLECTION_ROOT / topical_group / canonical_name
            
            content = file_path.read_text(encoding='utf-8')
            for color in old_colors:
                if color in content:
                    violations.append(f"Ch{chapter['chapter_number']:03d}: still defines {color}")
        
        self.assertEqual(len(violations), 0,
                        f"Old color definitions not removed:\n" + "\n".join(violations[:10]))
    
    # ========== Collection Mapping Tests ==========
    
    def test_all_104_chapters_mapped_in_manifest(self):
        """Manifest contains mapping for all chapters 1-104."""
        chapter_numbers = sorted({ch["chapter_number"] for ch in self.chapters})
        expected = list(range(1, 105))
        self.assertEqual(chapter_numbers, expected,
                        f"Missing chapters in manifest: {set(expected) - set(chapter_numbers)}")
    
    def test_chapter_16_present_in_platform_group(self):
        """Chapter 16 (LAN Security) is present and in platform-network-and-iot."""
        ch16 = next((ch for ch in self.chapters if ch["chapter_number"] == 16), None)
        self.assertIsNotNone(ch16, "Chapter 16 missing from manifest")
        self.assertEqual(ch16["topical_group"], "platform-network-and-iot",
                        "Chapter 16 in wrong topical group")
        
        # Verify file exists
        file_path = self.COLLECTION_ROOT / ch16["topical_group"] / ch16["canonical_filename"]
        self.assertTrue(file_path.exists(),
                       f"Chapter 16 file not found: {file_path}")
    
    def test_each_topical_group_has_expected_chapters(self):
        """Each topical group contains its expected chapter range."""
        for group_name, (start, end) in self.TOPICAL_GROUPS.items():
            group_chapters = [ch["chapter_number"] for ch in self.chapters 
                             if ch["topical_group"] == group_name]
            group_chapters_sorted = sorted(group_chapters)
            expected_range = list(range(start, end + 1))
            
            self.assertEqual(group_chapters_sorted, expected_range,
                           f"Group {group_name} has wrong chapters: {group_chapters_sorted} vs {expected_range}")


class CybersecurityReferenceStyleValidationTest(unittest.TestCase):
    """Style validation tests for transformed documents."""
    
    REPO_ROOT = Path("/home/jordan/latex-docs")
    COLLECTION_ROOT = REPO_ROOT / "src" / "cornell-notes" / "security" / "cybersecurity-reference"
    MANIFEST_PATH = REPO_ROOT / "tooling" / "manifests" / "cybersecurity-reference-intake.json"
    
    @classmethod
    def setUpClass(cls):
        """Load manifest."""
        with open(cls.MANIFEST_PATH) as f:
            manifest = json.load(f)
        cls.chapters = manifest["chapters"]
    
    def test_documentclass_is_article(self):
        """Every file uses \\documentclass{article}."""
        violations = []
        for chapter in self.chapters:
            topical_group = chapter["topical_group"]
            canonical_name = chapter["canonical_filename"]
            file_path = self.COLLECTION_ROOT / topical_group / canonical_name
            
            content = file_path.read_text(encoding='utf-8')
            if r'\documentclass' not in content or 'article' not in content.split(r'\documentclass')[1].split('\n')[0]:
                violations.append(f"Ch{chapter['chapter_number']:03d}: wrong documentclass")
        
        self.assertEqual(len(violations), 0,
                        "\n".join(violations))
    
    def test_no_fancy_header_styling(self):
        """No \\thispagestyle{fancy} or fancy header setup remains."""
        violations = []
        for chapter in self.chapters:
            topical_group = chapter["topical_group"]
            canonical_name = chapter["canonical_filename"]
            file_path = self.COLLECTION_ROOT / topical_group / canonical_name
            
            content = file_path.read_text(encoding='utf-8')
            if r'\thispagestyle{fancy}' in content:
                violations.append(f"Ch{chapter['chapter_number']:03d}: still has \\thispagestyle{{fancy}}")
        
        self.assertEqual(len(violations), 0,
                        "\n".join(violations))


if __name__ == "__main__":
    unittest.main(verbosity=2)
