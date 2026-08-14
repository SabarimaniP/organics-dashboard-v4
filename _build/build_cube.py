# Organics Dashboard v4 — cube builder            built 2026-08-01
# Source: E:\Organics Numbers Update\Orignal updated data   (5 exports, organic sources only)
#
# LOCKED LOGIC (all confirmed by the user)
#   TIME     W1 = Monday 4 May 2026, Mon-Sun weeks, W1..W13 (W13 = 27 Jul - 2 Aug).
#            A MONTH IS A GROUP OF WEEKS, not calendar dates: a week belongs to the month holding
#            most of its days (its Thursday). May = W1-W4, June = W5-W8, July = W9-W13 (29 Jun-2 Aug).
#            Because months are week groups, week bitmasks answer every question - no month layer.
#   SETS     Cohort  = leads whose CREATION WEEK is in the period.
#            Rolling = leads created in the two full CALENDAR months before the period's month.
#            Outside = worked in the period but created earlier than that.
#   ASSIGNED owner not in {Leads Manager, LSQ Admin, Lead Allocation}  OR  has activity.
#            Every rate divides by this.
#   COUNTING Timing views  - each lead ONCE, at its first occurrence (first call / 2nd call /
#                            first answered / first demo / first conducted).
#            Activity views- distinct leads inside the period (week bits OR-ed over the period).
#   AGEING   Weekly View buckets = calendar days from the COHORT WEEK'S MONDAY:
#            D0-D3 / D4-D7 / D8-D14 / D15-D30 / D30-D60 / D60+.   Cohort only - a March-created
#            lead cannot have a measurable D0-D3 because call data starts 4 May.
#   SPEED    View 5 buckets = days from the lead's FIRST ANSWERED CALL to its FIRST demo:
#            D0-D3 / D4-D7 / D8+ , plus 4 = never answered.
#   SALES    The master sheet is truth, but only sales whose lead is in the ORGANIC leads file
#            count - the master also holds Inbound Project / WhatsApp / Referral etc., which are
#            out of scope for an Organics dashboard. Sale week always from the master's Sale Date.

import pandas as pd, json, re, os, collections, sys

DATA = os.environ.get("FUNNEL_DATA_DIR") or r"E:\Organics Numbers Update\Orignal updated data"
HERE = os.path.dirname(os.path.abspath(__file__))
F_LEADS = "Created in Mar to Aug.xlsx"
F_CALLS = "Outbound phone call mar 4 to 1 aug 8pm.xlsx"
F_DB    = "demo booking 4 mar to 1 aug 8pm.xlsx"
F_DC    = "demo conducted 4 mar to 1 aug 8 pm.xlsx"
F_SM    = "Original Sales May, June, July.xlsx"
P = lambda f: os.path.join(DATA, f)
dt  = lambda s: pd.to_datetime(s, errors="coerce", dayfirst=True)
pid = lambda s: s.astype(str).str.strip().str.lower()

# ---------------------------------------------------------------- 1. time
W1, NW = pd.Timestamp("2026-05-04"), 15   # Aug 1-12 top-up: activity to 11 Aug, so W15 (10-16 Aug) opens
# Everything is capped at the end of the last complete day of data. Leads created after the cap have
# had no chance to be called, and counting them would understate the newest week's rates.
CAP = pd.Timestamp("2026-08-13 23:59:59")   # Aug 1-14 top-up: activity reaches 14 Aug but only 12 calls by ~11am,
                                            # so the last COMPLETE day is the 13th. W15 partial (10-13 of 10-16).
WEND = W1 + pd.Timedelta(days=7 * NW - 1)
WEEKS = []
for i in range(NW):
    a = W1 + pd.Timedelta(days=7 * i); b = a + pd.Timedelta(days=6)
    WEEKS.append({"id": i + 1, "start": a.strftime("%Y-%m-%d"), "end": b.strftime("%Y-%m-%d"),
                  "label": f"W{i+1}", "range": f"{a:%d %b}\u2013{b:%d %b}",
                  "month": int((a + pd.Timedelta(days=3)).month)})
def wk(ts):
    if pd.isna(ts): return 0
    d = pd.Timestamp(ts).normalize()
    return 0 if (d < W1 or d > WEND) else int((d - W1).days // 7) + 1
MONTHS = []
for m, nm in [(5, "May"), (6, "June"), (7, "July"), (8, "August")]:
    ws = [w for w in WEEKS if w["month"] == m]
    if not ws: continue
    r1 = pd.Timestamp(2026, m - 2, 1); r2 = pd.Timestamp(2026, m, 1) - pd.Timedelta(days=1)
    MONTHS.append({"id": m, "name": nm, "weeks": [w["id"] for w in ws],
                   "range": ws[0]["range"].split("\u2013")[0] + " \u2013 " + ws[-1]["range"].split("\u2013")[1],
                   "roll": f"{r1.day} {r1:%b} \u2013 {r2.day} {r2:%b}", "rollMonths": [m - 2, m - 1]})
print("weeks:", ", ".join(f"{w['label']} {w['range']}({w['month']})" for w in WEEKS))
for m in MONTHS: print(f"  {m['name']:5s} = W{m['weeks']}  {m['range']}   rolling = {m['roll']}")

AGE_EDGES = [(0, 3), (4, 7), (8, 14), (15, 30), (31, 60), (61, 10 ** 6)]
def age_bucket(days):
    d = max(0, days)
    for i, (lo, hi) in enumerate(AGE_EDGES):
        if lo <= d <= hi: return i + 1
    return 6
def speed_bucket(days):
    d = days
    if d <= 3: return 1          # D0-D3 (a demo before first contact clamps here)
    if d <= 7: return 2          # D4-D7
    return 3                     # D8+

# ---------------------------------------------------------------- 2. normalisers
SYS = {"leads manager", "lsq admin", "lead allocation"}
def norm_src(v):
    s = str(v or "").lower()
    if "learn" in s: return "Learn App"
    if "surge" in s: return "IL Surge"
    if "website" in s: return "IL Website"
    return "Other"
def norm_grade(v):
    m = re.search(r"\d+", str(v or ""))
    if not m: return "Blank/Unknown"
    g = int(m.group())
    if 1 <= g <= 5: return "1-5"
    if 6 <= g <= 10: return "6-10"
    if 11 <= g <= 12: return "11-12"
    if g == 13: return "13 (Dropper)"
    return "Blank/Unknown"
# ---- Indian states / UTs only.  Anything foreign drops the lead from the whole dashboard.
IND_STATES = {
 "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Goa","Gujarat","Haryana",
 "Himachal Pradesh","Jharkhand","Karnataka","Kerala","Madhya Pradesh","Maharashtra","Manipur",
 "Meghalaya","Mizoram","Nagaland","Odisha","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana",
 "Tripura","Uttar Pradesh","Uttarakhand","West Bengal",
 "Andaman And Nicobar Islands","Chandigarh","Dadra And Nagar Haveli And Daman And Diu","Delhi",
 "Jammu And Kashmir","Ladakh","Lakshadweep","Puducherry"}
ALIAS = {
 "National Capital Territory Of Delhi":"Delhi","New Delhi":"Delhi",
 "Chattisgarh":"Chhattisgarh","Orissa":"Odisha","Uttaranchal":"Uttarakhand",
 "Pondicherry":"Puducherry","Union Territory Of Puducherry":"Puducherry",
 "Telengana":"Telangana","Telanagana":"Telangana","Andhrapradesh":"Andhra Pradesh",
 "Andaman And Nicobar":"Andaman And Nicobar Islands","Jammu & Kashmir":"Jammu And Kashmir",
 "Andaman & Nicobar":"Andaman And Nicobar Islands","Srikakulam":"Andhra Pradesh",
 "Dadra And Nagar Haveli":"Dadra And Nagar Haveli And Daman And Diu",
 "Daman And Diu":"Dadra And Nagar Haveli And Daman And Diu",
 "The Dadra And Nagar Haveli And Daman And Diu":"Dadra And Nagar Haveli And Daman And Diu",
 "Dadra & Nagar Haveli And Daman & Diu":"Dadra And Nagar Haveli And Daman And Diu"}
STATE_DROPPED = collections.Counter()
def norm_state(v):
    """canonical Indian state, 'Blank/Unknown', or None when the lead is not in India"""
    s = str(v or "").strip().replace("_", " ")
    s = " ".join(s.split()).title()
    if s.lower() in ("", "nan", "none"): return "Blank/Unknown"
    if s in IND_STATES: return s
    if s in ALIAS: return ALIAS[s]
    # LSQ zone labels such as "Bihar & Jharkhand" -> take the leading state
    for sep in ("&", " And "):
        if sep in s:
            head = s.split(sep)[0].strip()
            if head in IND_STATES: return head
            if head in ALIAS: return ALIAS[head]
    STATE_DROPPED[s] += 1
    return None

# ---------------------------------------------------------------- 3. leads
lf = pd.read_excel(P(F_LEADS), usecols=["Prospect ID", "Created On", "Owner", "Lead Source",
                                        "Grade", "State", "Student Phone Number"])
lf["p"] = pid(lf["Prospect ID"]); lf["c"] = dt(lf["Created On"])
lf = lf.dropna(subset=["c"]).sort_values("c").drop_duplicates("p", keep="first")
_pre = len(lf); lf = lf[lf.c <= CAP].copy()
print(f"  capped at {CAP:%d %b %H:%M} - dropped {_pre - len(lf):,} leads created after the cap")
lf["cmonth"] = lf.c.dt.month
lf["cwk"] = lf.c.map(wk)
lf["owner_ok"] = ~lf["Owner"].astype(str).str.strip().str.lower().isin(SYS)
lf = lf.rename(columns={"Lead Source": "src_raw"})   # itertuples needs a valid identifier
lf["st"] = lf["State"].map(norm_state)
_before = len(lf)
lf = lf[lf.st.notna()].copy()                      # Indian states (and blanks) only
N_FOREIGN = _before - len(lf)
print(f"  dropped {N_FOREIGN:,} leads with a non-Indian state "
      f"({len(STATE_DROPPED)} distinct values, e.g. "
      f"{', '.join(k for k,_ in STATE_DROPPED.most_common(5))})")
print(f"\nleads {len(lf):,}   {lf.c.min():%d-%b} .. {lf.c.max():%d-%b}")
print("  by creation month:", lf.cmonth.value_counts().sort_index().to_dict())
pre = int(((lf.cmonth == 5) & (lf.cwk == 0)).sum())
print(f"  created 1-3 May (before W1, so never a cohort, but do count in rolling): {pre:,}")
LEADSET = set(lf.p)

# ---------------------------------------------------------------- 4. activity
def load(fn, col, extra=()):
    d = pd.read_excel(P(fn), usecols=["Prospect Id", col, *extra])
    d["p"] = pid(d["Prospect Id"]); d["t"] = dt(d[col]); d["wk"] = d["t"].map(wk)
    d["mo"] = d["t"].dt.month.fillna(0).astype(int)      # real calendar month, for the calendar layer
    return d[(d.wk > 0) & (d.t <= CAP) & d.p.isin(LEADSET)]
calls = load(F_CALLS, "Start Time", ("Status",))
calls["ans"] = calls["Status"].astype(str).str.strip().str.lower().eq("answered")
dbs = load(F_DB, "Activity Date")
dcs = load(F_DC, "Activity Date")
THROUGH = max(calls.t.max(), dbs.t.max(), dcs.t.max())
print(f"calls {len(calls):,} ({int(calls.ans.sum()):,} answered) | demo booked {len(dbs):,} | conducted {len(dcs):,}")
print(f"data through {THROUGH:%d-%b %H:%M}")

# ---------------------------------------------------------------- 5. sales
sm = pd.read_excel(P(F_SM))
sm["p"] = sm["Lead Link"].astype(str).str.extract(r"LeadID=([0-9a-fA-F-]+)")[0].str.lower()
sd = pd.to_datetime(sm["Sale Date"], format="%d-%b-%y", errors="coerce")
sd = sd.fillna(pd.to_datetime(sm["Sale Date"], format="%d-%b-%Y", errors="coerce")).fillna(dt(sm["Sale Date"]))
sm["sd"] = sd
if sm.sd.isna().any(): sys.exit(f"unparsable Sale Date: {sm.loc[sm.sd.isna(),'Sale Date'].head().tolist()}")
sm = sm.dropna(subset=["p"]).sort_values("sd").drop_duplicates("p", keep="first")
sm = sm[sm.sd <= CAP].copy()
sm["wk"] = sm.sd.map(wk)
# keep the Lead Link id as it was written, before the phone fallback below reassigns p
sm["p0"] = sm["p"]
# ---- phone fallback -------------------------------------------------------------------------
# The sales sheet's Lead Link sometimes points at a lead that is not in the leads export. Before
# giving up on that sale, try to find the lead by phone number instead.
# A blank cell anywhere in a phone column makes pandas read the whole column as float, so a number
# arrives as "7095571808.0". Stripping non-digits would give "70955718080" and the last-10 slice
# "0955718080" - a corrupted key. Drop a trailing ".0" first. No effect on int or text columns.
ph10 = lambda s: (s.astype(str).str.replace(r"\.0$", "", regex=True)
                   .str.replace(r"\D", "", regex=True).str[-10:])
_ph = lf.assign(k=ph10(lf["Student Phone Number"]))
_ph = _ph[_ph.k.str.len() == 10].drop_duplicates("k")
PHMAP = dict(zip(_ph.k, _ph.p))
_miss = ~sm.p.isin(LEADSET)
_rec = 0
for col in ["Enter Customer mobile number", "Customer Alternate mobile number"]:
    if col not in sm.columns: continue
    k = ph10(sm[col])
    hit = _miss & k.isin(PHMAP.keys())
    if hit.any():
        sm.loc[hit, "p"] = k[hit].map(PHMAP)
        _rec += int(hit.sum())
        _miss = ~sm.p.isin(LEADSET)
print(f"  sales rescued by phone match (Lead Link missing from the leads export): {_rec}")
organic = sm[sm.p.isin(LEADSET)]
SALE_WK = {r.p: int(r.wk) for r in organic.itertuples() if r.wk > 0}
SALE_MO = {r.p: int(r.sd.month) for r in organic.itertuples() if r.wk > 0}
# ---- sale classification (August logic) -----------------------------------------------------
# Every sale is classified from the PAIR (Original Source, Updated Lead Source):
#
#   Updated = Referral                               -> REFERRAL
#   Updated = WhatsApp Chat / Middle East + WhatsApp  -> REACTIVATION
#   Original organic AND Updated organic             -> M0   (the only class that splits
#                                                              cohort vs rolling)
#   anything else                                    -> OTHER
#
# Organic ORIGINAL sources are Website, Website Inbound, Surge and App - Website and Website
# Inbound are the same thing. The organic UPDATED sources are the same set under the names the
# sales sheet actually uses (IL Website, IL Surge, Learn App ...).
# Referral, Reactivation and Other all sit on the ROLLING side; only M0 can be cohort.
ORIG_ORGANIC = {"website", "website inbound", "surge", "app"}
UPD_REFERRAL = {"referral"}
UPD_REACT    = {"whatsapp chat", "middle east + whatsapp", "whatsapp middle east",
                "middle east + whatsapp chat", "whatsapp"}
UPD_M0       = {"website", "website inbound", "il website", "surge", "il surge", "search",
                "app", "learn app", "learn (an)", "learn an", "learnin", "learn"}
CLS_M0, CLS_REF, CLS_REACT, CLS_OTHER = 1, 2, 3, 4
CLS_NAME = {CLS_M0: "M0", CLS_REF: "Referral", CLS_REACT: "Reactivation", CLS_OTHER: "Other"}

def _norm_src(v):
    return " ".join(str(v or "").strip().lower().split())

def sale_class(orig, upd):
    """Organic ORIGIN gates all three named classes; everything else is Other."""
    o_, u_ = _norm_src(orig), _norm_src(upd)
    if o_ not in ORIG_ORGANIC:              return CLS_OTHER
    if u_ in UPD_REFERRAL:                  return CLS_REF
    if u_ in UPD_REACT:                     return CLS_REACT
    if u_ in UPD_M0:                        return CLS_M0
    return CLS_OTHER

_o = sm["Original Source"]     if "Original Source"     in sm else pd.Series("", index=sm.index)
_u = sm["Updated Lead Source"] if "Updated Lead Source" in sm else pd.Series("", index=sm.index)
sm["cls"] = [sale_class(a, b) for a, b in zip(_o, _u)]
organic = sm[sm.p.isin(LEADSET)]
SALE_CLS = {r.p: int(r.cls) for r in organic.itertuples() if r.wk > 0}
_cc = collections.Counter(SALE_CLS.values())
print("  sale classes inside the window: "
      + ", ".join(f"{CLS_NAME[k]}={_cc.get(k,0)}" for k in (CLS_M0, CLS_REF, CLS_REACT, CLS_OTHER)))
# ---- August buckets, matching the split the user signed off ----------------------------------
# Three peer buckets:  M0 | Rolling | Reactivation
#   Reactivation = organic origin + WhatsApp updated source
#   M0           = organic origin + organic updated source AND a fresh lead (see M0_FROM)
#   Rolling      = everything else, i.e. aged M0 + Referral + Other
# Referral stays visible as a subset of Rolling rather than a fourth bucket.
#
# Counted from the SALES SHEET, not from lead rows: 14 of the 45 August rows have no lead in any
# export (11 of them Reactivation), and row-based counting showed Reactivation as 10 instead of 19.
# A lead date is consulted only to decide whether an M0-source sale is fresh (M0) or aged (Rolling).
# This also retires the hand-added sales for August - each is already a row in the sheet.
#
# M0_FROM is the fresh-lead boundary. 27 Jul is the only value that reproduces the signed-off
# 4 / 22 / 19 split, and it is the first day of W13. CHANGE THIS ONE CONSTANT if the intended
# rule turns out to be different - nothing else needs touching.
M0_FROM = pd.Timestamp("2026-07-27")

_augmask = (sm.sd >= pd.Timestamp("2026-08-01")) & (sm.sd <= CAP)
_aug = sm.loc[_augmask]
# Scope August to the sales sheet. merge_aug12.py drops its LeadIDs here; the master also holds
# older August rows (Laxman, Degala Kruthika, Rayyan, Shifra Joe) that the sheet does not list, and
# counting them would overstate Rolling. Without the sidecar, fall back to every August row.
_keyfile = os.path.join(DATA, "_aug_sale_keys.json")
if os.path.exists(_keyfile):
    import json as _json
    _sheet_keys = set(_json.load(open(_keyfile)))
    _before = len(_aug)
    # match on p0 - the phone fallback may have remapped p away from the sheet's own Lead Link id
    _aug = _aug[_aug.p0.isin(_sheet_keys)]
    print(f"  August scoped to the sales sheet: {len(_aug)} of {_before} master August rows "
          f"({_before - len(_aug)} not listed in the sheet, excluded)")
# lead creation date from every source available, no state filter - the sheet's own rows matter
# here even when the lead is dropped from the funnel population
_created = dict(zip(lf.p, lf.c))
for _fn, _dc in ((F_CALLS, "Lead Created On"), (F_DB, "Lead Created On"), (F_DC, "Lead Created On")):
    try:
        _d = pd.read_excel(P(_fn), usecols=["Prospect Id", _dc])
    except ValueError:
        continue
    for _p, _c in zip(pid(_d["Prospect Id"]), dt(_d[_dc])):
        if _p not in _created and pd.notna(_c): _created[_p] = _c

# bucket code: 1 = M0, 2 = Rolling (not referral), 3 = Reactivation, 4 = Rolling referral
def _aug_bucket(cls_, p_):
    if cls_ == CLS_REACT: return 3
    if cls_ == CLS_M0 and pd.notna(_created.get(p_)) and _created[p_] >= M0_FROM: return 1
    return 4 if cls_ == CLS_REF else 2

# The August buckets must respond to the Source / Grade / State filters, so each sale needs a
# dimension. It cannot come from the lead: 19 of these rows have no lead record at all. It comes
# from the SHEET instead - Original Source is the organic channel and maps 1:1 onto the three
# dashboard sources, with Select Standard for grade and State for state. One rule for all rows,
# so a sale's dimension never depends on whether its lead happened to be exported.
ORIG_TO_SRC = {"website": "IL Website", "website inbound": "IL Website",
               "surge": "IL Surge", "app": "Learn App"}
_augd = _aug.copy()
_augd["_bk"] = [_aug_bucket(c, p) for c, p in zip(_augd["cls"], _augd["p"])]
_augd["_sd"] = [ORIG_TO_SRC.get(_norm_src(v), "Other") for v in _augd["Original Source"]]
_augd["_gd"] = [norm_grade(v) for v in _augd.get("Select Standard", pd.Series(index=_augd.index))]
_augd["_st"] = [norm_state(v) or "Blank/Unknown" for v in _augd["State"]]
_unmapped = int((_augd["_sd"] == "Other").sum())
if _unmapped:
    print(f"  !! {_unmapped} August sale(s) have an Original Source outside "
          f"{sorted(ORIG_TO_SRC)} and fall into source 'Other'")
AUG_DIMCOUNT = collections.Counter(zip(_augd["_sd"], _augd["_gd"], _augd["_st"], _augd["_bk"]))

AUG = collections.Counter()
for (_s, _g, _t, _b), _n in AUG_DIMCOUNT.items():
    if _b == 1:   AUG["m0"] += _n
    elif _b == 3: AUG["react"] += _n
    else:
        AUG["rolling"] += _n
        if _b == 4: AUG["referral"] += _n
AUG_TOTAL = AUG["m0"] + AUG["rolling"] + AUG["react"]
print(f"  August (calendar) from the sales sheet -> M0 {AUG['m0']} | Rolling {AUG['rolling']} "
      f"(incl. {AUG['referral']} referral) | Reactivation {AUG['react']} | TOTAL {AUG_TOTAL}"
      f"   [M0 fresh-lead boundary {M0_FROM:%d %b}]")
print(f"\nsales master {len(sm)} distinct leads | organic (in the leads file) {len(organic)} | "
      f"organic inside W1-W13 {len(SALE_WK)}")
print(f"  excluded as non-organic (Inbound Project / WhatsApp / Referral etc.): {len(sm)-len(organic)}")
off = organic["Type Of Sales"].astype(str).str.lower().eq("offline").sum() if "Type Of Sales" in organic else 0
print(f"  of the organic ones, Type Of Sales = Offline: {int(off)} (included; say the word to exclude)")

# ---------------------------------------------------------------- 6. per-lead facts
def bits(v):
    m = 0
    for x in set(v): m |= 1 << int(x)
    return m
first_call, second_call, cmask, amask, d0, first_ans = {}, {}, {}, {}, {}, {}
cmask_mo, amask_mo = {}, {}
for p, g in calls.sort_values("t").groupby("p", sort=False):
    w = list(g.wk); first_call[p] = w[0]
    if len(w) > 1: second_call[p] = w[1]
    cmask[p] = bits(w);          cmask_mo[p] = bits(g.mo)
    ag = g[g.ans]
    amask[p] = bits(ag.wk);      amask_mo[p] = bits(ag.mo)
    if len(ag):
        first_ans[p] = int(ag.wk.iloc[0]); d0[p] = ag["t"].iloc[0].normalize()
first_call_d = calls.sort_values("t").groupby("p")["t"].first().dt.normalize().to_dict()
second_call_d = calls.sort_values("t").groupby("p")["t"].apply(
    lambda s: s.iloc[1].normalize() if len(s) > 1 else pd.NaT).to_dict()
d0_d = d0
def ev(df):
    m, mm, fw, fd = {}, {}, {}, {}
    for p, g in df.groupby("p", sort=False):
        m[p] = bits(g.wk); mm[p] = bits(g.mo)
        t0 = g["t"].min(); fw[p] = int(wk(t0)); fd[p] = t0.normalize()
    return m, mm, fw, fd
dbm, dbm_mo, db_w, db_d = ev(dbs)
dcm, dcm_mo, dc_w, dc_d = ev(dcs)

# ---------------------------------------------------------------- 7. rows
DIMS, DIDX = [], {}
def dim_id(t):
    if t not in DIDX: DIDX[t] = len(DIMS); DIMS.append(list(t))
    return DIDX[t]
touched = set(cmask) | set(dbm) | set(dcm) | set(SALE_WK)
rows, den = [], collections.Counter()
MON_OF = {w["id"]: pd.Timestamp(w["start"]) for w in WEEKS}
for r in lf.itertuples():
    p = r.p
    d = dim_id((norm_src(r.src_raw), norm_grade(r.Grade), r.st))   # r.st already canonical
    assigned = bool(r.owner_ok) or (p in touched)
    den[(int(r.cmonth), int(r.cwk), d, 1 if assigned else 0)] += 1
    fc = first_call.get(p, 0)
    if not (fc or dbm.get(p) or dcm.get(p) or SALE_WK.get(p)):
        continue
    # ageing buckets, measured from this lead's own cohort-week Monday (cohort rows only)
    ab = [0, 0, 0, 0]
    if r.cwk:
        M = MON_OF[r.cwk]
        if p in first_call_d:  ab[0] = age_bucket((first_call_d[p] - M).days)
        sc = second_call_d.get(p)
        if sc is not None and pd.notna(sc): ab[1] = age_bucket((sc - M).days)
        if p in d0_d:          ab[2] = age_bucket((d0_d[p] - M).days)
        if p in db_d:          ab[3] = age_bucket((db_d[p] - M).days)
    sb = 0
    if p in db_d:
        sb = speed_bucket((db_d[p] - d0_d[p]).days) if p in d0_d else 4      # 4 = never answered
    rows.append([d, int(r.cmonth), int(r.cwk), 1 if assigned else 0,
                 fc, second_call.get(p, 0), first_ans.get(p, 0), db_w.get(p, 0), dc_w.get(p, 0),
                 SALE_WK.get(p, 0),
                 cmask.get(p, 0), amask.get(p, 0), dbm.get(p, 0), dcm.get(p, 0),
                 ab[0], ab[1], ab[2], ab[3], sb,
                 # calendar layer: 19 callMo 20 ansMo 21 dbMo 22 dcMo 23 saleMo
                 cmask_mo.get(p, 0), amask_mo.get(p, 0), dbm_mo.get(p, 0), dcm_mo.get(p, 0),
                 SALE_MO.get(p, 0),
                 # 24 saleClass: 0 none, 1 M0, 2 Referral, 3 Reactivation, 4 Other.
                 # A label on the sale already counted at 9/23 - never an extra sale.
                 SALE_CLS.get(p, 0)])
# Resolve the August sale dimensions now that DIMS exists. dim_id() will mint a combo that the
# leads data never produced, which is fine and necessary: a sale whose lead was never exported
# still has a real source/grade/state from the sheet, and the funnel must be able to filter on it.
AUG_SALE_DIM = collections.Counter()
_newdims = 0
for (_s, _g, _t, _b), _n in AUG_DIMCOUNT.items():
    _before = len(DIMS)
    AUG_SALE_DIM[(dim_id((_s, _g, _t)), _b)] += _n
    if len(DIMS) > _before: _newdims += 1
AUG_SALE_DIM = [[d, b, n] for (d, b), n in sorted(AUG_SALE_DIM.items())]
print(f"  August sales carry {len(AUG_SALE_DIM)} dim/bucket cells"
      + (f" ({_newdims} new dim combo(s) minted from the sheet)" if _newdims else ""))

CALM = []
for _m in range(5, 9):
    _a = pd.Timestamp(2026, _m, 1)
    if _a > CAP: continue
    _end = _a + pd.offsets.MonthEnd(0)
    _b = min(CAP.normalize(), _end)
    CALM.append({"id": _m, "name": _a.strftime("%B"),
                 "from": f"{_a.day} {_a:%b}", "to": f"{_b.day} {_b:%b}",
                 "complete": bool(_b >= _end), "rollMonths": [_m - 2, _m - 1]})
print("\ncalendar timeline:", ", ".join(
    f"{c['name']} {c['from']}-{c['to']}{'' if c['complete'] else ' (to date)'}" for c in CALM))
print(f"\nrows {len(rows):,} leads with activity of {len(lf):,} total")

# Hardcoded sales: the sale is real but its lead is absent from every export, so nothing links it to
# a lead row and the normal path cannot see it. Each is added back by hand.
#   HAri     Aug 1  W13   Learn (AN)     Tazmeen  Aug 4  W14   Learn (AN)
#   Laxman   Aug 4  W14   WhatsApp Chat  Rayyan   Aug 6  W14   IL Website
# Re-check on every rebuild: if any of these leads later appears in the leads export (and survives the
# state filter), the normal path will count it and the hand-added figure below becomes a double count.
HARDCODED_IDS = {"3223045e-7ecd-4114-ae34-19f69221e466": ("HAri", 13),
                 "e9d507c8-1948-11f1-8166-02b754a99095": ("Laxman Khatwani", 14),
                 "5fd0a6ed-6252-4177-909d-f3a38e834e4e": ("Tazmeen mehwish", 14),
                 "04ffa05b-81eb-11f1-bff5-0a572a71c62d": ("Rayyan", 14)}
# Their class is read from the same source pair as every other sale, so it self-corrects if the
# sheet ever reclassifies them. All four sit on the ROLLING side: under the August rule only an
# M0 sale with a lead created in the period can be cohort, and these have no usable lead row.
hardcoded_sales = collections.Counter()          # week -> count, for the week-group view
hardcoded_cls   = collections.Counter()          # class -> count, rolling side of Aug calendar
_smk = sm.set_index("p") if sm.index.name != "p" else sm
for _pid, (_nm, _wk) in HARDCODED_IDS.items():
    _row = sm[sm.p == _pid]
    if _pid in LEADSET:
        print(f"  hardcoded {_nm}: lead now present in the leads export -> counted normally, NOT hand-added")
        continue
    _c = int(_row["cls"].iloc[0]) if len(_row) else CLS_OTHER
    hardcoded_sales[_wk] += 1
    hardcoded_cls[_c] += 1
    print(f"  hand-added {_nm:<18} W{_wk}  class {CLS_NAME[_c]}  (lead in no export)")
hardcoded_sales = dict(hardcoded_sales)
hardcoded_sales_aug = sum(hardcoded_cls.values())   # all on the rolling side
hardcoded_sales_aug_cohort = 0

sales_by_week = {str(w): sum(1 for x in SALE_WK.values() if x == w) for w in range(1, NW + 1)}
for w, count in hardcoded_sales.items():
    sales_by_week[str(w)] = sales_by_week.get(str(w), 0) + count
hardcoded_total = sum(hardcoded_sales.values())

CUBE = {"weeks": WEEKS, "months": MONTHS, "dims": DIMS,
        "den": [[k[0], k[1], k[2], k[3], v] for k, v in den.items()], "rows": rows,
        "buckets": ["D0\u2013D3", "D4\u2013D7", "D8\u2013D14", "D15\u2013D30", "D30\u2013D60", "D60+"],
        "speed": ["D0\u2013D3", "D4\u2013D7", "D8+", "No answer"],
        "sales": {"organicInWindow": len(SALE_WK) + hardcoded_total, "masterDistinct": int(len(sm)),
                  "nonOrganic": int(len(sm) - len(organic)),
                  "byWeek": sales_by_week},
        "calMonths": CALM,
        "hardcodedAugSales": hardcoded_sales_aug,
        "hardcodedAugSalesCohort": hardcoded_sales_aug_cohort,
        # hand-added sales split by class (week-group views only - the August calendar month is
        # counted straight from the sales sheet below, where these already appear as rows)
        "hardcodedAugByClass": {str(k): v for k, v in hardcoded_cls.items()},
        "saleClasses": {str(k): v for k, v in CLS_NAME.items()},
        # August calendar month, counted from the sales sheet: M0 | Rolling | Reactivation
        "augSale": {"m0": AUG["m0"], "rolling": AUG["rolling"], "react": AUG["react"],
                    "referral": AUG["referral"], "total": AUG_TOTAL},
        # [dimIdx, bucket, count]  bucket: 1 M0 · 2 Rolling · 3 Reactivation · 4 Rolling-referral
        "augSaleDim": AUG_SALE_DIM,
        "augM0From": M0_FROM.strftime("%Y-%m-%d"),
        "systemOwners": ["Leads Manager", "LSQ Admin", "Lead Allocation"],
        "through": THROUGH.strftime("%Y-%m-%d"), "throughLabel": THROUGH.strftime("%d %b %Y"),
        "elapsed": {str(w["id"]): int((THROUGH.normalize() - pd.Timestamp(w["start"])).days) for w in WEEKS},
        "preW1May": pre, "foreignDropped": int(N_FOREIGN),
        "foreignExamples": [k for k, _ in STATE_DROPPED.most_common(8)]}
json.dump(CUBE, open(os.path.join(HERE, "_cube.json"), "w"))
print(f"cube written · {len(DIMS)} dim combos · {len(CUBE['den'])} denominator cells")
