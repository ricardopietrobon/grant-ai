# GRANT-AI: start-up feasibility analysis

Reproduction materials for the manuscript **"Start-up of a randomized pilot trial of
artificial intelligence feedback for NIH grant writing: outreach yield, data system
readiness, and the failure of cold invitation."**

GRANT-AI is a parallel-group randomized pilot trial comparing large language model
feedback against retrieval-augmented generation feedback for investigators drafting NIH
proposals (University of South Florida IRB STUDY008974, exempt determination 18 September
2025). The trial did not reach the sample at which its randomized comparison becomes
interpretable. This repository contains the de-identified start-up record and the single
script that regenerates every number, table and figure in the manuscript.

## Reproduce

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python analysis/reproduce.py
```

The script re-derives 33 published values from `data/` and exits non-zero if any one of
them fails to match the manuscript. Outputs land in `outputs/`.

## What is here

| Path | Contents |
|---|---|
| `data/outreach_tracker_deid.csv` | 299 institution-department outreach records, institution names replaced by salted SHA-256 surrogates, contact names and email addresses removed |
| `data/crf_specification.csv` | All 66 planned variables with type, parent form and study timepoint |
| `data/crf_testing_checklist.csv` | All 31 pre-trial validation checks with their recorded status |
| `data/study_timeline.csv` | 20 dated study milestones from file creation timestamps |
| `data/enrollment_summary_deid.csv` | Aggregate enrollment record for the two consented participants |
| `analysis/reproduce.py` | Single entry point: tables 1-4, appendix tables A.1-A.5, figures 1-2, `results.json` |
| `outputs/` | Generated artifacts, committed so the record is readable without running anything |

## De-identification

No participant, contact or institution is identifiable. Institution identity is replaced
by `INST-<8 hex>` from a salted SHA-256 digest; the salt is not published, so the mapping
cannot be inverted from this repository. Personal names, email addresses and free-text
notes from the operational tracker were dropped rather than masked. The two consented
participants appear only as aggregate counts and coarse demographic categories.

The consequence for reuse: institution-level linkage to external data is not possible
with these files. That is deliberate. The full tracker can be requested from the
corresponding author under a data use agreement.

## Reproducibility caveats

Three things in the manuscript are **not** reproducible from this repository, and are
documented rather than hidden:

1. **Timeline dates are file creation timestamps**, not logged events. They bound when
   work happened; they do not measure it.
2. **Blank cells in the operational tracker are treated as "not done," with one exception.**
   The study team confirmed that a blank in the invitation column, for a contact who completed a
   videoconference, records an invitation that was issued and never answered. Those 16 are counted
   as invitations issued and as non-responses. Blanks
   elsewhere still mean not done, so those denominators remain conservative.
3. **The feedback artifacts themselves** (one 772-word structured critique and four worked
   examples totalling 6,911 words) contain unpublished proposal content and are not
   included. Only their word counts and structure enter the analysis.

## Citation

See `CITATION.cff`.

## Coordination

This repository was created on 31 October 2026 as the reproducibility layer for the
Contemporary Clinical Trials submission. If you are another agent session or collaborator
working on GRANT-AI, read `COORDINATION.md` before creating a parallel repository.

## License

Code under MIT (`LICENSE`). Data files under CC BY 4.0 (`LICENSE-DATA`).
