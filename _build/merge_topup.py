# -*- coding: utf-8 -*-
# Fold the latest top-up exports into _merged. Supersedes merge_aug8/10/12.py, which each hardcoded
# one round's filenames; this one discovers them by role so a new round needs no new script.
#
#   leads / activity -> union, de-duplicated on Prospect ID / Activity Id
#   sales            -> the sheet is the authority on HOW a sale is classified. For rows already in
#                       the master only `Original Source` and `Updated Lead Source` are overwritten;
#                       the master keeps its own Sale Date, phones and the rest. New rows are
#                       appended whole. Its LeadIDs go to _aug_sale_keys.json so build_cube can
#                       scope the August buckets to exactly the sheet's rows.
#
# The top-up is cohort+rolling only, so it omits activity against pre-June leads. Union, never
# replace, or the base's August activity against older leads is lost.
import pandas as pd, os, shutil, glob, json, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MERGED = os.path.join(HERE, "_merged")
TOPUP = r"E:\Organics Numbers Update\August Data for Dashboard Update"
dt = lambda s: pd.to_datetime(s, errors="coerce", dayfirst=True)
key = lambda x: x.astype(str).str.extract(r"LeadID=([0-9a-fA-F-]+)")[0].str.lower()

F_LEADS = "Created in Mar to Aug.xlsx"
F_CALLS = "Outbound phone call mar 4 to 1 aug 8pm.xlsx"
F_DB    = "demo booking 4 mar to 1 aug 8pm.xlsx"
F_DC    = "demo conducted 4 mar to 1 aug 8 pm.xlsx"
F_SM    = "Original Sales May, June, July.xlsx"

def pick(*must, avoid=()):
    """the newest top-up file whose name contains every `must` token and no `avoid` token"""
    hits = []
    for p in glob.glob(os.path.join(TOPUP, "*.xlsx")):
        n = os.path.basename(p).lower()
        if n.startswith("~$"): continue
        if all(m in n for m in must) and not any(a in n for a in avoid):
            hits.append(p)
    if not hits:
        sys.exit(f"no top-up file matching {must!r} in {TOPUP}")
    return max(hits, key=os.path.getmtime)

ROLES = {"leads":     pick("leads", "created"),
         "calls":     pick("outbound"),
         "booked":    pick("demo booking"),
         "conducted": pick("demo conducted"),
         "sales":     pick("sales")}

print("=" * 94); print("FOLDING IN THE LATEST TOP-UP"); print("=" * 94)
for r, p in ROLES.items():
    print(f"  {r:<10} {os.path.basename(p)}")
print()

BACKUP = os.path.join(HERE, "_merged_pre_" + pd.Timestamp.fromtimestamp(
    os.path.getmtime(ROLES['leads'])).strftime("%m%d"))
os.makedirs(BACKUP, exist_ok=True)
for f in (F_LEADS, F_CALLS, F_DB, F_DC, F_SM):
    src = os.path.join(MERGED, f)
    if os.path.exists(src) and not os.path.exists(os.path.join(BACKUP, f)):
        shutil.copy2(src, os.path.join(BACKUP, f))
print(f"backup -> {BACKUP}\n")

# ---------------------------------------------------------------- leads
o = pd.read_excel(os.path.join(MERGED, F_LEADS))
n = pd.read_excel(ROLES["leads"])
extra = [c for c in n.columns if c not in o.columns]
if extra: print(f"leads          dropping columns absent from the base schema: {extra}")
n = n.reindex(columns=o.columns)
before = len(o)
# On a clash the TOP-UP wins: it is the fresher export and may carry a corrected State or Owner.
# Sorting on (_c, _src) makes that deterministic, so re-running this script is a no-op.
o["_src"], n["_src"] = 1, 0
m = pd.concat([o, n], ignore_index=True)
m["_c"] = dt(m["Created On"])
m = (m.sort_values(["_c", "_src"]).drop_duplicates("Prospect ID", keep="first")
      .drop(columns=["_c", "_src"]))
print(f"leads          base {before:>7,} + topup {len(n):>6,} -> {len(m):>7,}   added {len(m)-before:,}")
print(f"               created up to {dt(m['Created On']).max()}")
m.to_excel(os.path.join(MERGED, F_LEADS), index=False)

# ---------------------------------------------------------------- activity
def merge_act(basefile, role, datecol, label):
    o = pd.read_excel(os.path.join(MERGED, basefile))
    n = pd.read_excel(ROLES[role]).reindex(columns=o.columns)
    before = len(o)
    m = pd.concat([o, n], ignore_index=True).drop_duplicates("Activity Id", keep="first")
    print(f"{label:<15}base {before:>7,} + topup {len(n):>6,} -> {len(m):>7,}   added {len(m)-before:,}")
    print(f"               {datecol} up to {dt(m[datecol]).max()}")
    m.to_excel(os.path.join(MERGED, basefile), index=False)

merge_act(F_CALLS, "calls",     "Start Time",    "calls")
merge_act(F_DB,    "booked",    "Activity Date", "demo booked")
merge_act(F_DC,    "conducted", "Activity Date", "demo conducted")

# ---------------------------------------------------------------- sales
o = pd.read_excel(os.path.join(MERGED, F_SM))
s = pd.read_excel(ROLES["sales"], sheet_name=0)
missing = [c for c in o.columns if c not in s.columns]
if missing: print(f"sales          sheet lacks {len(missing)} master column(s), filled blank: {missing}")
s = s.reindex(columns=o.columns)
o["_k"] = key(o["Lead Link"]); s["_k"] = key(s["Lead Link"])
before = len(o)

overlap = set(o["_k"].dropna()) & set(s["_k"].dropna())
srcmap = s.drop_duplicates("_k").set_index("_k")[["Original Source", "Updated Lead Source"]]
hit = o["_k"].isin(overlap)
o.loc[hit, "Original Source"]     = o.loc[hit, "_k"].map(srcmap["Original Source"])
o.loc[hit, "Updated Lead Source"] = o.loc[hit, "_k"].map(srcmap["Updated Lead Source"])
print(f"sales          reclassified {len(overlap)} existing row(s) from the sheet")

fresh = s[~s["_k"].isin(overlap)].drop(columns="_k")
out = pd.concat([o.drop(columns="_k"), fresh], ignore_index=True)
k = key(out["Lead Link"])
out = out.loc[~k.duplicated(keep="first")]
sd = pd.to_datetime(out["Sale Date"], format="%d-%b-%y", errors="coerce").fillna(dt(out["Sale Date"]))
print(f"               {before} -> {len(out)}   appended {len(fresh)}")
print(f"               columns {len(out.columns)}   sale dates {sd.min():%d %b} .. {sd.max():%d %b}")
out.to_excel(os.path.join(MERGED, F_SM), index=False)

sheet_keys = sorted(set(k for k in s["_k"].dropna()))
with open(os.path.join(MERGED, "_aug_sale_keys.json"), "w") as fh:
    json.dump(sheet_keys, fh)
print(f"               wrote _aug_sale_keys.json with {len(sheet_keys)} sheet LeadIDs")

print("=" * 94)
print("merged input set updated in:", MERGED)
