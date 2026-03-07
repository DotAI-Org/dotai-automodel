"""Generate a sample e-commerce transaction CSV for testing."""

import random
import csv
from datetime import datetime, timedelta


def generate_ecommerce_csv(filepath: str, n_customers: int = 200, n_transactions: int = 5000):
    categories = ["Electronics", "Clothing", "Home & Garden", "Books", "Sports"]
    products = {
        "Electronics": ["Laptop", "Phone", "Headphones", "Tablet", "Charger"],
        "Clothing": ["T-Shirt", "Jeans", "Jacket", "Shoes", "Hat"],
        "Home & Garden": ["Lamp", "Rug", "Plant Pot", "Cushion", "Candle"],
        "Books": ["Novel", "Cookbook", "Textbook", "Comic", "Magazine"],
        "Sports": ["Yoga Mat", "Dumbbell", "Water Bottle", "Shoes", "Band"],
    }
    channels = ["Online", "Store", "Mobile App"]
    regions = ["North", "South", "East", "West"]

    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range = (end_date - start_date).days

    customer_ids = [f"CUST_{i:04d}" for i in range(1, n_customers + 1)]

    # Some customers are "churned" - stop buying after mid-2024
    churn_cutoff = datetime(2024, 7, 1)
    churned_customers = set(random.sample(customer_ids, int(n_customers * 0.3)))

    random.seed(42)
    rows = []

    for _ in range(n_transactions):
        cust = random.choice(customer_ids)
        cat = random.choice(categories)
        prod = random.choice(products[cat])
        channel = random.choice(channels)
        region = random.choice(regions)
        qty = random.randint(1, 5)
        amount = round(random.uniform(5.0, 500.0) * qty, 2)

        if cust in churned_customers:
            # Churned customers only transact before cutoff
            max_days = (churn_cutoff - start_date).days
            txn_date = start_date + timedelta(days=random.randint(0, max_days))
        else:
            txn_date = start_date + timedelta(days=random.randint(0, date_range))

        rows.append({
            "customer_id": cust,
            "transaction_date": txn_date.strftime("%Y-%m-%d"),
            "amount": amount,
            "product": prod,
            "quantity": qty,
            "category": cat,
            "channel": channel,
            "region": region,
        })

    # Sort by date
    rows.sort(key=lambda r: r["transaction_date"])

    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "customer_id", "transaction_date", "amount",
            "product", "quantity", "category", "channel", "region",
        ])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} transactions for {n_customers} customers at {filepath}")


if __name__ == "__main__":
    generate_ecommerce_csv("tests/test_data/ecommerce_sample.csv")
