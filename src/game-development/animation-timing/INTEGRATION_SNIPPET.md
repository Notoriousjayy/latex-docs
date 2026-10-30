# Proposed `latex-docs` navigation changes (not applied upstream)

Under `src/game-development/README.md`, add a new subject collection row:

`| [Animation timing and game animation engineering](animation-timing/README.md) | 82 chapter guides; timing/dynamics references; labs, game-engine specifications, scorecards, printable working forms. | See package catalog |`

Under repository root `README.md` start-here navigation, add:

`| Study animation timing and playable character movement | [Animation Timing and Game Animation Engineering suite](src/game-development/animation-timing/README.md) |`

For each entry in `PAIR_REGISTER.json`, add a corresponding row to `catalog/template-blank-pairs.md` and the repository's current machine-readable pair registry. **Do not replace or rewrite** existing catalog entries: inspect the latest validators and append in their established format.
