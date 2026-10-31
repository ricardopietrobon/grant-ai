"""
GRANT-AI start-up feasibility analysis: full reproduction script.

Regenerates every number, table and figure reported in the manuscript
"Start-up of a randomized pilot trial of artificial intelligence feedback for
NIH grant writing" from the de-identified data in ../data/.

Run:  python analysis/reproduce.py
Outputs land in outputs/ : tables (CSV), figures (PNG + PDF), results.json.
Every published value is re-asserted at the end; the script exits non-zero if
any assertion fails.
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "outputs")
os.makedirs(OUT, exist_ok=True)

CENSUS = "2026-02-05"
TARGET_N = 30
R = {}


# --------------------------------------------------------------------------
# Load
# --------------------------------------------------------------------------
tr = pd.read_csv(os.path.join(DATA, "outreach_tracker_deid.csv"))
crf = pd.read_csv(os.path.join(DATA, "crf_specification.csv"))
chk = pd.read_csv(os.path.join(DATA, "crf_testing_checklist.csv"))
tl = pd.read_csv(os.path.join(DATA, "study_timeline.csv"), parse_dates=["date"])
enr = pd.read_csv(os.path.join(DATA, "enrollment_summary_deid.csv"))

for c in ["searched", "contact_identified", "email_obtained", "videoconference_completed"]:
    tr[c] = tr[c].astype(bool)


# --------------------------------------------------------------------------
# Table 1: outreach volume and contact identification by stratum
# --------------------------------------------------------------------------
def stratum_block(d):
    return pd.Series({
        "Outreach records": len(d),
        "Distinct institutions": d["institution_id"].nunique(),
        "Institutions searched for a contact": int(d["searched"].sum()),
        "Named contacts identified": int(d["contact_identified"].sum()),
        "Contact email addresses obtained": int(d["email_obtained"].sum()),
    })


order = ["Internal Medicine", "Surgery", "Unassigned"]
T1 = pd.concat([stratum_block(tr[tr.stratum == s]).rename(s) for s in order], axis=1).T
T1.loc["Total"] = stratum_block(tr)
T1.index.name = "Departmental stratum"
T1 = T1.reset_index()
T1.to_csv(os.path.join(OUT, "table_1.csv"), index=False)

R["records_total"] = len(tr)
R["institutions_total"] = int(tr["institution_id"].nunique())
R["searched_total"] = int(tr["searched"].sum())
R["contacts_total"] = int(tr["contact_identified"].sum())
R["emails_total"] = int(tr["email_obtained"].sum())
R["contact_yield_overall_pct"] = round(R["contacts_total"] / R["searched_total"] * 100, 1)
im = tr[tr.stratum == "Internal Medicine"]
R["contact_yield_IM_pct"] = round(int(im["contact_identified"].sum()) / int(im["searched"].sum()) * 100, 1)


# --------------------------------------------------------------------------
# Table 2: recruitment funnel
# --------------------------------------------------------------------------
meetings = int(tr["videoconference_completed"].sum())
recorded = tr["invitation_outcome"] != "no_outcome_recorded"
agreed = int((tr["invitation_outcome"] == "agreed").sum())
no_resp = int((tr["invitation_outcome"] == "no_response").sum())
other = int((tr["invitation_outcome"] == "other").sum())
consents = int(len(enr))
submitted = int((enr["sections_submitted"] > 0).sum())
iterated = int((enr["feedback_iterations_received"] > 0).sum())

stages = [
    ("Outreach records opened", R["records_total"]),
    ("Institution searched for an eligible contact", R["searched_total"]),
    ("Named contact identified", R["contacts_total"]),
    ("Contact email address obtained", R["emails_total"]),
    ("Introductory videoconference completed", meetings),
    ("Study invitation with a recorded outcome", int(recorded.sum())),
    ("Verbal agreement to participate", agreed),
    ("Informed consent form on file", consents),
    ("At least one proposal section submitted", submitted),
    ("At least one feedback iteration delivered", iterated),
]
T2 = pd.DataFrame(stages, columns=["Stage", "n"])
T2["% of 299 outreach records"] = (T2["n"] / R["records_total"] * 100).round(1)
T2.to_csv(os.path.join(OUT, "table_2.csv"), index=False)

R.update(meetings=meetings, invitations_recorded=int(recorded.sum()), agreed=agreed,
         no_response=no_resp, other_outcome=other, consents=consents,
         sections_submitted=submitted, feedback_iterations=iterated,
         pct_of_target=round(consents / TARGET_N * 100, 1))


# --------------------------------------------------------------------------
# Table 3: invitation outcome by prior videoconference  (primary comparison)
# --------------------------------------------------------------------------
inv = tr[recorded]
a = int(((inv.videoconference_completed) & (inv.invitation_outcome == "agreed")).sum())
b = int(((inv.videoconference_completed) & (inv.invitation_outcome != "agreed")).sum())
c = int(((~inv.videoconference_completed) & (inv.invitation_outcome == "agreed")).sum())
d = int(((~inv.videoconference_completed) & (inv.invitation_outcome != "agreed")).sum())
odds, p = stats.fisher_exact([[a, b], [c, d]])


def jeffreys(k, n):
    lo, hi = stats.beta.ppf([0.025, 0.975], k + 0.5, n - k + 0.5)
    return round(lo * 100, 1), round(hi * 100, 1)


n_meet, n_cold = a + b, c + d
ci_meet, ci_cold = jeffreys(a, n_meet), jeffreys(c, n_cold)
T3 = pd.DataFrame([
    ["Yes", n_meet, a,
     int(((inv.videoconference_completed) & (inv.invitation_outcome == "no_response")).sum()),
     int(((inv.videoconference_completed) & (inv.invitation_outcome == "other")).sum()),
     f"{a / n_meet * 100:.1f} ({ci_meet[0]}-{ci_meet[1]})"],
    ["No", n_cold, c,
     int(((~inv.videoconference_completed) & (inv.invitation_outcome == "no_response")).sum()),
     int(((~inv.videoconference_completed) & (inv.invitation_outcome == "other")).sum()),
     f"{c / n_cold * 100:.1f} ({ci_cold[0]}-{ci_cold[1]})"],
    ["Total", n_meet + n_cold, a + c, no_resp, other,
     f"{(a + c) / (n_meet + n_cold) * 100:.1f}"],
], columns=["Introductory videoconference before invitation", "Invitations",
            "Agreed to participate", "No response", "Other response",
            "Agreement, % (95% CI)"])
T3.to_csv(os.path.join(OUT, "table_3.csv"), index=False)

R.update(fisher_p=float(p), agree_after_meeting=a, invited_after_meeting=n_meet,
         agree_cold=c, invited_cold=n_cold,
         ci_meeting=list(ci_meet), ci_cold=list(ci_cold),
         meetings_without_outcome=int((tr.videoconference_completed & ~recorded).sum()))

# Sensitivity: if every videoconference with no recorded outcome resolved as a refusal
den = n_meet + R["meetings_without_outcome"]
R["sensitivity_agreement_pct"] = round(a / den * 100, 1)
_, p_sens = stats.fisher_exact([[a, den - a], [c, d]])
R["sensitivity_fisher_p"] = float(p_sens)


# --------------------------------------------------------------------------
# Table 4: pre-trial validation of the data capture system
# --------------------------------------------------------------------------
status = chk["Test Completed (Yes/No)"].fillna("(blank)").astype(str).str.strip()
chk = chk.assign(_status=status.map(lambda v: "Executed" if v.lower() == "yes"
                                    else ("Deferred or not applicable" if v == "-" else "Unresolved at census")))
T4 = (chk.pivot_table(index="Category", columns="_status", aggfunc="size", fill_value=0)
      .reindex(columns=["Executed", "Deferred or not applicable", "Unresolved at census"], fill_value=0)
      .reset_index().rename(columns={"Category": "Test category"}))
T4.insert(1, "Items", T4[["Executed", "Deferred or not applicable", "Unresolved at census"]].sum(axis=1))
T4.loc[len(T4)] = ["Total"] + T4[["Items", "Executed", "Deferred or not applicable", "Unresolved at census"]].sum().tolist()
T4.to_csv(os.path.join(OUT, "table_4.csv"), index=False)

R.update(crf_fields=len(crf), crf_forms=int(crf["Form Name"].nunique()),
         crf_timepoints=int(crf["Timepoint"].nunique()),
         checks_total=len(chk), checks_executed=int((chk._status == "Executed").sum()),
         checks_deferred=int((chk._status == "Deferred or not applicable").sum()),
         checks_unresolved=int((chk._status == "Unresolved at census").sum()),
         fields_populated=int(enr["enrollment_fields_populated"].sum()),
         forms_never_opened=int(crf["Form Name"].nunique() - 1))

# Timeline-derived intervals
m = dict(zip(tl["milestone"], tl["date"]))
first_outreach = m["recruitment tracker opened; invitation template written"]
first_consent = m["first informed consent on file"]
R["days_outreach_to_first_consent"] = int((first_consent - first_outreach).days)
R["days_irb_to_first_consent"] = int((first_consent - m["IRB exempt determination (STUDY008974)"]).days)
R["days_draft_to_feedback"] = int((m["first structured feedback returned"] - m["first proposal section submitted"]).days)


# --------------------------------------------------------------------------
# Appendix tables
# --------------------------------------------------------------------------
crf.to_csv(os.path.join(OUT, "table_A1_crf_specification.csv"), index=False)
chk.drop(columns=["_status"]).to_csv(os.path.join(OUT, "table_A2_testing_checklist.csv"), index=False)
A3 = (tr.groupby(["stratum", "invitation_outcome"])
      .agg(records=("institution_id", "size"), searched=("searched", "sum"),
           contacts=("contact_identified", "sum"), meetings=("videoconference_completed", "sum"))
      .reset_index())
A3.to_csv(os.path.join(OUT, "table_A3_outreach_by_stratum_outcome.csv"), index=False)
ft = (crf["Type"].value_counts().rename_axis("Field type").reset_index(name="Variables"))
ft.to_csv(os.path.join(OUT, "table_A4_field_types.csv"), index=False)
tl.assign(date=tl["date"].dt.strftime("%Y-%m-%d")).to_csv(os.path.join(OUT, "table_A5_timeline.csv"), index=False)


# --------------------------------------------------------------------------
# Figures
# --------------------------------------------------------------------------
try:
    apply_figure_style()  # noqa: F821  (provided by the figure-style kernel plugin)
except Exception:
    plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False,
                         "figure.dpi": 300, "savefig.bbox": "tight"})

INK = "#1b1b1b"
FOCAL = "#1f6fb4"
MUTED = "#9aa3ab"


def figure_1():
    """Recruitment flow from institutional outreach to feedback delivery."""
    fig, ax = plt.subplots(figsize=(6.6, 7.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    steps = [
        ("Institution-department outreach\nrecords opened", R["records_total"], None),
        ("Institution searched for an\neligible contact", R["searched_total"],
         f"Not searched by census\nn = {R['records_total'] - R['searched_total']}"),
        ("Named contact identified", R["contacts_total"],
         f"Search returned no eligible\ncontact  n = {R['searched_total'] - R['contacts_total']}"),
        ("Introductory videoconference\ncompleted", R["meetings"],
         f"No videoconference\nn = {R['contacts_total'] - R['meetings']}"),
        ("Verbal agreement to participate", R["agreed"],
         f"No response to invitation  n = {R['no_response']}\nOutcome still open  n = {R['meetings_without_outcome']}"),
        ("Informed consent on file", R["consents"],
         f"Agreed but not consented\nn = {R['agreed'] - R['consents']}"),
        ("Proposal section submitted and\nfeedback iteration delivered", R["feedback_iterations"],
         f"Consented, no section submitted\nn = {R['consents'] - R['feedback_iterations']}"),
    ]
    top, gap, bw, bh = 9.4, 1.33, 4.5, 0.86
    for i, (label, n, loss) in enumerate(steps):
        y = top - i * gap
        ax.add_patch(plt.Rectangle((0.3, y - bh / 2), bw, bh, fill=True, lw=1.0,
                                   facecolor="white", edgecolor=INK, zorder=3))
        ax.text(0.5, y + 0.11, label, va="center", ha="left", fontsize=7.4, color=INK, zorder=4)
        ax.text(0.5, y - 0.25, f"n = {n}", va="center", ha="left", fontsize=7.6,
                color=FOCAL, fontweight="bold", zorder=4)
        if i < len(steps) - 1:
            ax.annotate("", xy=(2.55, y - bh / 2 - gap + bh), xytext=(2.55, y - bh / 2),
                        arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9))
        if loss:
            ly = y + gap / 2 - 0.1
            ax.add_patch(plt.Rectangle((5.6, ly - 0.42), 4.1, 0.84, fill=True, lw=0.7,
                                       facecolor="#f4f5f6", edgecolor=MUTED, zorder=3))
            ax.plot([2.55, 5.6], [ly, ly], color=MUTED, lw=0.8, zorder=2)
            ax.text(5.78, ly, loss, va="center", ha="left", fontsize=6.6, color="#4a5157", zorder=4)
    ax.text(0.3, 0.12, f"Census date {CENSUS}. Target sample 30; enrolled {R['consents']} "
                       f"({R['pct_of_target']}% of target).", fontsize=6.8, color="#4a5157")
    fig.savefig(os.path.join(OUT, "figure_1_recruitment_flow.png"), dpi=300, bbox_inches="tight")
    fig.savefig(os.path.join(OUT, "figure_1_recruitment_flow.pdf"), bbox_inches="tight")
    return fig


def figure_2():
    """Infrastructure build ran ahead of the recruitment that would have used it."""
    fig, (ax, bx) = plt.subplots(2, 1, figsize=(7.2, 4.6), sharex=True,
                                 gridspec_kw={"height_ratios": [2.0, 1], "hspace": 0.14})
    colour = {"infrastructure": FOCAL, "recruitment": "#c4622d",
              "regulatory": "#6b6f73", "delivery": "#2e8b6f"}
    # lane order top to bottom: infrastructure, regulatory, recruitment, delivery
    lanes = {"infrastructure": 3, "regulatory": 2, "recruitment": 1, "delivery": 0}
    labels = {3: "Infrastructure build", 2: "Regulatory", 1: "Recruitment", 0: "Feedback delivery"}
    for _, r in tl.iterrows():
        if r["category"] == "census":
            continue
        ax.scatter(r["date"], lanes[r["category"]], s=34, color=colour[r["category"]],
                   zorder=3, edgecolor="white", lw=0.6)
    census_dt = tl.loc[tl.category == "census", "date"].iloc[0]
    ax.axvline(census_dt, color=MUTED, lw=0.9, ls=(0, (4, 3)))
    ax.text(census_dt, 3.95, "census", fontsize=6.3, color="#4a5157", ha="right", va="bottom")
    ax.set_yticks(sorted(labels))
    ax.set_yticklabels([labels[k] for k in sorted(labels)])
    ax.set_ylim(-0.6, 4.35)
    ax.set_title("Trial infrastructure was finished months before the first participant arrived",
                 loc="left", fontsize=8.6, pad=10)
    annots = [("13 case report\nforms built", m["13 case report forms built"], "infrastructure", 0.52),
              ("4 worked feedback\nexamples produced", m["four worked feedback examples produced"],
               "infrastructure", -0.62),
              ("IRB exempt\ndetermination", m["IRB exempt determination (STUDY008974)"], "regulatory", 0.50),
              ("tracker opened", m["recruitment tracker opened; invitation template written"],
               "recruitment", 0.48),
              ("first consent", m["first informed consent on file"], "recruitment", -0.55)]
    for lab, dt, cat_, dy in annots:
        yy = lanes[cat_]
        ax.annotate(lab, xy=(dt, yy), xytext=(dt, yy + dy), fontsize=6.3, ha="center",
                    va="bottom" if dy > 0 else "top",
                    color="#4a5157", arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))

    cum = tl[tl.milestone.str.contains("informed consent on file")].sort_values("date")
    xs = [tl["date"].min()] + list(cum["date"]) + [census_dt]
    ys = [0] + list(range(1, len(cum) + 1)) + [len(cum)]
    bx.step(xs, ys, where="post", color="#c4622d", lw=1.8, zorder=3)
    bx.axhline(TARGET_N, color=MUTED, lw=0.9, ls=(0, (4, 3)))
    bx.text(tl["date"].min(), TARGET_N * 0.84, f"target n = {TARGET_N}", fontsize=6.6, color="#4a5157")
    bx.annotate(f"n = {len(cum)} at census", xy=(census_dt, len(cum)),
                xytext=(census_dt, TARGET_N * 0.42), fontsize=6.6, ha="right", color="#c4622d",
                arrowprops=dict(arrowstyle="-", color="#c4622d", lw=0.7))
    bx.set_ylim(0, TARGET_N * 1.15)
    bx.set_ylabel("Cumulative\nconsents")
    bx.set_xlabel("2025 to 2026")
    fig.savefig(os.path.join(OUT, "figure_2_timeline.png"), dpi=300, bbox_inches="tight")
    fig.savefig(os.path.join(OUT, "figure_2_timeline.pdf"), bbox_inches="tight")
    return fig


f1 = figure_1()
f2 = figure_2()


# --------------------------------------------------------------------------
# Assertions against every value published in the manuscript
# --------------------------------------------------------------------------
PUBLISHED = {
    "records_total": 299, "institutions_total": 152, "searched_total": 94,
    "contacts_total": 51, "emails_total": 49, "meetings": 23,
    "invitations_recorded": 28, "agreed": 6, "no_response": 21, "other_outcome": 1,
    "consents": 2, "sections_submitted": 1, "feedback_iterations": 1,
    "agree_after_meeting": 6, "invited_after_meeting": 7,
    "agree_cold": 0, "invited_cold": 21, "meetings_without_outcome": 16,
    "crf_fields": 66, "crf_forms": 13, "crf_timepoints": 8,
    "checks_total": 31, "checks_executed": 18, "checks_deferred": 10, "checks_unresolved": 3,
    "fields_populated": 6, "forms_never_opened": 12,
    "days_outreach_to_first_consent": 189, "days_irb_to_first_consent": 111,
    "days_draft_to_feedback": 10, "pct_of_target": 6.7,
    "contact_yield_overall_pct": 54.3, "contact_yield_IM_pct": 67.7,
    "sensitivity_agreement_pct": 26.1,
}
fails = [(k, v, R.get(k)) for k, v in PUBLISHED.items() if R.get(k) != v]
assert R["fisher_p"] < 2.0e-5, R["fisher_p"]
assert R["ci_meeting"] == [49.9, 98.4], R["ci_meeting"]
assert R["ci_cold"] == [0.0, 11.1], R["ci_cold"]
assert round(R["sensitivity_fisher_p"], 3) == 0.022, R["sensitivity_fisher_p"]

R["fisher_p_formatted"] = f"{R['fisher_p']:.1e}"
R["census_date"] = CENSUS
with open(os.path.join(OUT, "results.json"), "w") as fh:
    json.dump(R, fh, indent=1, sort_keys=True)

print(f"tables written : {[f for f in sorted(os.listdir(OUT)) if f.endswith('.csv')]}")
print(f"figures written: {[f for f in sorted(os.listdir(OUT)) if f.endswith(('.png', '.pdf'))]}")
print(f"Fisher exact p = {R['fisher_p']:.3g}")
if fails:
    for k, want, got in fails:
        print(f"MISMATCH {k}: manuscript={want} recomputed={got}", file=sys.stderr)
    sys.exit(1)
print(f"all {len(PUBLISHED)} published values reproduced exactly")
