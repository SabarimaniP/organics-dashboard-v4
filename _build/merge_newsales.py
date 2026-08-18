# -*- coding: utf-8 -*-
# Fold "Sales from 14 - 18.csv" into the sales master.
#
# This export is a different report from the sheets used before: it is a Sales Punch In ACTIVITY
# export, so it has Prospect Id / Lead Source / Grade and NOT Lead Link / Original Source /
# Updated Lead Source / Select Standard. Two consequences:
#
#   1. The signed-off (Original Source, Updated Lead Source) classifier cannot run on it - every
#      row would fail the organic-origin gate and pile into Rolling. So these rows are bucketed by
#      LEAD CREATION DATE instead: created in August -> cohort, created earlier -> rolling. The
#      bucket is written to _aug_creation_buckets.json and build_cube.py prefers it over the
#      source-based rule for exactly these leads. The 59 rows already signed off are untouched.
#
#   2. A synthetic Lead Link is built from Prospect Id. LeadID and Prospect ID are the same GUID,
#      so this keys identically to every existing row and costs nothing.
#
# Dedupe is on the lead, matching the rest of the pipeline (one sale per lead; the 244-row master
# holds 244 distinct leads). A lead already in the master is skipped, and a lead appearing twice
# inside the CSV is kept once at its EARLIEST sale date.
import pandas as pd, os, json, shutil, sys, re

HERE = os.path.dirname(os.path.abspath(__file__))
MERGED = os.path.join(HERE, "_merged")
TOPUP = r"E:\Organics Numbers Update\August Data for Dashboard Update"
CSV = os.path.join(TOPUP, "Sales from 14 - 18.csv")
F_SM = "Original Sales May, June, July.xlsx"
SM = os.path.join(MERGED, F_SM)
AUG1 = pd.Timestamp("2026-08-01")

pid = lambda s: s.astype(str).str.strip().str.lower()
W = 96
print("=" * W); print("FOLDING IN THE NEW SALES EXPORT"); print("=" * W)
print(f"  source: {os.path.basename(CSV)}")

n = pd.read_csv(CSV, encoding="utf-8-sig", dtype=str)
sm = pd.read_excel(SM)
print(f"  csv rows {len(n)}   master rows {len(sm)}   master cols {len(sm.columns)}")

# ---------------------------------------------------------------- keys and dates
n["_k"] = pid(n["Prospect Id"])
n["_sale"] = pd.to_datetime(n["Sale Date"], errors="coerce")          # ISO with AM/PM, already IST
n["_created"] = pd.to_datetime(n["Lead Created On"], errors="coerce")
if n["_sale"].isna().any():
    sys.exit(f"unparsable Sale Date: {n.loc[n['_sale'].isna(), 'Sale Date'].tolist()}")

sm_k = set(pid(sm["Lead Link"].astype(str).str.extract(r"LeadID=([0-9a-fA-F-]+)")[0]).dropna())

# ---------------------------------------------------------------- dedupe
before = len(n)
already = n[n["_k"].isin(sm_k)]
for _, r in already.iterrows():
    print(f"  skip (already in master): {r['Lead Name']}  {r['_sale']:%d %b %H:%M}  {r['_k']}")
n = n[~n["_k"].isin(sm_k)]

n = n.sort_values("_sale")
dup = n[n["_k"].duplicated(keep=False)]
for k, g in dup.groupby("_k"):
    print(f"  same lead twice in the csv: {g['Lead Name'].iloc[0]}  "
          f"{', '.join(f'{d:%d %b}' for d in g['_sale'])}  -> keeping earliest ({g['_sale'].min():%d %b})")
n = n.drop_duplicates("_k", keep="first")
print(f"  {before} csv rows -> {len(n)} new sales "
      f"(-{len(already)} already in master, -{len(dup) - dup['_k'].nunique() if len(dup) else 0} duplicate)")

# ---------------------------------------------------------------- bucket from creation date
n["_bk"] = n["_created"].ge(AUG1).map({True: 1, False: 2})
n.loc[n["_created"].isna(), "_bk"] = 2          # no creation date can never be cohort
coh = int((n["_bk"] == 1).sum())
print(f"\n  bucketed by LEAD CREATION DATE (cohort = created on/after {AUG1:%d %b %Y}):")
print(f"    cohort  {coh}")
print(f"    rolling {len(n) - coh}")

# ---------------------------------------------------------------- map onto the master schema
# Original Source is set to the BARE vocabulary the dashboard's ORIG_TO_SRC already understands,
# so the Source filter keeps working without touching that map. Anything non-organic is left as it
# is and lands in source "Other", exactly as a lead with that source would.
SRC_TO_BARE = {"il website": "Website", "website": "Website", "il surge": "Surge",
               "surge": "Surge", "learn (an)": "App", "learn an": "App", "learn app": "App",
               "app": "App"}
nz = lambda v: " ".join(str(v or "").strip().lower().split())

out = pd.DataFrame(index=n.index).reindex(columns=sm.columns)


def put(col, vals):
    if col in out.columns:
        out[col] = vals
    else:
        print(f"  !! master has no '{col}' column - skipped")


put("Lead Link", "?LeadID=" + n["_k"])
put("Sale Date", n["_sale"])
put("State", n["State"])
put("Select Standard", n["Grade"])
put("Original Source", [SRC_TO_BARE.get(nz(v), v) for v in n["Lead Source"]])
put("Updated Lead Source", n["Lead Source"])
put("Enter Customer Name", n["Lead Name"])

# The csv ABBREVIATES the revenue headers - "Collected Rev" against the master's
# "(Collected Revenue)". Mapping them by identical name silently left revenue blank on every new
# row, which is invisible in the sale counts and only shows up when someone asks for money.
# Master name on the left, csv name on the right, and never assume the two agree.
money = lambda s: pd.to_numeric(s.astype(str).str.replace(r"[^\d.\-]", "", regex=True),
                                errors="coerce")
for master_col, csv_col, conv in (
        ("Enter Sale value (Collected Revenue)", "Enter Sale value Collected Rev", money),
        ("Enter Sale value (Booking Revenue)",   "Enter Sale value (Booking Rev)",  money),
        ("Enter Customer mobile number",         "Phone Number",                    lambda s: s)):
    if csv_col in n.columns:
        put(master_col, conv(n[csv_col]))
    else:
        print(f"  !! csv has no {csv_col!r} - {master_col!r} left blank")

_rev = money(n["Enter Sale value Collected Rev"])
print(f"\n  collected revenue on the new rows: {int(_rev.notna().sum())}/{len(n)} priced, "
      f"total {_rev.sum():,.0f}")

print("\n  source mapping applied:")
for k, v in pd.Series([SRC_TO_BARE.get(nz(v), f"{v} (-> Other)") for v in n["Lead Source"]]).value_counts().items():
    print(f"    {k:<26} {v}")

# ---------------------------------------------------------------- dashboard source dimension
# Four rows carry a non-organic Lead Source (WhatsApp Chat, InMobious Leads, Performance
# Marketing). Left alone those fall into a phantom source "Other" that no LEAD ever occupies -
# every one of the 83k leads is IL Website / Learn App / IL Surge - so the funnel showed 0 leads
# against 4 sales. Resolve the channel in order of authority instead:
#
#   1. the lead's OWN Lead Source from the leads export   (independently confirms 3 of the 4)
#   2. the csv's Lead Source.1, which is organic on every row
#   3. the csv's Lead Source
#
# This is carried in the sidecar rather than written into Original Source, so sale_class, the
# weekly views and the audit trail of what the sheet actually said all stay untouched.
def _dash_src(v):
    s = str(v or "").lower()
    if "learn" in s:   return "Learn App"
    if "surge" in s:   return "IL Surge"
    if "website" in s: return "IL Website"
    return "Other"


_L = pd.read_excel(os.path.join(MERGED, "Created in Mar to Aug.xlsx"),
                   usecols=["Prospect ID", "Lead Source"])
_lsrc = _L.assign(_k=pid(_L["Prospect ID"])).drop_duplicates("_k").set_index("_k")["Lead Source"]

resolved, origin_of = {}, {}
for _, r in n.iterrows():
    for cand, lab in ((_lsrc.get(r["_k"]), "lead export"),
                      (r.get("Lead Source.1"), "Lead Source.1"),
                      (r.get("Lead Source"), "Lead Source")):
        g = _dash_src(cand)
        if g != "Other":
            resolved[r["_k"]] = g
            origin_of[r["_k"]] = lab
            break
    else:
        resolved[r["_k"]] = "Other"
        origin_of[r["_k"]] = "unresolved"

print("\n  dashboard source resolved to:")
for k, v in pd.Series(list(resolved.values())).value_counts().items():
    print(f"    {k:<26} {v}")
print("  resolved from:")
for k, v in pd.Series(list(origin_of.values())).value_counts().items():
    print(f"    {k:<26} {v}")
_still = sum(1 for v in resolved.values() if v == "Other")
print(f"  sales still falling into 'Other': {_still}"
      + ("  <- none, the phantom source is gone" if _still == 0 else "  !! check these"))

# ---------------------------------------------------------------- write
shutil.copy2(SM, SM.replace(".xlsx", "_pre_newsales.xlsx"))
merged = pd.concat([sm, out], ignore_index=True)
if len(merged.columns) != len(sm.columns):
    sys.exit(f"schema drift: {len(sm.columns)} -> {len(merged.columns)}")
merged.to_excel(SM, index=False)
print(f"\n  master {len(sm)} -> {len(merged)} rows, {len(merged.columns)} cols (schema unchanged)")

# sidecar: the August scope must become the UNION, or the 1-12 Aug sales drop out of August
kf = os.path.join(MERGED, "_aug_sale_keys.json")
old_keys = set(json.load(open(kf))) if os.path.exists(kf) else set()
new_keys = sorted(old_keys | set(n["_k"]))
json.dump(new_keys, open(kf, "w"))
print(f"  _aug_sale_keys.json {len(old_keys)} -> {len(new_keys)} keys")

bf = os.path.join(MERGED, "_aug_creation_buckets.json")
json.dump({k: {"bk": int(b), "src": resolved[k]} for k, b in zip(n["_k"], n["_bk"])},
          open(bf, "w"))
print(f"  _aug_creation_buckets.json written with {len(n)} lead -> bucket + source entries")
print("=" * W)
