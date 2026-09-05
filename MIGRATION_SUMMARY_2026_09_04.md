# Cybersecurity Reference Notes Rebuild Record

This record supersedes the earlier migration summary. The collection was
rechecked against the live worktree and rebuilt through the repository build
helper; structural tests alone are not treated as compilation evidence.

## Inventory

- Initial live collection: 104 `.tex` roots.
- Final collection: 104 roots, Chapters 1--104, in eight topical directories.
- Chapter 16 is present at
  `platform-network-and-iot/ch16-local-area-network-security-cornell-notes.tex`.
  The reported missing source was stale; the authoritative worktree contains
  it and the manifest maps it correctly.
- The collection remains source-anonymous and contains no source bibliographic
  metadata.

## Rebuild corrections

- All roots use standalone `article` documents and load `cornell-notes` as the
  only semantic family package.
- 775 raw cue-table blocks were converted to public `CornellNotesTable` and
  `CornellNoteRow` APIs. Analytical tables retain their own schemas.
- Practical checklists use `CornellChecklist`; self-test questions use
  `CornellRecallList`; answer keys retain explicit numbering.
- Human-readable title and unit metadata was normalized from the manifest.
- Fifteen mechanically truncated or malformed filenames were repaired with
  `git mv`, including six shortened again to satisfy the 50-character policy.
  The manifest and collection README were updated atomically.
- Preserved analytical tables use standard `\raggedright`; unsupported
  `\RaggedRight` commands were removed from the target collection.
- No target root contains `\CornellHeader`, old private boxes, local palette
  definitions, listings constructs, or legacy title renderers.
- The collection-specific `\CornellHeader` compatibility block was removed
  from `tooling/styles/latex/cornell-notes.sty`; no consumer remains.

## Build evidence

The canonical helper was inspected before invocation and run as:

```bash
python3 tooling/scripts/latex_build.py build-category \
  cornell-notes/security/cybersecurity-reference --jobs 4 \
  --output-dir /tmp/cybersecurity-reference-build/pdfs \
  --log-dir /tmp/cybersecurity-reference-build/logs \
  --artifact-dir /tmp/cybersecurity-reference-build/artifacts --clean-output
```

The final machine-readable summary reports 104 attempted, 104 succeeded, zero
failed, 104 PDFs, zero skipped, and `build_status: success`. Temporary build
summaries are in `/tmp/cybersecurity-reference-build/logs/`; PDFs are in
`/tmp/cybersecurity-reference-build/pdfs/`. Pages staging was verified under
`/tmp/cybersecurity-reference-pages/pdfs/cornell-notes/security/
cybersecurity-reference/` with 104 source-relative PDFs.

## Commands and tests

```bash
python3 -m unittest tests/test_cybersecurity_reference_collection.py -v
python3 -m unittest tests/test_style_migration.py -v
python3 tooling/scripts/style_migration.py --validate
python3 -m unittest tests/test_build_pipeline.py -v
python3 tooling/scripts/latex_build.py build-category cornell-notes/security/cybersecurity-reference --jobs 4 --output-dir /tmp/cybersecurity-reference-build/pdfs --log-dir /tmp/cybersecurity-reference-build/logs --artifact-dir /tmp/cybersecurity-reference-build/artifacts --clean-output
git diff --check
make list-roots
```

The dedicated collection suite passes all exact per-root checks. The shared
style migration suite passes all 41 tests. Any remaining repository-wide
validator findings are outside this collection and pre-existing.

## Visual QA

Representative compiled PDFs were inspected through a temporary local PDF
server. Chapter 16 and Chapter 86 showed the expected navy title page, white
content pages, normalized metadata, canonical repeated cue headers, readable
callout boxes, and safe table flow. The local environment did not provide a
PDF rasterizer for automated contact sheets, so no image artifacts were
created or retained.

## Remaining problems

- Introduced by this work: none known after the final 104-root successful
  build.
- Pre-existing: unrelated collections may retain repository-wide filename
  policy findings; they were not changed.
- Blocked by missing authoritative source material: none; Chapter 16 is
  present in the live worktree.