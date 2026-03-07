"""Generate synthetic data for maturity-based churn testing."""

import random
import csv
from datetime import datetime, timedelta

def generate_maturity_churn_csv(filepath: str, n_healthy: int = 100, n_churn: int = 100):
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 12, 31)
    
    rows = []
    
    # Cohort 1: Healthy (Frequent, long-term)
    for i in range(1, n_healthy + 1):
        cust_id = f"HEALTHY_{i:03d}"
        n_txns = random.randint(10, 20)
        for _ in range(n_txns):
            days_offset = random.randint(0, 360)
            txn_date = start_date + timedelta(days=days_offset)
            rows.append({
                "customer_id": cust_id,
                "transaction_date": txn_date.strftime("%Y-%m-%d"),
                "amount": round(random.uniform(20.0, 100.0), 2),
                "product": "Pro Plan"
            })

    # Cohort 2: Churn (Exactly 3 txns, then stop)
    for i in range(1, n_churn + 1):
        cust_id = f"CHURN_{i:03d}"
        # Start at various times in the first half of the year
        cohort_start = start_date + timedelta(days=random.randint(0, 180))
        for j in range(3):
            # Spaced 1 week apart
            txn_date = cohort_start + timedelta(weeks=j)
            rows.append({
                "customer_id": cust_id,
                "transaction_date": txn_date.strftime("%Y-%m-%d"),
                "amount": round(random.uniform(20.0, 100.0), 2),
                "product": "Basic Plan"
            })

    # Sort by date
    rows.sort(key=lambda r: r["transaction_date"])

    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["customer_id", "transaction_date", "amount", "product"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} transactions for {n_healthy + n_churn} customers at {filepath}")

if __name__ == "__main__":
    import os
    os.makedirs("tests/test_data", exist_ok=True)
    generate_maturity_churn_csv("tests/test_data/maturity_churn.csv")
