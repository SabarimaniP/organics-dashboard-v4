# -*- coding: utf-8 -*-
# Fold the Aug 1-12 top-up into _merged, including the reclassified sales sheet.
#
#   leads / activity -> union, de-duplicated on Prospect ID / Activity Id
#   sales            -> "Updated Sales 1 - 12.xlsx" is the new authority on HOW a sale is
#                       classified. For rows already in the master, only `Original Source` and
#                       `Updated Lead Source` are overwritten (the master keeps its own Sale Date,
#                       phones etc). Rows not in the master are appended whole.
#
# The top-up is cohort+rolling only, so it omits activity against pre-June leads. Union, never
# replace, or the base's August activity against older leads is lost.
import pandas as pd, os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
MERGED = os.path.join(HERE, "_merged")
TOPUP = r"E:\Organics Numbers Update\August Data for Dashboard Update"
BACKUP = os.path.join(HERE, "_merged_pre_aug12")
dt = lambda s: pd.to_datetime(s, errors="coerce", dayfirst=True)
key = lambda x: x.astype(str).str.extract(r"LeadID=([0-9a-fA-F-]+)")[0].str.lower()

F_LEADS = "Created in Mar to Aug.xlsx"
F_CALLS = "Outbound phone call mar 4 to 1 aug 8pm.xlsx"
F_DB    = "demo booking 4 mar to 1 aug 8pm.xlsx"
F_DC    = "demo conducted 4 mar to 1 aug 8 pm.xlsx"
F_SM    = "Original Sales May, June, July.xlsx"
T_LEADS = "Leads Created - Aug 1 - 12 - Cohort + Rolling.xlsx"
T_CALLS = "Outbound Phone Call - Aug 1 - 12 Cohort + Rolling.xlsx"
T_DB    = "Demo Booking - Aug 1 - 12 - Cohort + Rolling.xlsx"
T_DC    = "Demo Conducted - Aug 1 - 12 Cohort + Rolling.xlsx"
T_SM    = "Updated Sales 1 - 12.xlsx"

print("=" * 92); print("FOLDING IN THE AUG 1-12 TOP-UP"); print("=" * 92)
os.makedirs(BACKUP, exist_ok=True)
for f in (F_LEADS, F_CALLS, F_DB, F_DC, F_SM):
    src = os.path.join(MERGED, f)
    if os.path.exists(src) and not os.path.exists(os.path.join(BACKUP, f)):
        shutil.copy2(src, os.path.join(BACKUP, f))
print(f"backup -> {BACKUP}\n")

# ---------------------------------------------------------------- leads
o = pd.read_excel(os.path.join(MERGED, F_LEADS))
n = pd.read_excel(os.path.join(TOPUP, T_LEADS))
extra = [c for c in n.columns if c not in o.columns]
if extra: print(f"leads          dropping columns absent from the base schema: {extra}")
n = n.reindex(columns=o.columns)
before = len(o)
m = pd.concat([o, n], ignore_index=True)
m["_c"] = dt(m["Created On"])
m = m.sort_values("_c").drop_duplicates("Prospect ID", keep="first").drop(columns="_c")
print(f"leads          base {before:>7,} + topup {len(n):>6,} -> {len(m):>7,}   added {len(m)-before:,}")
print(f"               created up to {dt(m['Created On']).max()}")
m.to_excel(os.path.join(MERGED, F_LEADS), index=False)

# ---------------------------------------------------------------- activity
def merge_act(basefile, topfile, datecol, label):
    o = pd.read_excel(os.path.join(MERGED, basefile))
    n = pd.read_excel(os.path.join(TOPUP, topfile)).reindex(columns=o.columns)
    before = len(o)
    m = pd.concat([o, n], ignore_index=True).drop_duplicates("Activity Id", keep="first")
    print(f"{label:<15}base {before:>7,} + topup {len(n):>6,} -> {len(m):>7,}   added {len(m)-before:,}")
    print(f"               {datecol} up to {dt(m[datecol]).max()}")
    m.to_excel(os.path.join(MERGED, basefile), index=False)

merge_act(F_CALLS, T_CALLS, "Start Time",    "calls")
merge_act(F_DB,    T_DB,    "Activity Date", "demo booked")
merge_act(F_DC,    T_DC,    "Activity Date", "demo conducted")

# ---------------------------------------------------------------- sales
o = pd.read_excel(os.path.join(MERGED, F_SM))
s = pd.read_excel(os.path.join(TOPUP, T_SM), sheet_name=0)
missing = [c for c in o.columns if c not in s.columns]
if missing: print(f"sales          sheet lacks {len(missing)} master column(s), filled blank: {missing}")
s = s.reindex(columns=o.columns)
o["_k"] = key(o["Lead Link"]); s["_k"] = key(s["Lead Link"])
before = len(o)

# overlapping rows: take ONLY the sheet's two classification columns
overlap = set(o["_k"].dropna()) & set(s["_k"].dropna())
srcmap = s.set_index("_k")[["Original Source", "Updated Lead Source"]]
hit = o["_k"].isin(overlap)
o.loc[hit, "Original Source"]      = o.loc[hit, "_k"].map(srcmap["Original Source"])
o.loc[hit, "Updated Lead Source"]  = o.loc[hit, "_k"].map(srcmap["Updated Lead Source"])
print(f"sales          reclassified {len(overlap)} existing row(s) from the sheet")

fresh = s[~s["_k"].isin(overlap)].drop(columns="_k")
out = pd.concat([o.drop(columns="_k"), fresh], ignore_index=True)
k = key(out["Lead Link"])
out = out.loc[~k.duplicated(keep="first")]
sd = pd.to_datetime(out["Sale Date"], format="%d-%b-%y", errors="coerce").fillna(dt(out["Sale Date"]))
print(f"               {before} -> {len(out)}   appended {len(fresh)}")
print(f"               columns {len(out.columns)}   sale dates {sd.min():%d %b} .. {sd.max():%d %b}")
print(f"               August rows: {int(((sd >= pd.Timestamp('2026-08-01')) & (sd <= pd.Timestamp('2026-08-12'))).sum())}")
out.to_excel(os.path.join(MERGED, F_SM), index=False)

print("=" * 92)
print("merged input set updated in:", MERGED)
