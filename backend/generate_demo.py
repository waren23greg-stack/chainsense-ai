import pandas as pd, numpy as np, os, random
from datetime import datetime, timedelta

random.seed(42); np.random.seed(42)
SUPPLIERS  = ["Nairobi Supplies Ltd","East Africa Logistics","Kenya Procurement Co","Mombasa Trading Co","Kampala Wholesale","Dar es Salaam Imports","Global Freight KE","Pan-Africa Distributors","Rift Valley Suppliers","Lake Region Trading"]
PRODUCTS   = ["Industrial Bearings","Safety Equipment","Packaging Material","Electronic Components","Raw Cotton","Steel Rods","Chemical Compounds","Medical Supplies","Office Supplies","Machinery Parts"]
CARRIERS   = ["DHL","FedEx","Kenya Airways Cargo","Siginon Logistics","G4S Logistics"]
WAREHOUSES = ["Nairobi","Mombasa","Kisumu","Eldoret"]
COUNTRIES  = ["Kenya","Uganda","Tanzania","Ethiopia","Rwanda"]
STATUSES   = ["Delivered"]*48 + ["Shipped"]*16 + ["Processing"]*19 + ["Cancelled"]*17
N          = 500; START = datetime(2024, 1, 1)

qty   = np.random.randint(10, 500, N)
price = np.round(np.random.uniform(5, 250, N), 2)
df    = pd.DataFrame({
    "order_id":      [f"ORD-{1000+i}" for i in range(N)],
    "order_date":    [(START+timedelta(days=random.randint(0,450))).strftime("%Y-%m-%d") for _ in range(N)],
    "supplier_name": [random.choice(SUPPLIERS) for _ in range(N)],
    "product_name":  [random.choice(PRODUCTS)  for _ in range(N)],
    "carrier":       [random.choice(CARRIERS)  for _ in range(N)],
    "warehouse":     [random.choice(WAREHOUSES) for _ in range(N)],
    "country":       [random.choice(COUNTRIES)  for _ in range(N)],
    "quantity":      qty, "unit_price": price,
    "status":        [random.choice(STATUSES) for _ in range(N)],
    "delay_days":    np.maximum(0, np.random.normal(5,6,N).astype(int)),
    "stock_level":   np.random.randint(0,1000,N),
    "reorder_point": np.random.randint(50,200,N),
})
df["revenue"] = (df["quantity"] * df["unit_price"]).round(2)
df["total_amount"] = df["revenue"]
df["order_date"] = pd.to_datetime(df["order_date"])
df = df.sort_values("order_date").reset_index(drop=True)

out = os.path.join(os.path.dirname(__file__), "..", "data", "demo.csv")
os.makedirs(os.path.dirname(out), exist_ok=True)
df.to_csv(out, index=False)
print(f"Generated {len(df)} rows → {os.path.abspath(out)}")
print(f"Revenue: ${df['revenue'].sum():,.2f} | Cancelled: {(df['status']=='Cancelled').mean()*100:.1f}%")
