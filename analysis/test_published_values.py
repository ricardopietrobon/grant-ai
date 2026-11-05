"""Verification test: the committed outputs match the manuscript.

Run with:  python analysis/test_published_values.py
This is deliberately dependency-free beyond the analysis requirements, so a
reviewer can check the numbers without a test framework.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

subprocess.run([sys.executable, os.path.join(HERE, "reproduce.py")], check=True)
R = json.load(open(os.path.join(ROOT, "outputs", "results.json")))

CLAIMS = {
    "299 institution-department records": R["records_total"] == 299,
    "152 distinct institutions": R["institutions_total"] == 152,
    "94 institutions searched": R["searched_total"] == 94,
    "51 named contacts": R["contacts_total"] == 51,
    "contact yield 54.3% overall": R["contact_yield_overall_pct"] == 54.3,
    "contact yield 67.7% in Internal Medicine": R["contact_yield_IM_pct"] == 67.7,
    "23 videoconferences": R["meetings"] == 23,
    "28 invitations with a recorded outcome": R["invitations_recorded"] == 28,
    "44 invitations issued": R["invitations_issued"] == 44,
    "28 invitation outcomes recorded": R["invitations_recorded"] == 28,
    "16 invitations awaiting a reply at census": R["awaiting_reply"] == 16,
    "6 of 23 agreed after a videoconference": (R["agree_after_meeting"], R["invited_after_meeting"]) == (6, 23),
    "0 of 21 agreed without one": (R["agree_cold"], R["invited_cold"]) == (0, 21),
    "all-invited agreement 26.1%": R["agreement_all_invited_pct"] == 26.1,
    "complete-case agreement 85.7%": R["agreement_complete_case_pct"] == 85.7,
    "upper bound on agreement 95.7%": R["agreement_upper_bound_pct"] == 95.7,
    "Fisher exact p = 0.022 on all invited": round(R["fisher_p"], 3) == 0.022,
    "Fisher exact p below 2e-05 complete case": R["fisher_p_complete_case"] < 2.0e-5,
    "Jeffreys CI after meeting 11.7 to 46.1": R["ci_meeting"] == [11.7, 46.1],
    "Jeffreys CI without meeting 0 to 11.1": R["ci_cold"] == [0.0, 11.1],
    "2 consents": R["consents"] == 2,
    "1 feedback iteration": R["feedback_iterations"] == 1,
    "6.7% of the 30-participant target": R["pct_of_target"] == 6.7,
    "189 days outreach to first consent": R["days_outreach_to_first_consent"] == 189,
    "111 days IRB to first consent": R["days_irb_to_first_consent"] == 111,
    "10 days draft to feedback": R["days_draft_to_feedback"] == 10,
    "66 fields, 13 forms, 8 timepoints": (R["crf_fields"], R["crf_forms"], R["crf_timepoints"]) == (66, 13, 8),
    "31 checks: 18 executed, 10 deferred, 3 unresolved": (
        R["checks_total"], R["checks_executed"], R["checks_deferred"], R["checks_unresolved"]) == (31, 18, 10, 3),
    "6 fields ever populated": R["fields_populated"] == 6,
    "12 forms never opened": R["forms_never_opened"] == 12,
}
bad = [k for k, ok in CLAIMS.items() if not ok]
for k, ok in CLAIMS.items():
    print(("PASS  " if ok else "FAIL  ") + k)
print(f"\n{len(CLAIMS) - len(bad)}/{len(CLAIMS)} manuscript claims verified")
sys.exit(1 if bad else 0)
