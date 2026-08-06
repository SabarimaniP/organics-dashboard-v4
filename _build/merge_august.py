# -*- coding: utf-8 -*-
# Fold the August top-up exports into the base exports and write a complete input set to _merged\.
# The top-ups overlap 1 August, so every activity file is de-duplicated on Activity Id (exact),
# and leads are de-duplicated on Prospect ID keeping the earliest Created On.
# build_cube.py then runs unchanged against _merged via FUNNEL_DATA_DIR.
import pandas as pd, os, shutil

BASE = r"E:\Organics Numbers Update\Orignal updated data"
AUG  = r"E:\Organics Numbers Update\Created on June, July, Aug activities in aug"
OUT  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_merged")
os.makedirs(OUT, exist_ok=True)
dt = lambda s: pd.to_datetime(s, errors="coerce", dayfirst=True)

F_LEADS = "Created in Mar to Aug.xlsx"
F_CALLS = "Outbound phone call mar 4 to 1 aug 8pm.xlsx"
F_DB    = "demo booking 4 mar to 1 aug 8pm.xlsx"
F_DC    = "demo conducted 4 mar to 1 aug 8 pm.xlsx"
F_SM    = "Original Sales May, June, July.xlsx"
A_LEADS = "leads created - aug 1 -6.xlsx"
A_CALLS = "Created June, July, Aug - Called Aug 1 - 6.xlsx"
A_DB    = "Created June, July, Aug - Demo Booked Aug 1 - 6.xlsx"
A_DC    = "Created June, July, Aug - Demo Conducted Aug 1 - 6.xlsx"
A_SM    = "Original Sales - Created Jun, Jul, Aug - Sale Aug.xlsx"

print("=" * 84); print("MERGING THE AUGUST TOP-UP"); print("=" * 84)

# ---------------------------------------------------------------- leads
o = pd.read_excel(os.path.join(BASE, F_LEADS))
n = pd.read_excel(os.path.join(AUG,  A_LEADS))
n = n.reindex(columns=o.columns)                      # identical schema; keep base column order
m = pd.concat([o, n], ignore_index=True)
m["_c"] = dt(m["Created On"])
m = m.sort_values("_c").drop_duplicates("Prospect ID", keep="first").drop(columns="_c")
print(f"leads          base {len(o):>7,} + aug {len(n):>6,} -> {len(m):>7,}  "
      f"(added {len(m)-len(o):,}, overlap {len(o)+len(n)-len(m):,})")
print(f"               created up to {dt(m['Created On']).max()}")
m.to_excel(os.path.join(OUT, F_LEADS), index=False)

# ---------------------------------------------------------------- activity, de-duped on Activity Id
def merge_act(basefile, augfile, datecol, label, idfix=None):
    o = pd.read_excel(os.path.join(BASE, basefile))
    n = pd.read_excel(os.path.join(AUG,  augfile))
    if idfix and idfix in n.columns:                   # the Aug calls export renamed the ID column
        n = n.rename(columns={idfix: "Prospect Id"})
        print(f"               renamed '{idfix}' -> 'Prospect Id'")
    n = n.reindex(columns=o.columns)
    before = len(o)
    m = pd.concat([o, n], ignore_index=True)
    m = m.drop_duplicates("Activity Id", keep="first")
    print(f"{label:<15}base {before:>7,} + aug {len(n):>6,} -> {len(m):>7,}  "
          f"(added {len(m)-before:,}, duplicate Activity Ids removed {before+len(n)-len(m):,})")
    print(f"               {datecol} up to {dt(m[datecol]).max()}")
    m.to_excel(os.path.join(OUT, basefile), index=False)

merge_act(F_CALLS, A_CALLS, "Start Time",    "calls", idfix="INTLGENAI26")
merge_act(F_DB,    A_DB,    "Activity Date", "demo booked")
merge_act(F_DC,    A_DC,    "Activity Date", "demo conducted")

# ---------------------------------------------------------------- sales master
o = pd.read_excel(os.path.join(BASE, F_SM))
n = pd.read_excel(os.path.join(AUG,  A_SM))
n = n.reindex(columns=o.columns)

# Add August sales (organic sources only)
f_aug_ids = os.path.join(AUG, "Original Sales - Created Jun, Jul, Aug - Sale Aug.xlsx")
if os.path.exists(f_aug_ids):
    aug_sales_all = pd.read_excel(f_aug_ids, sheet_name=0)
    # Filter for organic sources only
    organic_sources = ['IL Website', 'Learn App', 'Learn (AN)', 'Learn AN', 'IL Surge', 'External Link']
    aug_sales = aug_sales_all[aug_sales_all['Lead Source'].isin(organic_sources)].copy()

    if len(aug_sales) > 0:
        # Ensure all columns match
        aug_sales_cols = aug_sales[o.columns]
        n = pd.concat([n, aug_sales_cols], ignore_index=True)
        print(f"  added {len(aug_sales)} organic Aug sales from {os.path.basename(f_aug_ids)}")

m = pd.concat([o, n], ignore_index=True)
key = m["Lead Link"].astype(str).str.extract(r"LeadID=([0-9a-fA-F-]+)")[0].str.lower()
m = m.loc[~key.duplicated(keep="first")]
sd = pd.to_datetime(m["Sale Date"], format="%d-%b-%y", errors="coerce").fillna(dt(m["Sale Date"]))
print(f"sales master   base {len(o):>7,} + aug {len(n):>6,} -> {len(m):>7,}  "
      f"(added {len(m)-len(o):,})")
print(f"               sale dates {sd.min():%d %b} .. {sd.max():%d %b}")
m.to_excel(os.path.join(OUT, F_SM), index=False)

print("=" * 84)
print("merged input set written to:", OUT)
