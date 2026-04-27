#!/usr/bin/env python3
"""Generate South India evaluation datasets for distribution churn scenarios."""

from __future__ import annotations

import csv
import math
import random
import shutil
from datetime import date, datetime, timedelta
from pathlib import Path

SEED = 20260427
random.seed(SEED)
ROOT = Path(__file__).resolve().parent

START_DATE = date(2024, 4, 1)
END_DATE = date(2026, 3, 31)
MONTHS = []
cur = date(2024, 4, 1)
while cur <= END_DATE:
    MONTHS.append(cur)
    if cur.month == 12:
        cur = date(cur.year + 1, 1, 1)
    else:
        cur = date(cur.year, cur.month + 1, 1)

STATE_GEO = {
    "Tamil Nadu": {
        "abbr": "TN",
        "cities": ["Chennai", "Coimbatore", "Madurai", "Trichy", "Salem", "Erode", "Vellore", "Tirunelveli", "Hosur", "Cuddalore", "Kanchipuram", "Thanjavur"],
        "districts": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Erode", "Vellore", "Tirunelveli", "Krishnagiri", "Cuddalore", "Kanchipuram", "Thanjavur"],
        "prefix": "33",
    },
    "Karnataka": {
        "abbr": "KA",
        "cities": ["Bengaluru", "Mysuru", "Mangaluru", "Hubballi", "Belagavi", "Davanagere", "Shivamogga", "Tumakuru", "Ballari", "Udupi", "Kalaburagi", "Raichur"],
        "districts": ["Bengaluru Urban", "Mysuru", "Dakshina Kannada", "Dharwad", "Belagavi", "Davanagere", "Shivamogga", "Tumakuru", "Ballari", "Udupi", "Kalaburagi", "Raichur"],
        "prefix": "29",
    },
    "Telangana": {
        "abbr": "TS",
        "cities": ["Hyderabad", "Warangal", "Karimnagar", "Nizamabad", "Khammam", "Mahbubnagar", "Nalgonda", "Siddipet", "Adilabad", "Suryapet"],
        "districts": ["Hyderabad", "Warangal", "Karimnagar", "Nizamabad", "Khammam", "Mahbubnagar", "Nalgonda", "Siddipet", "Adilabad", "Suryapet"],
        "prefix": "36",
    },
    "Andhra Pradesh": {
        "abbr": "AP",
        "cities": ["Vijayawada", "Visakhapatnam", "Guntur", "Nellore", "Kurnool", "Tirupati", "Rajahmundry", "Kakinada", "Anantapur", "Kadapa", "Ongole"],
        "districts": ["Krishna", "Visakhapatnam", "Guntur", "Nellore", "Kurnool", "Tirupati", "East Godavari", "Kakinada", "Anantapur", "Kadapa", "Prakasam"],
        "prefix": "37",
    },
    "Kerala": {
        "abbr": "KL",
        "cities": ["Kochi", "Thiruvananthapuram", "Kozhikode", "Thrissur", "Kollam", "Kannur", "Palakkad", "Alappuzha", "Kottayam"],
        "districts": ["Ernakulam", "Thiruvananthapuram", "Kozhikode", "Thrissur", "Kollam", "Kannur", "Palakkad", "Alappuzha", "Kottayam"],
        "prefix": "32",
    },
    "Puducherry": {
        "abbr": "PY",
        "cities": ["Puducherry", "Karaikal"],
        "districts": ["Puducherry", "Karaikal"],
        "prefix": "34",
    },
}

STATE_WEIGHTS = [
    ("Tamil Nadu", 0.24),
    ("Karnataka", 0.24),
    ("Telangana", 0.18),
    ("Andhra Pradesh", 0.22),
    ("Kerala", 0.10),
    ("Puducherry", 0.02),
]

STATE_ALIASES = {
    "Tamil Nadu": ["Tamil Nadu", "TN", "TAMILNADU", "Tamilnadu"],
    "Karnataka": ["Karnataka", "KA", "KARNATAKA"],
    "Telangana": ["Telangana", "TS", "TELANGANA", "TG"],
    "Andhra Pradesh": ["Andhra Pradesh", "AP", "A.P.", "ANDHRA"],
    "Kerala": ["Kerala", "KL", "KERALA"],
    "Puducherry": ["Puducherry", "PY", "Pondicherry"],
}

PERSON_FIRST = ["Anand", "Arun", "Bala", "Chandra", "Deepak", "Ganesh", "Hari", "Irfan", "Jagan", "Karthik", "Lokesh", "Manoj", "Naveen", "Prakash", "Rafiq", "Sanjay", "Senthil", "Suresh", "Venkatesh", "Yusuf", "Lakshmi", "Meena", "Priya", "Revathi", "Sowmya", "Farida", "Geetha", "Kavya"]
PERSON_LAST = ["Rao", "Reddy", "Naidu", "Shetty", "Nair", "Pillai", "Gowda", "Iyer", "Kumar", "Khan", "Prasad", "Menon", "Acharya", "Patil", "Das", "Varma", "Babu", "Joseph"]
FIRM_PREFIX = ["Sri", "Shree", "New", "National", "Metro", "City", "Royal", "Star", "Lucky", "Modern", "Balaji", "Vijaya", "Kaveri", "Mahalakshmi", "Murugan", "Ganesh", "Prime", "United", "Sree"]
FIRM_CORE = ["Traders", "Agencies", "Enterprises", "Distributors", "Paints", "Hardware", "Tyres", "Fertilisers", "Agro", "Stores", "Mart", "Depot", "Corporation", "Sales", "Associates", "Chemicals", "Services"]
ROUTES = ["Metro", "Tier2", "Coastal", "Industrial", "Rural", "Highway", "Delta", "Construction", "Agri belt", "Hill route"]
SALES_REPS = [f"SR{str(i).zfill(3)}" for i in range(1, 151)]
SCHEMES = ["None", "Quarterly rebate", "Slab discount", "Focus SKU push", "Display support", "Credit note pending", "Dealer meet commitment", "Festival scheme", "Launch incentive"]
MESSY_NULLS = ["", "NA", "N/A", "-", "null"]

COLUMN_MEANINGS = {
    "customer_id": "customer key used in sales and support files",
    "legacy_code": "older ERP or distributor code",
    "customer_name": "synthetic customer name",
    "customer_name_at_invoice": "name captured at invoice time",
    "owner_name": "synthetic owner/contact name",
    "role": "network role",
    "channel": "trade or service channel",
    "parent_customer_id": "upstream dealer/distributor link",
    "state": "raw state value from export",
    "state_clean": "normalized state value",
    "district": "district",
    "city": "city or town",
    "pincode": "postal code",
    "route_type": "route or market type",
    "sales_rep_id": "field owner",
    "territory": "sales territory",
    "gstin": "GST identifier or placeholder",
    "mobile": "contact phone value",
    "onboarded_date": "customer onboarding date",
    "credit_limit": "approved credit limit",
    "payment_terms_days": "payment terms",
    "current_status": "current status from operating system",
    "status_profile_for_eval": "synthetic behavior driver, not a model label",
    "data_quality_note": "known issue in record",
    "sku_id": "product key",
    "legacy_sku_code": "older product code",
    "category": "product category",
    "sku_name": "product name",
    "sku_name_at_invoice": "product name captured at invoice time",
    "pack_size": "pack size bucket",
    "uom": "unit of measure",
    "mrp": "list price",
    "active_flag": "active product flag",
    "invoice_id": "transaction line key",
    "invoice_date": "transaction date",
    "posting_month": "month for aggregation",
    "quantity": "quantity sold or claimed",
    "gross_amount": "value before discount",
    "discount_amount": "discount value",
    "net_amount": "value after discount",
    "scheme_name": "scheme or incentive name",
    "order_source": "system or manual source",
    "payment_status": "payment status",
    "secondary_customer_id": "secondary linked customer or store",
    "free_text_note": "unstructured note",
    "as_of_date": "snapshot date",
    "outstanding_amount": "total outstanding",
    "not_due_amount": "not due amount",
    "days_1_30": "ageing bucket",
    "days_31_60": "ageing bucket",
    "days_61_90": "ageing bucket",
    "days_90_plus": "ageing bucket",
    "last_payment_date": "last payment date",
    "block_flag": "credit block indicator",
    "collector_note": "collection note",
    "activity_id": "field activity key",
    "activity_date": "field activity date",
    "activity_type": "activity type",
    "visit_outcome": "outcome recorded by field team",
    "next_action_date": "next follow-up date",
    "minutes_spent": "minutes captured by app",
    "lat_long_quality": "GPS quality flag",
    "claim_id": "claim or return key",
    "claim_date": "claim date",
    "claim_type": "claim type",
    "claim_amount": "requested amount",
    "approved_amount": "approved amount",
    "status": "workflow status",
    "reason_text": "claim reason text",
    "document_status": "document state",
    "watch_id": "watchlist key",
    "added_by": "source of watchlist entry",
    "added_date": "watchlist date",
    "watch_reason": "reason for watchlist entry",
    "last_known_action": "last action recorded",
    "manager_confidence": "manager confidence",
}


def choose_state(weights=None):
    pool = weights or STATE_WEIGHTS
    r = random.random()
    acc = 0.0
    for state, weight in pool:
        acc += weight
        if r <= acc:
            return state
    return pool[-1][0]


def geo_for_state(state):
    info = STATE_GEO[state]
    idx = random.randrange(len(info["cities"]))
    return {
        "state": state,
        "state_raw": random.choice(STATE_ALIASES[state]) if random.random() < 0.18 else state,
        "abbr": info["abbr"],
        "city": info["cities"][idx],
        "district": info["districts"][idx % len(info["districts"])],
        "pincode": f"{info['prefix']}{random.randint(1000, 9999)}",
    }


def date_string(d):
    style = random.random()
    if style < 0.78:
        return d.isoformat()
    if style < 0.88:
        return d.strftime("%d/%m/%Y")
    if style < 0.95:
        return d.strftime("%m/%d/%Y")
    return d.strftime("%d-%b-%y")


def random_date(start=START_DATE, end=END_DATE):
    return start + timedelta(days=random.randint(0, (end - start).days))


def maybe_blank(value, p=0.04):
    return random.choice(MESSY_NULLS) if random.random() < p else value


def phone():
    if random.random() < 0.05:
        return random.choice(["", "0", "9999999999", "NA"])
    return str(random.choice([6, 7, 8, 9])) + "".join(str(random.randint(0, 9)) for _ in range(9))


def gstin(state):
    if random.random() < 0.12:
        return random.choice(["", "Applied", "NA", "URD"])
    prefix = STATE_GEO[state]["prefix"]
    body = "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(10))
    return f"{prefix}{body}1Z{random.randint(1,9)}"


def owner_name():
    return f"{random.choice(PERSON_FIRST)} {random.choice(PERSON_LAST)}"


def firm_name(category=None):
    core = random.choice(FIRM_CORE)
    if category and random.random() < 0.35:
        core = category
    name = f"{random.choice(FIRM_PREFIX)} {random.choice(PERSON_FIRST)} {core}"
    roll = random.random()
    if roll < 0.07:
        name = name.upper()
    elif roll < 0.13:
        name = name.replace("Sri", "SRI").replace("Shree", "Shri")
    elif roll < 0.17:
        name = name + " " + random.choice(["Pvt", "Ltd", "& Co", "Main"])
    return name


def profile_factor(profile, month_index):
    if profile == "stable":
        return random.uniform(0.85, 1.18)
    if profile == "growing":
        return 0.65 + (month_index / max(1, len(MONTHS) - 1)) * random.uniform(0.7, 1.2)
    if profile == "declining":
        return max(0.12, 1.25 - (month_index / max(1, len(MONTHS) - 1)) * random.uniform(0.85, 1.25))
    if profile == "lost":
        cutoff = random.randint(11, 18)
        return random.uniform(0.75, 1.2) if month_index < cutoff else random.uniform(0.0, 0.08)
    if profile == "credit_watch":
        return random.uniform(0.75, 1.1) if month_index < 15 else random.uniform(0.22, 0.7)
    if profile == "seasonal":
        m = MONTHS[month_index].month
        return random.uniform(1.25, 1.85) if m in [6, 7, 8, 9, 10] else random.uniform(0.28, 0.8)
    if profile == "new":
        start = random.randint(8, 16)
        return random.uniform(0.0, 0.04) if month_index < start else random.uniform(0.5, 1.25)
    if profile == "erratic":
        return random.choice([random.uniform(0.05, 0.3), random.uniform(0.7, 1.6)])
    return 1.0


def weighted_profile():
    return random.choices(
        ["stable", "growing", "declining", "lost", "credit_watch", "seasonal", "new", "erratic"],
        weights=[35, 13, 16, 8, 9, 8, 5, 6],
        k=1,
    )[0]


def as_money(value):
    return f"{max(0, value):.2f}"


def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_csv_stream(path, fieldnames, row_iter):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in row_iter:
            writer.writerow(row)


def random_amount(base, profile, month_idx, volatility=0.35):
    f = profile_factor(profile, month_idx)
    seasonal = 1.0 + 0.15 * math.sin((month_idx + 2) / 12 * math.pi * 2)
    return base * f * seasonal * random.uniform(1 - volatility, 1 + volatility)


def make_customers(prefix, count, role, category, state_weights=None, parent_pool=None, channels=None):
    rows = []
    for i in range(1, count + 1):
        state = choose_state(state_weights)
        geo = geo_for_state(state)
        profile = weighted_profile()
        join = random_date(date(2017, 1, 1), date(2025, 12, 31))
        parent = random.choice(parent_pool)["customer_id"] if parent_pool and random.random() < 0.9 else ""
        credit_limit = random.choice([0, 50000, 75000, 100000, 150000, 250000, 400000, 750000, 1200000])
        if role in ["dealer", "distributor"]:
            credit_limit = random.choice([250000, 500000, 750000, 1200000, 2000000, 3500000, 5000000, 7500000])
        row = {
            "customer_id": f"{prefix}{i:06d}",
            "legacy_code": maybe_blank(f"{prefix.replace('_', '')[:3]}-{random.randint(10000,99999)}", 0.10),
            "customer_name": firm_name(category),
            "owner_name": owner_name(),
            "role": role,
            "channel": random.choice(channels or ["General trade", "Dealer", "Distributor", "Retail", "Project"]),
            "parent_customer_id": parent,
            "state": geo["state_raw"],
            "state_clean": state,
            "district": geo["district"],
            "city": geo["city"],
            "pincode": maybe_blank(geo["pincode"], 0.03),
            "route_type": random.choice(ROUTES),
            "sales_rep_id": random.choice(SALES_REPS),
            "territory": f"{geo['abbr']}-{random.choice(['North','South','Central','East','West'])}-{random.randint(1,9)}",
            "gstin": gstin(state),
            "mobile": phone(),
            "onboarded_date": date_string(join),
            "credit_limit": credit_limit,
            "payment_terms_days": random.choice([0, 7, 15, 21, 30, 45, 60]),
            "current_status": random.choices(["Active", "Watch", "Inactive", "Blocked", "New"], [68, 13, 8, 4, 7], k=1)[0],
            "status_profile_for_eval": profile,
            "data_quality_note": random.choice(["", "duplicate name in old ERP", "GST pending", "phone shared by two outlets", "territory changed FY25", "manual code from distributor sheet"]),
        }
        rows.append(row)
    return rows


def make_products(prefix, categories):
    rows = []
    idx = 1
    for cat, names in categories.items():
        for name in names:
            for pack in random.sample(["small", "medium", "large", "bulk"], k=random.randint(1, 3)):
                rows.append({
                    "sku_id": f"{prefix}{idx:04d}",
                    "legacy_sku_code": maybe_blank(f"{prefix}-{random.randint(1000,9999)}", 0.05),
                    "category": cat,
                    "sku_name": name,
                    "pack_size": pack,
                    "uom": random.choice(["EA", "KG", "LTR", "BOX", "BAG", "SET"]),
                    "mrp": as_money(random.uniform(80, 9000)),
                    "active_flag": random.choice(["Y", "Y", "Y", "N"]),
                })
                idx += 1
    return rows


def pick_month_index():
    return random.randrange(len(MONTHS))


def sales_rows(target_rows, customers, products, prefix, channel_label, value_scale, include_secondary=False):
    for i in range(1, target_rows + 1):
        customer = random.choice(customers)
        product = random.choice(products)
        mi = pick_month_index()
        day = random.randint(0, 27)
        inv_date = MONTHS[mi] + timedelta(days=day)
        amount = random_amount(value_scale * random.uniform(0.2, 2.8), customer["status_profile_for_eval"], mi)
        qty = max(1, int(amount / max(25, float(product["mrp"]) * random.uniform(0.25, 1.4))))
        overdue_hint = customer["status_profile_for_eval"] == "credit_watch" and mi > 14
        row = {
            "invoice_id": f"{prefix}INV{i:08d}",
            "invoice_date": date_string(inv_date),
            "posting_month": inv_date.strftime("%Y-%m"),
            "customer_id": customer["customer_id"],
            "customer_name_at_invoice": customer["customer_name"] if random.random() > 0.08 else firm_name(),
            "sku_id": product["sku_id"],
            "sku_name_at_invoice": product["sku_name"] if random.random() > 0.06 else product["sku_name"].replace(" ", "-"),
            "category": product["category"],
            "quantity": qty,
            "uom": product["uom"],
            "gross_amount": as_money(amount),
            "discount_amount": as_money(amount * random.choice([0, 0.02, 0.04, 0.06, 0.10, 0.14])),
            "net_amount": as_money(amount * random.uniform(0.82, 1.0)),
            "scheme_name": random.choice(SCHEMES),
            "sales_rep_id": customer["sales_rep_id"],
            "territory": customer["territory"],
            "state": customer["state"],
            "city": customer["city"],
            "order_source": random.choice(["ERP", "DMS", "WhatsApp", "Salesman app", "Email", "Phone order", "Manual upload"]),
            "payment_status": random.choices(["Paid", "Partial", "Open", "Overdue", "Credit hold"], [52, 17, 18, 10, 3], k=1)[0] if not overdue_hint else random.choice(["Overdue", "Credit hold", "Partial"]),
            "secondary_customer_id": random.choice(customers)["customer_id"] if include_secondary and random.random() < 0.15 else "",
            "free_text_note": random.choice(["", "rate diff", "urgent dispatch", "manual CN pending", "route changed", "partial supply", "dealer asked split bill"]),
        }
        yield row


def credit_rows(customers):
    for c in customers:
        base = int(c["credit_limit"] or 0)
        used = base * random.uniform(0.05, 1.35) if base else random.uniform(0, 25000)
        profile = c["status_profile_for_eval"]
        overdue = used * random.uniform(0.05, 0.55)
        if profile in ["credit_watch", "lost"]:
            overdue = used * random.uniform(0.35, 0.95)
        yield {
            "customer_id": c["customer_id"],
            "customer_name": c["customer_name"],
            "as_of_date": date_string(date(2026, 3, 31)),
            "credit_limit": base,
            "outstanding_amount": as_money(used),
            "not_due_amount": as_money(max(0, used - overdue)),
            "days_1_30": as_money(overdue * random.uniform(0.15, 0.35)),
            "days_31_60": as_money(overdue * random.uniform(0.12, 0.35)),
            "days_61_90": as_money(overdue * random.uniform(0.05, 0.25)),
            "days_90_plus": as_money(overdue * random.uniform(0.02, 0.45)),
            "last_payment_date": date_string(random_date(date(2025, 7, 1), date(2026, 3, 31))),
            "block_flag": "Y" if profile == "credit_watch" and random.random() < 0.35 else random.choice(["N", "N", "N", "Y"]),
            "collector_note": random.choice(["", "cheque bounce", "promised next week", "owner not reachable", "claims adjusted", "limit increase requested"]),
        }


def field_rows(target_rows, customers, prefix, activity_types):
    for i in range(1, target_rows + 1):
        c = random.choice(customers)
        visit_date = random_date(date(2024, 4, 1), date(2026, 3, 31))
        yield {
            "activity_id": f"{prefix}ACT{i:08d}",
            "activity_date": date_string(visit_date),
            "customer_id": c["customer_id"],
            "customer_name": c["customer_name"],
            "activity_type": random.choice(activity_types),
            "sales_rep_id": c["sales_rep_id"],
            "territory": c["territory"],
            "visit_outcome": random.choice(["Order taken", "No order", "Owner absent", "Payment follow-up", "Competitor push seen", "Complaint raised", "Demo done", "Stock checked"]),
            "next_action_date": date_string(visit_date + timedelta(days=random.randint(3, 45))) if random.random() < 0.72 else "",
            "minutes_spent": random.choice([5, 10, 15, 20, 30, 45, 60, "NA"]),
            "lat_long_quality": random.choice(["OK", "outside beat", "missing", "manual", "same gps as prior visit"]),
            "free_text_note": random.choice(["", "asked scheme support", "cash crunch", "shifted to competitor", "new counter opened nearby", "secondary sale low", "stockist dispute"]),
        }


def returns_rows(target_rows, customers, products, prefix, claim_types):
    for i in range(1, target_rows + 1):
        c = random.choice(customers)
        p = random.choice(products)
        claim_date = random_date(date(2024, 4, 1), date(2026, 3, 31))
        amount = random.uniform(300, 85000)
        yield {
            "claim_id": f"{prefix}CLM{i:07d}",
            "claim_date": date_string(claim_date),
            "customer_id": c["customer_id"],
            "customer_name": c["customer_name"],
            "sku_id": p["sku_id"],
            "claim_type": random.choice(claim_types),
            "quantity": random.randint(1, 60),
            "claim_amount": as_money(amount),
            "approved_amount": as_money(amount * random.uniform(0, 1.0)),
            "status": random.choice(["Open", "Approved", "Rejected", "Pending photo", "Credit note raised", "Settled"]),
            "reason_text": random.choice(["leakage", "expired stock", "damaged in transit", "rate difference", "batch issue", "warranty defect", "wrong SKU billed", "dealer says slow moving"]),
            "document_status": random.choice(["complete", "photo missing", "invoice missing", "manual approval", "duplicate suspected"]),
        }


def watchlist_rows(customers, prefix):
    risky = [c for c in customers if c["status_profile_for_eval"] in ["declining", "lost", "credit_watch", "erratic"]]
    random.shuffle(risky)
    for i, c in enumerate(risky[: max(50, min(len(risky), len(customers) // 8))], start=1):
        yield {
            "watch_id": f"{prefix}WL{i:05d}",
            "customer_id": c["customer_id"],
            "customer_name": c["customer_name"],
            "added_by": random.choice(["ASM", "RSM", "Credit", "Distributor", "Service", "Zonal office"]),
            "added_date": date_string(random_date(date(2025, 6, 1), date(2026, 3, 31))),
            "watch_reason": random.choice(["orders down", "payment delay", "competitor offer", "owner dispute", "closed counter", "scheme claim pending", "service complaint", "seasonal crop miss"]),
            "last_known_action": random.choice(["field visit planned", "credit call done", "scheme support requested", "lost to competitor", "new owner to verify", "waiting for payment"]),
            "manager_confidence": random.choice(["low", "medium", "high", "unknown"]),
        }


def markdown_table(rows):
    if not rows:
        return ""
    headers = list(rows[0].keys())
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(row[h]) for h in headers) + " |")
    return "\n".join(out)


def write_company_docs(company_dir, meta, files, dictionaries):
    source_lines = "\n".join(f"- {label}: {url}" for label, url in meta["sources"])
    file_rows = [{"file": f, "rows": rows, "grain": grain} for f, rows, grain in files]
    (company_dir / "README.md").write_text(f"""# {meta['company']} Evaluation Dataset

## Role
{meta['role']}

## Public scale basis
{meta['scale_basis']}

## South operating assumption
{meta['south_assumption']}

## Data files
{markdown_table(file_rows)}

## Public sources
{source_lines}

## Use
Use the transaction file first, then join master, credit, service or field files by customer id. Treat free-text fields, duplicated names, mixed dates, and missing codes as part of the test.
""", encoding="utf-8")

    (company_dir / "regional_manager_notes.md").write_text(f"""# Regional Manager Notes

I run the South region sales number for {meta['company']}. I can move sales reps, change beat plans, push schemes, hold credit requests, and ask distributors to recover inactive counters. I cannot rebuild the data estate.

## What I have
{meta['what_i_have']}

## What I need from a churn system
- Tell me which named customers changed behavior.
- Show which signal changed: order gap, category mix, credit, returns, service, field notes, or scheme friction.
- Let me verify the names against customers my team knows.
- Give me an action file for ASM and distributor follow-up.

## Data limitations
{meta['limitations']}
""", encoding="utf-8")

    (company_dir / "generation_process.md").write_text(f"""# Generation Process

## Step 1: Start from public scale
{meta['step_public_scale']}

## Step 2: Define the manager data boundary
{meta['step_boundary']}

## Step 3: Choose files from first principles
{meta['step_files']}

## Step 4: Add churn-relevant behavior
Customers were assigned stable, growing, declining, lost, credit-watch, seasonal, new, or erratic profiles. Transactions, credit ageing, claims, service events, and visit notes reflect those profiles without adding a model-ready churn label.

## Step 5: Add messy operating data
Names, state values, dates, GST fields, phone numbers, SKU names, free-text notes, and document status fields include issues that a sales head would see in exports from ERP, DMS, field apps, distributor sheets, and service systems.

## Step 6: Keep all names synthetic
Customer, owner, farmer, contractor, and fleet names are synthetic. Company scale facts and URLs are public-source grounded.

## Seed
{SEED}
""", encoding="utf-8")

    dict_lines = [f"# Data Dictionary\n\n## Files\n{markdown_table(file_rows)}\n"]
    for filename, fields in dictionaries.items():
        dict_lines.append(f"\n## {filename}\n")
        dict_lines.append(markdown_table([{"column": c, "meaning": m} for c, m in fields]))
    dict_lines.append("\n## Full column inventory\n")
    for filename, _, _ in files:
        csv_path = company_dir / filename
        if not csv_path.exists() or csv_path.suffix.lower() != ".csv":
            continue
        with csv_path.open(newline="", encoding="utf-8") as f:
            header = next(csv.reader(f))
        rows = []
        for column in header:
            rows.append({
                "file": filename,
                "column": column,
                "meaning": COLUMN_MEANINGS.get(column, "company-specific operating field"),
            })
        dict_lines.append(f"\n### {filename}\n")
        dict_lines.append(markdown_table(rows))
    (company_dir / "data_dictionary.md").write_text("\n".join(dict_lines), encoding="utf-8")


def write_root_readme(company_summaries):
    rows = [{"company": s["company"], "folder": s["folder"], "basis": s["basis"], "main_transaction_file": s["main_file"]} for s in company_summaries]
    (ROOT / "README.md").write_text(f"""# Evals

This folder contains South India sales-head evaluation datasets for four target-market companies. The data is synthetic. Public scale assumptions are sourced in each company README.

## Companies
{markdown_table(rows)}

## Design rule
The dataset starts from the data a regional sales manager could export: masters, transactions, credit, service or claims, field activity, program ledgers, and watchlists. Product behavior should conform to these files rather than requiring cleaned labels or model-ready features.

## Generated files
Each company folder contains four documents:
- README.md
- regional_manager_notes.md
- generation_process.md
- data_dictionary.md

Each company folder also contains CSV files for customer and transaction evidence.
""", encoding="utf-8")


def pidilite():
    d = ROOT / "Pidilite_Industries"
    d.mkdir(parents=True, exist_ok=True)
    products = make_products("PID", {
        "Adhesives": ["Fevicol SH", "Fevicol MR", "Fevicol Marine", "Fevikwik", "Fevistik"],
        "Waterproofing": ["Dr Fixit LW Plus", "Dr Fixit Roofseal", "Dr Fixit Pidifin", "Dr Fixit Raincoat"],
        "Construction chemicals": ["Roff Tile Adhesive", "Roff Grout", "M-Seal", "Fevimate"],
        "Art and craft": ["Fevicryl", "Hobby Ideas Kit", "Rangeela"],
    })
    dealers = make_customers("PIDDLR", 1100, "dealer", "Distributors", channels=["Distributor", "Dealer", "Project dealer", "PKD"])
    outlets = make_customers("PIDOUT", 9000, "retail_outlet", "Hardware", parent_pool=dealers, channels=["Hardware", "Paint shop", "Tile shop", "PKD", "Lumber", "Sanitary"])
    influencers = []
    for i in range(1, 3501):
        state = choose_state()
        geo = geo_for_state(state)
        influencers.append({
            "influencer_id": f"PIDINF{i:06d}",
            "name": owner_name(),
            "influencer_type": random.choice(["Carpenter", "Waterproofing applicator", "Tile contractor", "Mason", "Painter"]),
            "mapped_outlet_id": random.choice(outlets)["customer_id"],
            "state": geo["state_raw"],
            "city": geo["city"],
            "mobile": phone(),
            "loyalty_tier": random.choice(["Bronze", "Silver", "Gold", "Platinum", "Inactive"]),
            "last_app_login": date_string(random_date(date(2024, 4, 1), date(2026, 3, 31))) if random.random() < 0.8 else "",
            "data_quality_note": random.choice(["", "same mobile as dealer", "mapped to old outlet", "name in local language in app", "inactive but purchases seen"]),
        })
    write_csv(d / "sku_master.csv", list(products[0].keys()), products)
    write_csv(d / "dealer_master.csv", list(dealers[0].keys()), dealers)
    write_csv(d / "outlet_master.csv", list(outlets[0].keys()), outlets)
    write_csv(d / "influencer_master.csv", list(influencers[0].keys()), influencers)
    sale_fields = ["invoice_id", "invoice_date", "posting_month", "customer_id", "customer_name_at_invoice", "sku_id", "sku_name_at_invoice", "category", "quantity", "uom", "gross_amount", "discount_amount", "net_amount", "scheme_name", "sales_rep_id", "territory", "state", "city", "order_source", "payment_status", "secondary_customer_id", "free_text_note"]
    write_csv_stream(d / "primary_sales.csv", sale_fields, sales_rows(55000, dealers + outlets, products, "PID", "primary", 22000, True))
    write_csv_stream(d / "credit_aging.csv", ["customer_id", "customer_name", "as_of_date", "credit_limit", "outstanding_amount", "not_due_amount", "days_1_30", "days_31_60", "days_61_90", "days_90_plus", "last_payment_date", "block_flag", "collector_note"], credit_rows(dealers))
    write_csv_stream(d / "field_activity.csv", ["activity_id", "activity_date", "customer_id", "customer_name", "activity_type", "sales_rep_id", "territory", "visit_outcome", "next_action_date", "minutes_spent", "lat_long_quality", "free_text_note"], field_rows(12000, dealers + outlets, "PID", ["Beat visit", "PKD audit", "Counter meet", "Applicator demo", "Payment follow-up", "Complaint follow-up"]))
    write_csv_stream(d / "scheme_claims_returns.csv", ["claim_id", "claim_date", "customer_id", "customer_name", "sku_id", "claim_type", "quantity", "claim_amount", "approved_amount", "status", "reason_text", "document_status"], returns_rows(4000, dealers + outlets, products, "PID", ["Damage return", "Leakage", "Expiry", "Scheme claim", "Rate difference", "Short supply"]))
    purchase_fields = ["purchase_id", "purchase_date", "influencer_id", "mapped_outlet_id", "sku_id", "points_earned", "purchase_value", "bill_photo_status", "approval_status", "note"]
    def inf_purchases():
        for i in range(1, 26001):
            inf = random.choice(influencers)
            product = random.choice(products)
            val = random.uniform(150, 18000)
            yield {"purchase_id": f"PIDINFBUY{i:08d}", "purchase_date": date_string(random_date()), "influencer_id": inf["influencer_id"], "mapped_outlet_id": inf["mapped_outlet_id"], "sku_id": product["sku_id"], "points_earned": int(val / random.uniform(20, 75)), "purchase_value": as_money(val), "bill_photo_status": random.choice(["ok", "blurred", "missing", "duplicate", "manual"]), "approval_status": random.choice(["approved", "pending", "rejected", "rework"]), "note": random.choice(["", "same bill twice", "dealer name mismatch", "old SKU code", "cash bill"])}
    write_csv_stream(d / "influencer_purchases.csv", purchase_fields, inf_purchases())
    write_csv_stream(d / "manager_watchlist.csv", ["watch_id", "customer_id", "customer_name", "added_by", "added_date", "watch_reason", "last_known_action", "manager_confidence"], watchlist_rows(dealers + outlets, "PID"))
    files = [("dealer_master.csv", len(dealers), "one row per billed dealer/distributor"), ("outlet_master.csv", len(outlets), "one row per outlet in regional panel"), ("sku_master.csv", len(products), "one row per SKU/pack"), ("primary_sales.csv", 55000, "one row per invoice line"), ("credit_aging.csv", len(dealers), "one row per dealer as of 2026-03-31"), ("influencer_master.csv", len(influencers), "one row per carpenter/applicator"), ("influencer_purchases.csv", 26000, "one row per loyalty bill event"), ("field_activity.csv", 12000, "one row per visit/activity"), ("scheme_claims_returns.csv", 4000, "one row per claim/return"), ("manager_watchlist.csv", max(50, (len(dealers)+len(outlets))//8), "one row per team watch item")]
    meta = {
        "company": "Pidilite Industries",
        "role": "South regional sales manager for adhesives, waterproofing, construction chemicals, and trade channels.",
        "scale_basis": "Pidilite FY25 reports 9,082 dealers/distributors and 88% of sales through dealer/distributor channels. Investor call transcripts mention close to 6 lakh outlets and PKD/Dr Fixit route-to-market programs.",
        "south_assumption": "The regional extract models about 1,100 billed dealers, 9,000 outlets, and 3,500 mapped influencers from South India. This is an operating panel, not the full national outlet universe.",
        "sources": [("Pidilite FY25 annual report", "https://www.pidilite.com/content/dam/pidilitecorporatewebsite/financial/annual-reports/annual-report-2024-25.pdf"), ("Pidilite FY25 Q2 transcript", "https://www.pidilite.com/content/dam/pidilitecorporatewebsite/financial/quarterly-reports/fy-2024-25/q2/Analyst%20Call%20Transcript.pdf"), ("Pidilite FY25 Q4 transcript", "https://www.pidilite.com/content/dam/pidilitecorporatewebsite/financial/quarterly-reports/fy-2024-25/q4/se-intimation-transcript-of-earnings-call-q4.pdf")],
        "what_i_have": "ERP primary invoices, dealer ageing, outlet panel from DMS, loyalty-app bills from carpenters/applicators, scheme claims, returns, and sales-app visits.",
        "limitations": "Outlets change parent distributor, GST is missing for small counters, influencer bills can map to the wrong shop, and field visit notes are free text.",
        "step_public_scale": "The public dealer and outlet scale sets the regional order of magnitude.",
        "step_boundary": "The manager sees South India with dealer billing, outlet panel, field team and loyalty program data.",
        "step_files": "Files follow the manager's joins: dealer/outlet master plus invoice lines, credit, field, loyalty, and claims.",
    }
    dicts = {
        "dealer_master.csv / outlet_master.csv": [("customer_id", "synthetic regional customer key"), ("parent_customer_id", "outlet to dealer link when present"), ("status_profile_for_eval", "synthetic behavior driver for evaluation only")],
        "primary_sales.csv": [("invoice_id", "invoice line key"), ("posting_month", "month for aggregation"), ("net_amount", "sales value after discount"), ("payment_status", "open/paid/overdue signal")],
        "credit_aging.csv": [("days_90_plus", "overdue bucket"), ("block_flag", "credit hold signal")],
        "field_activity.csv": [("visit_outcome", "rep outcome"), ("free_text_note", "unstructured sales note")],
        "influencer_purchases.csv": [("points_earned", "loyalty points"), ("bill_photo_status", "data quality/service friction")],
    }
    write_company_docs(d, meta, files, dicts)
    return {"company": "Pidilite Industries", "folder": "Pidilite_Industries", "basis": "9,082 dealers/distributors; close to 6 lakh outlets", "main_file": "primary_sales.csv"}


def asian_paints():
    d = ROOT / "Asian_Paints"
    d.mkdir(parents=True, exist_ok=True)
    products = make_products("ASP", {
        "Decorative paints": ["Royale Luxury", "Apcolite Premium", "Tractor Emulsion", "Ace Exterior", "Apex Ultima"],
        "Waterproofing": ["SmartCare Damp Proof", "SmartCare Hydroloc", "SmartCare Crack Seal"],
        "Wood finishes": ["Touchwood", "Melamyne", "Woodtech"],
        "Services": ["Beautiful Homes Painting", "Colour Consultancy", "Project Supply"],
    })
    dealers = make_customers("ASPDLR", 1000, "dealer", "Paints", channels=["Dealer", "Colour World", "Beautiful Homes", "Project dealer", "Distributor"])
    contractors = []
    for i in range(1, 5001):
        state = choose_state()
        geo = geo_for_state(state)
        contractors.append({
            "contractor_id": f"ASPCON{i:06d}",
            "contractor_name": owner_name(),
            "mapped_dealer_id": random.choice(dealers)["customer_id"],
            "state": geo["state_raw"],
            "city": geo["city"],
            "mobile": phone(),
            "tier": random.choice(["Registered", "Silver", "Gold", "Elite", "Dormant"]),
            "specialty": random.choice(["Interior repaint", "Exterior", "Waterproofing", "Luxury", "Projects"]),
            "last_training_date": date_string(random_date(date(2023, 1, 1), date(2026, 3, 31))) if random.random() < 0.65 else "",
            "data_quality_note": random.choice(["", "same mobile as helper", "dealer mapping old", "spelling mismatch", "inactive but claims points"]),
        })
    tint_machines = []
    for i in range(1, 651):
        dealer = random.choice(dealers)
        tint_machines.append({"machine_id": f"ASPTINT{i:05d}", "dealer_id": dealer["customer_id"], "dealer_name": dealer["customer_name"], "install_date": date_string(random_date(date(2015, 1, 1), date(2025, 12, 31))), "machine_model": random.choice(["CW-Classic", "CW-Pro", "CW-Express", "BH-Studio"]), "service_status": random.choice(["OK", "Calibration due", "Down", "Old", "Shifted"]), "last_service_date": date_string(random_date(date(2024, 4, 1), date(2026, 3, 31)))})
    write_csv(d / "dealer_master.csv", list(dealers[0].keys()), dealers)
    write_csv(d / "sku_master.csv", list(products[0].keys()), products)
    write_csv(d / "contractor_master.csv", list(contractors[0].keys()), contractors)
    write_csv(d / "tinting_machine_master.csv", list(tint_machines[0].keys()), tint_machines)
    sale_fields = ["invoice_id", "invoice_date", "posting_month", "customer_id", "customer_name_at_invoice", "sku_id", "sku_name_at_invoice", "category", "quantity", "uom", "gross_amount", "discount_amount", "net_amount", "scheme_name", "sales_rep_id", "territory", "state", "city", "order_source", "payment_status", "secondary_customer_id", "free_text_note"]
    write_csv_stream(d / "secondary_sales.csv", sale_fields, sales_rows(60000, dealers, products, "ASP", "secondary", 38000, False))
    write_csv_stream(d / "credit_aging.csv", ["customer_id", "customer_name", "as_of_date", "credit_limit", "outstanding_amount", "not_due_amount", "days_1_30", "days_31_60", "days_61_90", "days_90_plus", "last_payment_date", "block_flag", "collector_note"], credit_rows(dealers))
    def tint_events():
        for i in range(1, 30001):
            m = random.choice(tint_machines)
            dt = random_date()
            yield {"event_id": f"ASPTNTEVT{i:08d}", "event_date": date_string(dt), "machine_id": m["machine_id"], "dealer_id": m["dealer_id"], "colour_code": random.choice(["L124", "N093", "R156", "W001", "Y076", "custom", "missing"]), "base_liters": as_money(random.uniform(0.5, 60)), "can_count": random.randint(1, 35), "status": random.choice(["dispensed", "cancelled", "manual formula", "service error", "re-tint"]), "note": random.choice(["", "machine down", "shade mismatch", "manual entry", "power cut"])}
    write_csv_stream(d / "tinting_machine_events.csv", ["event_id", "event_date", "machine_id", "dealer_id", "colour_code", "base_liters", "can_count", "status", "note"], tint_events())
    def contractor_ledger():
        for i in range(1, 5001):
            c = random.choice(contractors)
            yield {"ledger_id": f"ASPCONLED{i:08d}", "activity_date": date_string(random_date()), "contractor_id": c["contractor_id"], "mapped_dealer_id": c["mapped_dealer_id"], "activity_type": random.choice(["bill upload", "training", "site lead", "points redemption", "complaint assist"]), "points_delta": random.randint(-500, 2500), "bill_value": as_money(random.uniform(0, 90000)), "approval_status": random.choice(["approved", "pending", "rejected", "duplicate", "manual"]), "note": random.choice(["", "dealer mismatch", "bill image unclear", "site closed", "redeemed gift"])}
    write_csv_stream(d / "contractor_loyalty_ledger.csv", ["ledger_id", "activity_date", "contractor_id", "mapped_dealer_id", "activity_type", "points_delta", "bill_value", "approval_status", "note"], contractor_ledger())
    write_csv_stream(d / "beat_visit_log.csv", ["activity_id", "activity_date", "customer_id", "customer_name", "activity_type", "sales_rep_id", "territory", "visit_outcome", "next_action_date", "minutes_spent", "lat_long_quality", "free_text_note"], field_rows(15000, dealers, "ASP", ["Beat visit", "Colour World check", "Contractor meet", "Service visit", "Scheme follow-up", "Project lead follow-up"]))
    write_csv_stream(d / "complaints_returns.csv", ["claim_id", "claim_date", "customer_id", "customer_name", "sku_id", "claim_type", "quantity", "claim_amount", "approved_amount", "status", "reason_text", "document_status"], returns_rows(6000, dealers, products, "ASP", ["Shade complaint", "Damaged stock", "Expiry", "Rate difference", "Service complaint", "Return", "Scheme claim"]))
    def project_leads():
        for i in range(1, 3001):
            dealer = random.choice(dealers)
            val = random.uniform(25000, 3000000)
            yield {"lead_id": f"ASPLEAD{i:07d}", "lead_date": date_string(random_date()), "mapped_dealer_id": dealer["customer_id"], "lead_type": random.choice(["Apartment repaint", "Villa", "Commercial", "Waterproofing", "Beautiful Homes", "Builder project"]), "stage": random.choice(["new", "quoted", "site visit", "won", "lost", "stalled"]), "estimated_value": as_money(val), "competitor_seen": random.choice(["Berger", "Nerolac", "JSW", "Indigo", "Local", "None", "unknown"]), "note": random.choice(["", "price high", "contractor controls decision", "dealer asked extra margin", "payment risk"])}
    write_csv_stream(d / "project_leads.csv", ["lead_id", "lead_date", "mapped_dealer_id", "lead_type", "stage", "estimated_value", "competitor_seen", "note"], project_leads())
    write_csv_stream(d / "manager_watchlist.csv", ["watch_id", "customer_id", "customer_name", "added_by", "added_date", "watch_reason", "last_known_action", "manager_confidence"], watchlist_rows(dealers, "ASP"))
    files = [("dealer_master.csv", len(dealers), "one row per billed dealer"), ("sku_master.csv", len(products), "one row per SKU/pack"), ("secondary_sales.csv", 60000, "one row per invoice line"), ("credit_aging.csv", len(dealers), "one row per dealer"), ("tinting_machine_master.csv", len(tint_machines), "one row per tinting machine"), ("tinting_machine_events.csv", 30000, "one row per tint event"), ("contractor_master.csv", len(contractors), "one row per contractor"), ("contractor_loyalty_ledger.csv", 5000, "one row per contractor program event"), ("beat_visit_log.csv", 15000, "one row per field visit"), ("complaints_returns.csv", 6000, "one row per complaint/return"), ("project_leads.csv", 3000, "one row per project lead"), ("manager_watchlist.csv", max(50, len(dealers)//8), "one row per team watch item")]
    meta = {
        "company": "Asian Paints",
        "role": "South regional sales manager for decorative paints, waterproofing, dealer retail and service-led channels.",
        "scale_basis": "Asian Paints FY24 reports 160,000+ retail touchpoints, 74,129 dealers/distributors billed, and 99.1% sales through dealers/distributors.",
        "south_assumption": "The regional extract models 1,000 billed dealers, 650 tinting machines, and 5,000 contractors from the South operating panel. A full regional dump would be larger; this extract preserves the joins and signals.",
        "sources": [("Asian Paints FY24 annual report", "https://www.asianpaints.com/content/dam/asianpaints/website/secondary-navigation/investors/annual-reports/2023-2024/Asian_Paints_FY24_AnnualReport.pdf"), ("Asian Paints strategic review", "https://www.asianpaints.com/content/dam/annual-report/annualreport-19-20/pdf/Strategic_review.pdf")],
        "what_i_have": "Dealer billing, secondary sales, credit ageing, tinting machine logs, contractor loyalty activity, complaints, returns, field visits and project leads.",
        "limitations": "One shop can be a dealer, Colour World and service participant. Tinting data has machine downtime. Contractors change dealer mapping. Project leads have manual stages.",
        "step_public_scale": "The public retail touchpoint and billed dealer counts define a dealer-led network with service overlays.",
        "step_boundary": "The manager sees dealer sales, machine usage, contractor behavior, complaints and lead movement.",
        "step_files": "Files follow sales loss causes: lower billing, tinting usage drop, contractor inactivity, credit, complaints, and project lead leakage.",
    }
    dicts = {
        "secondary_sales.csv": [("customer_id", "dealer key"), ("posting_month", "aggregation month"), ("net_amount", "dealer sales value"), ("free_text_note", "manual sales note")],
        "tinting_machine_events.csv": [("machine_id", "machine key"), ("base_liters", "paint base usage"), ("status", "dispense/service state")],
        "contractor_loyalty_ledger.csv": [("contractor_id", "program participant"), ("points_delta", "loyalty movement"), ("approval_status", "program friction")],
        "project_leads.csv": [("stage", "lead stage"), ("competitor_seen", "free-text competitor signal")],
    }
    write_company_docs(d, meta, files, dicts)
    return {"company": "Asian Paints", "folder": "Asian_Paints", "basis": "160,000+ touchpoints; 74,129 billed dealers/distributors", "main_file": "secondary_sales.csv"}


def ceat():
    d = ROOT / "CEAT"
    d.mkdir(parents=True, exist_ok=True)
    products = make_products("CEA", {
        "Two wheeler": ["Zoom", "Milaze", "Gripp", "Secura"],
        "Passenger car": ["SecuraDrive", "Milaze X3", "SportDrive", "Czar"],
        "Truck bus": ["WinLoad", "Buland", "Rock XL", "Mile XL"],
        "Farm": ["Aayushmaan", "Samraat", "Vardhan", "Farmax"],
        "LCV": ["Mile XL Pro", "LoadPro", "Buland LCV"],
    })
    dealers = make_customers("CEADLR", 750, "dealer", "Tyres", channels=["Dealer", "CEAT Shoppe", "Distributor", "Fleet dealer", "Rural sub dealer"])
    subdealers = make_customers("CEASUB", 4500, "sub_dealer", "Tyres", parent_pool=dealers, channels=["Sub dealer", "Puncture shop", "Wheel alignment", "Rural retail", "Mechanic"])
    fleets = []
    for i in range(1, 321):
        state = choose_state()
        geo = geo_for_state(state)
        fleets.append({"fleet_id": f"CEAFLEET{i:05d}", "fleet_name": firm_name("Logistics"), "mapped_dealer_id": random.choice(dealers)["customer_id"], "state": geo["state_raw"], "city": geo["city"], "vehicle_count": random.randint(8, 650), "segment": random.choice(["Bus", "Truck", "LCV", "Mining", "Agri", "Taxi"]), "contract_status": random.choice(["active", "trial", "expired", "lost", "rate negotiation"]), "last_review_date": date_string(random_date(date(2024, 4, 1), date(2026, 3, 31))), "note": random.choice(["", "price pressure", "claims pending", "OEM fitment", "competitor test running"] )})
    write_csv(d / "dealer_master.csv", list(dealers[0].keys()), dealers)
    write_csv(d / "subdealer_master.csv", list(subdealers[0].keys()), subdealers)
    write_csv(d / "sku_master.csv", list(products[0].keys()), products)
    write_csv(d / "fleet_accounts.csv", list(fleets[0].keys()), fleets)
    sale_fields = ["invoice_id", "invoice_date", "posting_month", "customer_id", "customer_name_at_invoice", "sku_id", "sku_name_at_invoice", "category", "quantity", "uom", "gross_amount", "discount_amount", "net_amount", "scheme_name", "sales_rep_id", "territory", "state", "city", "order_source", "payment_status", "secondary_customer_id", "free_text_note"]
    write_csv_stream(d / "sales_invoices.csv", sale_fields, sales_rows(50000, dealers + subdealers, products, "CEA", "replacement", 30000, True))
    write_csv_stream(d / "credit_aging.csv", ["customer_id", "customer_name", "as_of_date", "credit_limit", "outstanding_amount", "not_due_amount", "days_1_30", "days_31_60", "days_61_90", "days_90_plus", "last_payment_date", "block_flag", "collector_note"], credit_rows(dealers))
    def warranty_regs():
        for i in range(1, 10001):
            c = random.choice(dealers + subdealers)
            p = random.choice(products)
            sale_dt = random_date(date(2024, 4, 1), date(2026, 3, 1))
            yield {"registration_id": f"CEAWAR{i:08d}", "registration_date": date_string(sale_dt + timedelta(days=random.randint(0, 30))), "dealer_id": c["customer_id"], "dealer_name": c["customer_name"], "sku_id": p["sku_id"], "tyre_serial_no": maybe_blank(f"{random.choice(['A','B','C','D'])}{random.randint(1000000,9999999)}", 0.04), "vehicle_type": random.choice(["2W", "Car", "Truck", "Bus", "LCV", "Tractor"]), "customer_mobile": phone(), "km_at_registration": random.choice([0, random.randint(100, 75000), "NA"]), "extra_warranty_flag": random.choice(["Y", "N", "pending"]), "source": random.choice(["dealer app", "website", "call center", "manual", "fleet upload"])}
    write_csv_stream(d / "warranty_registrations.csv", ["registration_id", "registration_date", "dealer_id", "dealer_name", "sku_id", "tyre_serial_no", "vehicle_type", "customer_mobile", "km_at_registration", "extra_warranty_flag", "source"], warranty_regs())
    write_csv_stream(d / "claims.csv", ["claim_id", "claim_date", "customer_id", "customer_name", "sku_id", "claim_type", "quantity", "claim_amount", "approved_amount", "status", "reason_text", "document_status"], returns_rows(2500, dealers + subdealers, products, "CEA", ["Warranty claim", "Manufacturing defect", "Road hazard", "Tread wear", "Bead damage", "Transit damage", "Scheme claim"]))
    def fleet_logs():
        for i in range(1, 9001):
            f = random.choice(fleets)
            yield {"service_id": f"CEAFS{i:08d}", "service_date": date_string(random_date()), "fleet_id": f["fleet_id"], "mapped_dealer_id": f["mapped_dealer_id"], "vehicle_no": f"{random.choice(['TN','KA','TS','AP','KL'])}{random.randint(10,99)}{random.choice(['AB','CD','EF','GH','JK'])}{random.randint(1000,9999)}", "service_type": random.choice(["inspection", "rotation", "alignment", "claim check", "pressure audit", "fitment"]), "tyres_checked": random.randint(2, 32), "issue_count": random.randint(0, 8), "recommended_action": random.choice(["none", "replace", "rotate", "claim", "alignment", "pressure training"]), "note": random.choice(["", "driver unavailable", "fleet price issue", "high wear", "competitor tyres fitted"])}
    write_csv_stream(d / "fleet_service_logs.csv", ["service_id", "service_date", "fleet_id", "mapped_dealer_id", "vehicle_no", "service_type", "tyres_checked", "issue_count", "recommended_action", "note"], fleet_logs())
    write_csv_stream(d / "field_visits.csv", ["activity_id", "activity_date", "customer_id", "customer_name", "activity_type", "sales_rep_id", "territory", "visit_outcome", "next_action_date", "minutes_spent", "lat_long_quality", "free_text_note"], field_rows(7000, dealers + subdealers, "CEA", ["Dealer visit", "Sub dealer visit", "Fleet meet", "Mechanic meet", "Claim follow-up", "Scheme follow-up"]))
    write_csv_stream(d / "scheme_redemptions.csv", ["claim_id", "claim_date", "customer_id", "customer_name", "sku_id", "claim_type", "quantity", "claim_amount", "approved_amount", "status", "reason_text", "document_status"], returns_rows(3500, dealers + subdealers, products, "CEA", ["Consumer offer", "Dealer slab", "Fleet rebate", "Display support", "Subdealer coupon", "Rate difference"]))
    write_csv_stream(d / "manager_watchlist.csv", ["watch_id", "customer_id", "customer_name", "added_by", "added_date", "watch_reason", "last_known_action", "manager_confidence"], watchlist_rows(dealers + subdealers, "CEA"))
    files = [("dealer_master.csv", len(dealers), "one row per billed dealer"), ("subdealer_master.csv", len(subdealers), "one row per subdealer/retail point"), ("sku_master.csv", len(products), "one row per tyre SKU/size"), ("sales_invoices.csv", 50000, "one row per invoice line"), ("credit_aging.csv", len(dealers), "one row per dealer"), ("warranty_registrations.csv", 10000, "one row per registered tyre warranty"), ("claims.csv", 2500, "one row per claim"), ("fleet_accounts.csv", len(fleets), "one row per fleet"), ("fleet_service_logs.csv", 9000, "one row per fleet service event"), ("field_visits.csv", 7000, "one row per field visit"), ("scheme_redemptions.csv", 3500, "one row per redemption/claim"), ("manager_watchlist.csv", max(50, (len(dealers)+len(subdealers))//8), "one row per team watch item")]
    meta = {
        "company": "CEAT",
        "role": "South regional sales manager for replacement tyres, subdealer coverage, fleet accounts and service claims.",
        "scale_basis": "CEAT public pages report 400+ exclusive outlets, 4,500+ dealers, and 51,000+ sub-dealers. FY25 investor material reports 61,000+ sales touchpoints and 5,700+ dealers.",
        "south_assumption": "The regional extract models 750 billed dealers, 4,500 subdealers, 320 fleets, warranty registrations, claims and service logs.",
        "sources": [("CEAT About Us", "https://www.ceat.com/corporate/about-us.html"), ("CEAT annual reports page", "https://www.ceat.com/investors/annual-reports.html"), ("CEAT FY25 annual report", "https://www.ceat.com/content/dam/ceat/pdf/Annual_Reports/Annual-reports-fy-25.pdf"), ("CEAT warranty", "https://www.ceat.com/warranty.html"), ("CEAT claims", "https://www.ceat.com/claims.html")],
        "what_i_have": "Replacement sales invoices, dealer/subdealer master, dealer credit, warranty registration, claims, fleet service logs, scheme redemptions and field visits.",
        "limitations": "Tyre serial numbers can be missing or OCR-like. Warranty and sales customer identities do not always match. Fleet service data sits outside sales invoices.",
        "step_public_scale": "The public touchpoint, dealer and subdealer scale defines a replacement-network dataset with service evidence.",
        "step_boundary": "The manager sees South replacement channel and fleet service data, not OEM primary planning.",
        "step_files": "Files cover dealer/subdealer churn, service friction, claim load, warranty pull-through and fleet retention.",
    }
    dicts = {
        "sales_invoices.csv": [("customer_id", "dealer or subdealer key"), ("category", "tyre segment"), ("payment_status", "credit signal")],
        "warranty_registrations.csv": [("tyre_serial_no", "serial number with missing values"), ("extra_warranty_flag", "consumer registration status")],
        "claims.csv": [("reason_text", "service reason"), ("document_status", "claim document state")],
        "fleet_service_logs.csv": [("issue_count", "service issue volume"), ("recommended_action", "service recommendation")],
    }
    write_company_docs(d, meta, files, dicts)
    return {"company": "CEAT", "folder": "CEAT", "basis": "400+ exclusive outlets; 4,500+ dealers; 51,000+ sub-dealers", "main_file": "sales_invoices.csv"}


def coromandel():
    d = ROOT / "Coromandel_International"
    d.mkdir(parents=True, exist_ok=True)
    products = make_products("COR", {
        "Fertiliser": ["Gromor 28-28-0", "Gromor 14-35-14", "DAP", "Urea", "Potash"],
        "Specialty nutrients": ["Gromor Spray", "Zinc Sulphate", "Water soluble NPK", "Bentonite Sulphur"],
        "Crop protection": ["Insecticide A", "Fungicide B", "Herbicide C", "Seed treatment D"],
        "Organic and bio": ["City Compost", "Neem Cake", "Bio stimulant", "Mycorrhiza"],
    })
    store_weights = [("Andhra Pradesh", 0.45), ("Telangana", 0.29), ("Karnataka", 0.23), ("Tamil Nadu", 0.03)]
    stores = []
    for i in range(1, 1152):
        state = choose_state(store_weights)
        geo = geo_for_state(state)
        brand = "Mana Gromor" if state in ["Andhra Pradesh", "Telangana"] else "Namma Gromor" if state == "Karnataka" else "Nammadu Gromor"
        stores.append({"store_id": f"CORSTR{i:05d}", "store_name": f"{brand} {geo['city']} {random.randint(1,9)}", "brand": brand, "state": geo["state_raw"], "state_clean": state, "district": geo["district"], "city": geo["city"], "pincode": geo["pincode"], "opened_date": date_string(random_date(date(2007, 1, 1), date(2026, 4, 22))), "store_type": random.choice(["company owned", "hub", "satellite", "seasonal extension"]), "agronomist_mapped": random.choice(["Y", "N", "shared"]), "data_quality_note": random.choice(["", "brand spelling varies", "old store code", "district split", "new store from FY26"] )})
    dealers = make_customers("CORDLR", 3000, "dealer_distributor", "Agro", channels=["Dealer", "Distributor", "Retailer", "Cooperative", "Input shop"])
    farmers = []
    crops = ["Paddy", "Cotton", "Maize", "Chilli", "Groundnut", "Sugarcane", "Banana", "Coconut", "Vegetables", "Turmeric", "Mango"]
    for i in range(1, 25001):
        state = choose_state(store_weights)
        geo = geo_for_state(state)
        farmers.append({"farmer_id": f"CORFRM{i:07d}", "farmer_name": owner_name(), "mapped_store_id": random.choice(stores)["store_id"], "mapped_dealer_id": random.choice(dealers)["customer_id"] if random.random() < 0.35 else "", "state": geo["state_raw"], "district": geo["district"], "village": random.choice([geo["city"] + " Rural", "Kottapalli", "Rampur", "Melur", "Halli", "Cheruvu", "Palem", "Pudur"]), "mobile": phone(), "primary_crop": random.choice(crops), "acreage": round(random.uniform(0.5, 35), 2), "irrigation": random.choice(["rainfed", "borewell", "canal", "drip", "unknown"]), "data_quality_note": random.choice(["", "same mobile in family", "village spelling mismatch", "crop not updated", "mapped to nearest store"] )})
    write_csv(d / "retail_outlets.csv", list(stores[0].keys()), stores)
    write_csv(d / "dealer_distributors.csv", list(dealers[0].keys()), dealers)
    write_csv(d / "farmer_master.csv", list(farmers[0].keys()), farmers)
    write_csv(d / "product_master.csv", list(products[0].keys()), products)
    tx_fields = ["invoice_id", "invoice_date", "posting_month", "customer_id", "customer_name_at_invoice", "sku_id", "sku_name_at_invoice", "category", "quantity", "uom", "gross_amount", "discount_amount", "net_amount", "scheme_name", "sales_rep_id", "territory", "state", "city", "order_source", "payment_status", "secondary_customer_id", "free_text_note"]
    dealer_tx = sales_rows(45000, dealers, products, "COR", "dealer", 55000, False)
    def farmer_sales(n):
        for i in range(1, n + 1):
            f = random.choice(farmers)
            p = random.choice(products)
            mi = pick_month_index()
            dt = MONTHS[mi] + timedelta(days=random.randint(0, 27))
            amount = random.uniform(300, 45000)
            yield {"invoice_id": f"CORFARM{i:08d}", "invoice_date": date_string(dt), "posting_month": dt.strftime("%Y-%m"), "customer_id": f["farmer_id"], "customer_name_at_invoice": f["farmer_name"], "sku_id": p["sku_id"], "sku_name_at_invoice": p["sku_name"], "category": p["category"], "quantity": random.randint(1, 80), "uom": random.choice(["BAG", "KG", "LTR", "PKT"]), "gross_amount": as_money(amount), "discount_amount": as_money(amount * random.choice([0, 0.02, 0.05, 0.1])), "net_amount": as_money(amount * random.uniform(0.88, 1.0)), "scheme_name": random.choice(["None", "crop season promo", "soil test bundle", "store launch", "cash discount", "drone demo follow-up"]), "sales_rep_id": random.choice(SALES_REPS), "territory": f["district"], "state": f["state"], "city": f["village"], "order_source": random.choice(["retail POS", "store app", "dealer sheet", "manual book", "WhatsApp"]), "payment_status": random.choice(["Paid", "Open", "Partial", "cash", "subsidy pending"]), "secondary_customer_id": f["mapped_store_id"], "free_text_note": random.choice(["", "crop failure", "monsoon delayed", "asked agronomist", "dealer supplied", "price issue"])}
    def all_tx():
        for row in dealer_tx:
            yield row
        for row in farmer_sales(35000):
            yield row
    write_csv_stream(d / "transactions.csv", tx_fields, all_tx())
    write_csv_stream(d / "credit_aging.csv", ["customer_id", "customer_name", "as_of_date", "credit_limit", "outstanding_amount", "not_due_amount", "days_1_30", "days_31_60", "days_61_90", "days_90_plus", "last_payment_date", "block_flag", "collector_note"], credit_rows(dealers))
    def soil_tests():
        for i in range(1, 15001):
            f = random.choice(farmers)
            yield {"test_id": f"CORSOIL{i:08d}", "test_date": date_string(random_date()), "farmer_id": f["farmer_id"], "mapped_store_id": f["mapped_store_id"], "crop": f["primary_crop"], "ph": round(random.uniform(5.2, 8.8), 1), "organic_carbon": round(random.uniform(0.2, 1.4), 2), "npk_status": random.choice(["low N", "low P", "low K", "balanced", "salinity", "missing sample"]), "recommendation": random.choice(["NPK dose", "lime", "organic carbon", "micronutrient", "water management", "repeat sample"]), "followup_purchase_seen": random.choice(["Y", "N", "unknown"]), "note": random.choice(["", "sample label torn", "farmer not reachable", "crop changed", "village camp"])}
    write_csv_stream(d / "soil_tests.csv", ["test_id", "test_date", "farmer_id", "mapped_store_id", "crop", "ph", "organic_carbon", "npk_status", "recommendation", "followup_purchase_seen", "note"], soil_tests())
    def drone_sprays():
        for i in range(1, 7001):
            f = random.choice(farmers)
            yield {"spray_id": f"CORDRN{i:08d}", "spray_date": date_string(random_date()), "farmer_id": f["farmer_id"], "mapped_store_id": f["mapped_store_id"], "crop": f["primary_crop"], "acreage_sprayed": round(random.uniform(0.5, min(20, float(f["acreage"]))), 2), "product_used": random.choice(products)["sku_id"], "service_status": random.choice(["completed", "rescheduled", "cancelled", "weather hold", "payment pending"]), "operator_id": f"DRN{random.randint(1,249):04d}", "note": random.choice(["", "wind issue", "tank shortage", "farmer absent", "repeat booking"])}
    write_csv_stream(d / "drone_sprays.csv", ["spray_id", "spray_date", "farmer_id", "mapped_store_id", "crop", "acreage_sprayed", "product_used", "service_status", "operator_id", "note"], drone_sprays())
    write_csv_stream(d / "field_activity.csv", ["activity_id", "activity_date", "customer_id", "customer_name", "activity_type", "sales_rep_id", "territory", "visit_outcome", "next_action_date", "minutes_spent", "lat_long_quality", "free_text_note"], field_rows(25000, dealers, "COR", ["Dealer visit", "Farmer meeting", "Crop demo", "Soil camp", "Drone demo", "Payment follow-up", "Stock check"]))
    def demos():
        for i in range(1, 1001):
            f = random.choice(farmers)
            yield {"demo_id": f"CORDEMO{i:06d}", "demo_start_date": date_string(random_date(date(2024, 4, 1), date(2026, 1, 31))), "farmer_id": f["farmer_id"], "mapped_store_id": f["mapped_store_id"], "crop": f["primary_crop"], "product_focus": random.choice(products)["sku_id"], "plot_area_acres": round(random.uniform(0.1, 3), 2), "stage": random.choice(["planned", "in progress", "harvested", "abandoned", "converted"]), "result_note": random.choice(["", "good crop stand", "rain damage", "farmer bought later", "competitor demo nearby", "photo missing"])}
    write_csv_stream(d / "demo_plots.csv", ["demo_id", "demo_start_date", "farmer_id", "mapped_store_id", "crop", "product_focus", "plot_area_acres", "stage", "result_note"], demos())
    write_csv_stream(d / "manager_watchlist.csv", ["watch_id", "customer_id", "customer_name", "added_by", "added_date", "watch_reason", "last_known_action", "manager_confidence"], watchlist_rows(dealers, "COR"))
    files = [("retail_outlets.csv", len(stores), "one row per Gromor store"), ("dealer_distributors.csv", len(dealers), "one row per dealer/distributor"), ("farmer_master.csv", len(farmers), "one row per farmer in store/dealer panel"), ("product_master.csv", len(products), "one row per product/pack"), ("transactions.csv", 80000, "one row per dealer or farmer sale"), ("credit_aging.csv", len(dealers), "one row per dealer/distributor"), ("soil_tests.csv", 15000, "one row per soil test"), ("drone_sprays.csv", 7000, "one row per spray service"), ("field_activity.csv", 25000, "one row per sales/agronomy activity"), ("demo_plots.csv", 1000, "one row per demo plot"), ("manager_watchlist.csv", max(50, len(dealers)//8), "one row per team watch item")]
    meta = {
        "company": "Coromandel International",
        "role": "South regional sales manager for agri-inputs across company retail stores, dealers, farmers and services.",
        "scale_basis": "Coromandel announced 1,200 Gromor stores on April 22, 2026, including 850 in Andhra Pradesh/Telangana, 270 in Karnataka and 31 in Tamil Nadu, serving over 5 million farmers. FY25 reporting lists 13,060 dealers/distributors and 48% of sales through dealers/distributors.",
        "south_assumption": "The regional dataset uses the actual public South store count of 1,151 stores, plus a 3,000 dealer/distributor panel and 25,000 farmer records from store, dealer and service touchpoints.",
        "sources": [("Coromandel 1,200th Gromor store press release", "https://www.coromandel.biz/press-release/coromandel-international-marks-milestone-with-1200th-gromor-store-launch-in-coorg/"), ("Coromandel FY25 integrated annual report", "https://www.coromandel.biz/wp-content/uploads/2025/07/Integrated-Annual-Report-2024-25.pdf"), ("Coromandel retail", "https://www.coromandel.biz/retail/"), ("Gromor Drive", "https://www.coromandel.biz/gromor-drive/")],
        "what_i_have": "Store master, dealer/distributor master, farmer panel, product sales, credit ageing, soil tests, drone service logs, demo plots and field activities.",
        "limitations": "Store brands vary by state, farmer IDs are not always stable, crop names and villages are inconsistent, and service files do not share one clean customer key.",
        "step_public_scale": "The public South Gromor store counts anchor the retail footprint; dealer/distributor counts anchor the channel file.",
        "step_boundary": "The manager sees retail-store, dealer, farmer, advisory, soil-test and drone service evidence.",
        "step_files": "Files cover input purchase behavior, credit, agronomy engagement, service usage, demo conversion and field actions.",
    }
    dicts = {
        "transactions.csv": [("customer_id", "dealer or farmer key"), ("secondary_customer_id", "store link for farmer sales"), ("category", "input category"), ("free_text_note", "crop/payment note")],
        "soil_tests.csv": [("npk_status", "soil result"), ("followup_purchase_seen", "post-advisory purchase flag")],
        "drone_sprays.csv": [("service_status", "service completion state"), ("operator_id", "drone operator key")],
        "demo_plots.csv": [("stage", "demo lifecycle"), ("result_note", "unstructured result")],
    }
    write_company_docs(d, meta, files, dicts)
    return {"company": "Coromandel International", "folder": "Coromandel_International", "basis": "1,151 South Gromor stores; 13,060 dealers/distributors", "main_file": "transactions.csv"}


def main():
    for child in ROOT.iterdir():
        if child.is_dir() and child.name in ["Pidilite_Industries", "Asian_Paints", "CEAT", "Coromandel_International"]:
            shutil.rmtree(child)
    summaries = [pidilite(), asian_paints(), ceat(), coromandel()]
    write_root_readme(summaries)
    print("Generated evaluation datasets in", ROOT)


if __name__ == "__main__":
    main()
