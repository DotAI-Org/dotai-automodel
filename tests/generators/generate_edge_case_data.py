import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def make_empty_df():
    """Header only, 0 rows."""
    return pd.DataFrame(columns=[
        "customer_id", "transaction_date", "amount", "product",
        "quantity", "category", "channel", "region",
    ])


def make_single_customer(n_txns=5):
    """1 customer with n_txns transactions."""
    base = datetime(2024, 1, 1)
    rows = []
    for i in range(n_txns):
        rows.append({
            "customer_id": "CUST_001",
            "transaction_date": (base + timedelta(days=i * 10)).strftime("%Y-%m-%d"),
            "amount": 50 + i * 10,
            "product": f"P{i % 3}",
            "quantity": i + 1,
            "category": "CatA",
            "channel": "online",
            "region": "North",
        })
    return pd.DataFrame(rows)


def make_all_churned(n=50):
    """All customers stop buying after midpoint."""
    np.random.seed(42)
    rows = []
    base = datetime(2024, 1, 1)
    for i in range(n):
        cid = f"C{i:03d}"
        # Only transactions in first 60 days
        n_txns = np.random.randint(2, 6)
        for j in range(n_txns):
            day_offset = np.random.randint(0, 60)
            rows.append({
                "customer_id": cid,
                "transaction_date": (base + timedelta(days=day_offset)).strftime("%Y-%m-%d"),
                "amount": np.random.randint(10, 200),
                "product": f"P{j % 5}",
                "quantity": 1,
                "category": "CatA",
                "channel": "online",
                "region": "North",
            })
    # Add a single anchor transaction at the end so max_date is far out
    rows.append({
        "customer_id": "ANCHOR",
        "transaction_date": (base + timedelta(days=365)).strftime("%Y-%m-%d"),
        "amount": 10,
        "product": "P0",
        "quantity": 1,
        "category": "CatA",
        "channel": "online",
        "region": "North",
    })
    return pd.DataFrame(rows)


def make_all_active(n=50):
    """All customers keep buying throughout the period."""
    np.random.seed(42)
    rows = []
    base = datetime(2024, 1, 1)
    for i in range(n):
        cid = f"C{i:03d}"
        # Transactions spread across the full year
        for month in range(1, 13):
            rows.append({
                "customer_id": cid,
                "transaction_date": datetime(2024, month, 15).strftime("%Y-%m-%d"),
                "amount": np.random.randint(10, 200),
                "product": f"P{month % 5}",
                "quantity": 1,
                "category": "CatA",
                "channel": "online",
                "region": "North",
            })
    return pd.DataFrame(rows)


def make_single_day(n=20):
    """All transactions on the same date."""
    rows = []
    for i in range(n):
        rows.append({
            "customer_id": f"C{i:03d}",
            "transaction_date": "2024-06-15",
            "amount": 100 + i,
            "product": f"P{i % 4}",
            "quantity": 1,
            "category": "CatA",
            "channel": "online",
            "region": "North",
        })
    return pd.DataFrame(rows)


def make_negative_amounts(n=20):
    """Includes refund rows with negative amounts."""
    np.random.seed(42)
    rows = []
    base = datetime(2024, 1, 1)
    for i in range(n):
        cid = f"C{i % 5:03d}"
        amount = np.random.choice([50, 100, -30, -50, 200])
        rows.append({
            "customer_id": cid,
            "transaction_date": (base + timedelta(days=i * 5)).strftime("%Y-%m-%d"),
            "amount": int(amount),
            "product": f"P{i % 3}",
            "quantity": 1,
            "category": "CatA",
            "channel": "online",
            "region": "North",
        })
    return pd.DataFrame(rows)


def make_wide_csv(n_cols=50):
    """Many columns, only 3 meaningful."""
    np.random.seed(42)
    n_rows = 100
    base = datetime(2024, 1, 1)
    data = {
        "customer_id": [f"C{i % 10:03d}" for i in range(n_rows)],
        "transaction_date": [(base + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(n_rows)],
        "amount": np.random.randint(10, 500, n_rows).tolist(),
    }
    for i in range(n_cols - 3):
        data[f"extra_col_{i}"] = np.random.randn(n_rows).tolist()
    return pd.DataFrame(data)
