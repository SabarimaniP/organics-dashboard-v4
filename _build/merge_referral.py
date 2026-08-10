# -*- coding: utf-8 -*-
# Fold "Organic Refferal Sales.xlsx" into the sales master and tag the rows as referrals.
#
# Referral sales come from asking a student during the demo/counselling call whether a friend would
# like to join. If that referral converts, it is a Referral Sale.
#
# TWO TRAPS IN THIS FILE
#   1. It has NO HEADER ROW. Read with header=None and apply the master's column names, or pandas
#      consumes the first sale as the header and you silently lose a row.
#   2. One of the three referrals (Ahil) is ALREADY in the master as a normal sale
#      ("Mohammed Abdul Ahil", 8 Aug). It must not be appended again - its existing row is
#      re-tagged in place, so it moves from Sale into Referral rather than being counted twice.
#
# ADARSH BAROI is excluded per the user: source "InMobious Leads" is not organic.
#
# The tag is written to `Updated Lead Source` = "Referral", which no other master row uses.
# build_cube.py reads that to build the referral layer.
import pandas as pd, os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
MERGED = os.path.join(HERE, "_merged")
TOPUP = r"E:\Organics Numbers Update\August Data for Dashboard Update"
F_SM = "Original Sales May, June, July.xlsx"
T_REF = "Organic Refferal Sales.xlsx"
BACKUP = os.path.join(HERE, "_merged_pre_referral")
EXCLUDE_NAMES = {"adarsh baroi"}          # not organic - user's call
dt = lambda s: pd.to_datetime(s, errors="coerce", dayfirst=True)
key = lambda s: s.astype(str).str.extract(r"LeadID=([0-9a-fA-F-]+)")[0].str.lower()

print("=" * 92); print("FOLDING IN 'Organic Refferal Sales.xlsx'"); print("=" * 92)
os.makedirs(BACKUP, exist_ok=True)
if not os.path.exists(os.path.join(BACKUP, F_SM)):
    shutil.copy2(os.path.join(MERGED, F_SM), os.path.join(BACKUP, F_SM))
    print(f"backup -> {BACKUP}\n")

o = pd.read_excel(os.path.join(MERGED, F_SM))
r = pd.read_excel(os.path.join(TOPUP, T_REF), header=None)     # <-- no header row in this export
if len(r.columns) > len(o.columns):
    raise SystemExit(f"referral export has {len(r.columns)} columns, master has {len(o.columns)}")
r.columns = list(o.columns)[:len(r.columns)]
r = r.reindex(columns=o.columns)
print(f"master rows {len(o)}   referral rows {len(r)} (header-less, so every row is data)")

r["_k"] = key(r["Lead Link"])
drop = r["Enter Customer Name"].astype(str).str.strip().str.lower().isin(EXCLUDE_NAMES)
for nm in r.loc[drop, "Enter Customer Name"]:
    print(f"               excluded (not organic): {nm}")
r = r[~drop].copy()
r["Updated Lead Source"] = "Referral"

o["_k"] = key(o["Lead Link"])
already = r["_k"].isin(set(o["_k"].dropna()))

# already in the master -> re-tag in place, do NOT append
retag = set(r.loc[already, "_k"])
for k in retag:
    nm = o.loc[o["_k"] == k, "Enter Customer Name"].iloc[0]
    print(f"               re-tagged existing sale as Referral (not appended): {nm}")
o.loc[o["_k"].isin(retag), "Updated Lead Source"] = "Referral"

# genuinely new -> append
fresh = r[~already].drop(columns="_k")
for nm in fresh["Enter Customer Name"]:
    print(f"               appended as a new referral sale: {nm}")
out = pd.concat([o.drop(columns="_k"), fresh], ignore_index=True)
k = key(out["Lead Link"])
out = out.loc[~k.duplicated(keep="first")]

flag = out["Updated Lead Source"].astype(str).str.strip().str.lower().eq("referral")
sd = pd.to_datetime(out["Sale Date"], format="%d-%b-%y", errors="coerce").fillna(dt(out["Sale Date"]))
print()
print(f"sales master   {len(o)} -> {len(out)}   appended {len(fresh)}   re-tagged {len(retag)}")
print(f"               rows tagged Referral: {int(flag.sum())}")
print(f"               columns {len(out.columns)} (master schema unchanged)")
for _, x in out[flag].iterrows():
    print(f"                 {str(x['Enter Customer Name'])[:26]:<28} {str(x['Lead Source']):<14} sale {str(x['Sale Date'])[:10]}")
print(f"               sale dates {sd.min():%d %b} .. {sd.max():%d %b}")
out.to_excel(os.path.join(MERGED, F_SM), index=False)
print("=" * 92)
print("sales master updated in:", MERGED)
