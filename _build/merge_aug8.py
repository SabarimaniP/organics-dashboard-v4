# -*- coding: utf-8 -*-
# Fold the "August Data for Dashboard Update" top-up (Aug 1-8 cohort+rolling exports) into _merged.
#
# The top-up overlaps the previous Aug 1-6 merge, so:
#   activity files -> de-duplicated on Activity Id (exact), union of both sides
#   leads          -> de-duplicated on Prospect ID keeping the earliest Created On
# The top-up is a cohort+rolling export (leads created Jun/Jul/Aug only), so it does NOT contain
# activity against older leads. That is why this is a UNION, never a replace: the base still holds
# 354 August call rows against pre-June leads that the top-up legitimately omits.
#
# No sales file was supplied with this top-up, so the sales master is left untouched.
# build_cube.py then runs unchanged against _merged via FUNNEL_DATA_DIR.
import pandas as pd, os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
MERGED = os.path.join(HERE, "_merged")
TOPUP = r"E:\Organics Numbers Update\August Data for Dashboard Update"
BACKUP = os.path.join(HERE, "_merged_pre_aug8")
dt = lambda s: pd.to_datetime(s, errors="coerce", dayfirst=True)

F_LEADS = "Created in Mar to Aug.xlsx"
F_CALLS = "Outbound phone call mar 4 to 1 aug 8pm.xlsx"
F_DB    = "demo booking 4 mar to 1 aug 8pm.xlsx"
F_DC    = "demo conducted 4 mar to 1 aug 8 pm.xlsx"
T_LEADS = "Leads Created - Aug 1 - 8 - Cohort + Rolling.xlsx"
T_CALLS = "Outbound Phone Call - Aug 1 - 8 - Cohort + Rolling.xlsx"
T_DB    = "Demo Booking - Aug 1 - 8 - Cohort + Rolling.xlsx"
T_DC    = "Demo Conducted - Aug 1 - 8 - Cohort + Rolling.xlsx"

print("=" * 88); print("FOLDING IN THE AUG 1-8 TOP-UP"); print("=" * 88)

os.makedirs(BACKUP, exist_ok=True)
for f in (F_LEADS, F_CALLS, F_DB, F_DC):
    src = os.path.join(MERGED, f)
    if os.path.exists(src) and not os.path.exists(os.path.join(BACKUP, f)):
        shutil.copy2(src, os.path.join(BACKUP, f))
print(f"backup of the pre-merge inputs -> {BACKUP}\n")

# ---------------------------------------------------------------- leads
o = pd.read_excel(os.path.join(MERGED, F_LEADS))
n = pd.read_excel(os.path.join(TOPUP, T_LEADS)).reindex(columns=o.columns)
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

print("\nsales master   NOT TOUCHED - no sales export supplied with this top-up")
print("=" * 88)
print("merged input set updated in:", MERGED)
