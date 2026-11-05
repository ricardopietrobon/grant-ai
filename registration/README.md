# Registering GRANT-AI on ClinicalTrials.gov

`GRANT-AI_PRS_record.xml` is a complete, schema-valid PRS protocol record. It validates against
ClinicalTrials.gov's own `ProtocolRecordSchema.xsd` (fetched 5 November 2026), so the PRS will
accept it as an upload rather than requiring the fields to be typed.

## Who has to do what

Registration is gated by institution, not by API. The responsible party for STUDY008974 is the
University of South Florida, with Paul Kuo as principal investigator. Nobody outside USF's PRS
organization account can create this record.

1. **USF PRS administrator** logs in at register.clinicaltrials.gov and uses the PRS upload
   function to create a new record from this XML file. One file picker, not forty fields.
2. **Paul Kuo**, as responsible party, reviews the record and clicks **Release**. This step is a
   legal attestation that the information is accurate and cannot be delegated to a script or
   performed by anyone else.
3. **NLM PRS review** follows, typically 2 to 5 business days, and may return comments to address.

An organization with its own PRS account can also request API credentials and POST the XML
directly. For a single record that is more setup than it saves; the manual upload in step 1 takes
about two minutes.

## Decide before release

Three fields encode judgements rather than facts, and the record is permanent once posted.

- `overall_status` is set to **Terminated** with `why_stopped` of "Enrollment rate insufficient to
  reach the planned sample size". That matches what the manuscript reports. If the team considers
  the trial still open, change it to "Active, not recruiting" or "Recruiting" and remove
  `why_stopped`.
- `enrollment` is **2, Actual**. Correct as of the 5 February 2026 census; update if anyone
  consented after that date.
- `interventional_subtype` is **Health Services Research**. "Other" is defensible as well, since
  participants are investigators rather than patients.

## Retrospective registration

The start date (7 January 2026, first consent) precedes registration, so this is a retrospective
registration and ClinicalTrials.gov will display it as such. That is unavoidable now and is
disclosed in the manuscript rather than hidden. Registering still removes the reviewer objection
that no registry record exists at all, and it unblocks a medRxiv preprint, which refuses clinical
trials without a registration ID.

## What is in the record

Primary outcomes (3): recruitment yield; proportion submitting all three core sections within 90
days; blinded reviewer quality ratings on the 1-9 NIH scale. Secondary outcomes (4): platform
engagement, formal NIH submission, NIH peer review outcome, participant-reported acceptability.
Two arms, behavioral interventions, randomized parallel assignment, outcomes assessor masked,
eligibility criteria transcribed from the protocol, IRB exempt determination recorded, and an
IPD sharing statement pointing at the reproducibility archive.
