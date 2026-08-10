# -*- coding: utf-8 -*-
# Fold the Aug 1-10 top-up exports into _merged.
#
#   activity files -> de-duplicated on Activity Id, union of both sides
#   leads          -> de-duplicated on Prospect ID keeping the earliest Created On
#   sales master   -> de-duplicated on the LeadID inside Lead Link, master wins on collision
#
# The top-up is a cohort+rolling export (leads created Jun/Jul/Aug only), so it does NOT contain
# activity against older leads. Union, never replace, or the base's August activity against
# pre-June leads is silently lost.
#
# The Aug leads export carries three extra columns (Target Exam 1 / Target Exam_ report /
# Primary Target Exam) that the base does not; reindex to the base column order drops them.
import pandas as pd, os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
MERGED = os.path.join(HERE, "_merged")
TOPUP = r"E:\Organics Numbers Update\August Data for Dashboard Update"
BACKUP = os.path.join(HERE, "_merged_pre_aug10")
dt = lambda s: pd.to_datetime(s, errors="coerce", dayfirst=True)

F_LEADS = "Created in Mar to Aug.xlsx"
F_CALLS = "Outbound phone call mar 4 to 1 aug 8pm.xlsx"
F_DB    = "demo booking 4 mar to 1 aug 8pm.xlsx"
F_DC    = "demo conducted 4 mar to 1 aug 8 pm.xlsx"
F_SM    = "Original Sales May, June, July.xlsx"
T_LEADS = "Leads Created - Aug 1 - 10 - Cohort + Rolling.xlsx"
T_CALLS = "Outbound Phone Call - Aug 1 - 10 - Cohort + Rolling.xlsx"
T_DB    = "Demo Booking - Aug 1 - 10 - Cohort + Rolling.xlsx"
T_DC    = "Demo Conducted - Aug 1 - 10 - Cohort + Rolling.xlsx"
T_SM    = "Original Sales Aug 1 - 10.xlsx"

print("=" * 90); print("FOLDING IN THE AUG 1-10 TOP-UP"); print("=" * 90)

os.makedirs(BACKUP, exist_ok=True)
for f in (F_LEADS, F_CALLS, F_DB, F_DC, F_SM):
    src = os.path.join(MERGED, f)
    if os.path.exists(src) and not os.path.exists(os.path.join(BACKUP, f)):
        shutil.copy2(src, os.path.join(BACKUP, f))
print(f"backup of the pre-merge inputs -> {BACKUP}\n")

# ---------------------------------------------------------------- leads
o = pd.read_excel(os.path.join(MERGED, F_LEADS))
n = pd.read_excel(os.path.join(TOPUP, T_LEADS))
extra = [c for c in n.columns if c not in o.columns]
if extra:
    print(f"leads          dropping {len(extra)} column(s) not in the base schema: {extra}")
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
    print(f"{label:<15}base {before:>7,} + topup {len(n):>6,} -> {len(m):>7,}   added {len(m)-before:,}"
          f"   duplicate Activity Ids dropped {before+len(n)-len(m):,}")
    print(f"               {datecol} up to {dt(m[datecol]).max()}")
    m.to_excel(os.path.join(MERGED, basefile), index=False)

merge_act(F_CALLS, T_CALLS, "Start Time",    "calls")
merge_act(F_DB,    T_DB,    "Activity Date", "demo booked")
merge_act(F_DC,    T_DC,    "Activity Date", "demo conducted")

# ---------------------------------------------------------------- sales master
# Every row is appended; build_cube.py applies the organic-source filter and the
# lead-must-exist filter downstream, so no pre-filtering happens here.
o = pd.read_excel(os.path.join(MERGED, F_SM))
n = pd.read_excel(os.path.join(TOPUP, T_SM)).reindex(columns=o.columns)
before = len(o)
m = pd.concat([o, n], ignore_index=True)
k = m["Lead Link"].astype(str).str.extract(r"LeadID=([0-9a-fA-F-]+)")[0].str.lower()
m = m.loc[~k.duplicated(keep="first")]          # master rows come first, so they win
sd = pd.to_datetime(m["Sale Date"], format="%d-%b-%y", errors="coerce").fillna(dt(m["Sale Date"]))
print(f"sales master   base {before:>7,} + topup {len(n):>6,} -> {len(m):>7,}   added {len(m)-before:,}")
print(f"               sale dates {sd.min():%d %b} .. {sd.max():%d %b}")
print(f"               by month: {dict(sd.dt.to_period('M').value_counts().sort_index())}")
m.to_excel(os.path.join(MERGED, F_SM), index=False)

print("=" * 90)
print("merged input set updated in:", MERGED)
