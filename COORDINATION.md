# Coordination notes

**Status as of 31 October 2026.** This repository is the single reproducibility layer for
the GRANT-AI start-up feasibility manuscript. It was created after confirming that no
repository named `grant-ai` existed on the account and that no repository had been pushed
to in the preceding seven days.

A second, concurrent working session was known to be addressing the same task. To avoid
duplicate repositories:

- **Do not create `grant-ai-reproducibility`, `grantai`, or similar.** Add to this one.
- The analysis entry point is `analysis/reproduce.py`. It is deliberately a single file
  with assertions against every published value; extend it rather than adding a parallel
  pipeline.
- Manuscript text lives in `manuscript/`. The authoritative copy during drafting is the
  Word document delivered to the corresponding author; this directory holds the preprint
  build and the supplementary appendix.
- If you need to change a published number, change it in `PUBLISHED` inside
  `analysis/reproduce.py` in the same commit, so the assertion block stays honest.

**Open items not handled here.**

- The trial has no public registry record. medRxiv requires a trial registration ID for
  clinical trials, so a medRxiv preprint is blocked until the trial is registered.
  arXiv has no such requirement.
- The 16 contacts who completed a videoconference with no recorded invitation outcome
  remain unresolved. Resolving them changes Table 3 and the sensitivity analysis.

## Build state at first push

- `analysis/reproduce.py` -> 34 published values re-derived, exit 0.
- `analysis/test_published_values.py` -> 24/24 manuscript claims PASS.
- Manuscript: 3,415 words (limit 4,000), 238-word abstract (limit 250), 44 references
  (limit 75), 4 tables, 2 figures, supplementary Tables A.1-A.6 plus Appendices A.7-A.9.
- `manuscript/arxiv/main.tex` was validated structurally (balanced environments, 44/44
  cite keys resolved, both figure files present, no unescaped specials outside tabulars).
  It was **not compiled locally**: the build environment has TeX binaries but no LaTeX
  macro tree, so no format file can be generated. arXiv compiles submitted source itself.
