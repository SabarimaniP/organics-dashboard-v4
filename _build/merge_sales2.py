# -*- coding: utf-8 -*-
# Fold "Original Sales 2 Aug 1 - 10.xlsx" into the sales master.
#
# This export is a different shape from the usual one: it is a LeadSquared "Sales Punch In" ACTIVITY
# export (29 columns, Activity Event 275) rather than the 41-column sales form. Two consequences:
#
#   1. It carries Prospect Id directly, so there is no Lead Link to parse and the phone fallback is
#      not needed. build_cube.py keys sales off the LeadID inside Lead Link, so a synthetic link
#      (...LeadDetails?LeadID=<Prospect Id>) is written to keep the master schema unchanged.
#   2. It has no Type Of Sales column. Left blank, which build_cube treats as not-Offline, i.e.
#      included - the same default the existing rows get.
#
# De-duplicated against the master on that same LeadID, master wins on collision.
import pandas as pd, os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
MERGED = os.path.join(HERE, "_merged")
TOPUP = r"E:\Organics Numbers Update\August Data for Dashboard Update"
F_SM = "Original Sales May, June, July.xlsx"
T_SM2 = "Original Sales 2 Aug 1 - 10.xlsx"
BACKUP = os.path.join(HERE, "_merged_pre_sales2")
dt = lambda s: pd.to_datetime(s, errors="coerce", dayfirst=True)
LINK = "https://in21.leadsquared.com/LeadManagement/LeadDetails?LeadID="

print("=" * 92); print("FOLDING IN 'Original Sales 2 Aug 1 - 10.xlsx'"); print("=" * 92)
os.makedirs(BACKUP, exist_ok=True)
if not os.path.exists(os.path.join(BACKUP, F_SM)):
    shutil.copy2(os.path.join(MERGED, F_SM), os.path.join(BACKUP, F_SM))
    print(f"backup -> {BACKUP}\n")

o = pd.read_excel(os.path.join(MERGED, F_SM))
n = pd.read_excel(os.path.join(TOPUP, T_SM2), sheet_name=0)
print(f"master rows {len(o)}   new-export rows {len(n)}")

# map the activity export onto the master's column names
m = pd.DataFrame(index=n.index, columns=o.columns)
m["Lead Link"]                            = LINK + n["Prospect Id"].astype(str).str.strip()
m["Sale Date"]                            = dt(n["Sale Date"])
m["Lead Source"]                          = n["Lead Source"]
m["Enter Customer Name"]                  = n["Lead Name"]
m["Enter Customer mobile number"]         = n["Phone Number"]
m["Email"]                                = n["Email Address"]
m["State"]                                = n["State"]
m["Select Standard"]                      = n["Grade"]
m["Enter Sale value (Collected Revenue)"] = n["Enter Sale value Collected Rev"]
m["Enter Sale value (Booking Revenue)"]   = n["Enter Sale value (Booking Rev)"]
m["Enter Down Payment Collected"]         = n["Enter Down Payment Collected"]
m["Prediction Category with sales"]       = n["Prediction Category with sales"]
m["Lead Owner Email"]                     = n["Lead Owner Email"]
m["Lead Owner Name"]                      = n["Lead Owner Name"]
m["Lead Number"]                          = n["Lead Number"]
m["Activity Added By"]                    = n["Activity Added By"]
m["Associate Employee"]                   = n["Owner (User Name)"]
m["EMP MAIL ID"]                          = n["Owner (User Email)"]
m["Notes"]                                = n["Notes"]
m["Start time"] = m["Completion time"]    = dt(n["Activity Date"])
m["Updated Lead Source"]                  = n["Lead Source"]

# NOTE on phone columns: adding rows with blank alternate numbers turns that column from int64 to
# float64, so a cell reads back as 7095571808.0. build_cube's phone fallback strips non-digits and
# takes the last 10 characters, which on "70955718080" yields "0955718080" - a corrupted key that
# matches no lead. Rather than fight Excel dtypes here, ph10() in build_cube.py drops a trailing
# ".0" before stripping. Leaving the columns untouched keeps this merge lossless.
before = len(o)
allrows = pd.concat([o, m], ignore_index=True)
k = allrows["Lead Link"].astype(str).str.extract(r"LeadID=([0-9a-fA-F-]+)")[0].str.lower()
allrows = allrows.loc[~k.duplicated(keep="first")]        # master first, so master wins
added = len(allrows) - before
sd = pd.to_datetime(allrows["Sale Date"], format="%d-%b-%y", errors="coerce").fillna(dt(allrows["Sale Date"]))
print(f"sales master   {before} -> {len(allrows)}   added {added}   (dropped {len(n)-added} already present)")
print(f"               sale dates {sd.min():%d %b} .. {sd.max():%d %b}")
print(f"               by month: {dict(sd.dt.to_period('M').value_counts().sort_index())}")
print(f"               new rows by source: {dict(m['Lead Source'].value_counts())}")
allrows.to_excel(os.path.join(MERGED, F_SM), index=False)
print("=" * 92)
print("sales master updated in:", MERGED)
