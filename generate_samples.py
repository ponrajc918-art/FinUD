"""
Generate sample CSV datasets for testing FinAI Dashboard.
Run: python generate_samples.py
"""
import pandas as pd
import numpy as np
import random

np.random.seed(42)
random.seed(42)
N = 100

# ── Loan Dataset ──────────────────────────────────────────────
loans = pd.DataFrame({
    'loan_id': [f'L{1000+i}' for i in range(N)],
    'age': np.random.randint(22, 65, N),
    'income': np.random.choice(
        np.concatenate([np.random.normal(55000, 20000, 95), [250000, 320000, 410000, 5000, 1000]]), N
    ).clip(0).astype(int),
    'loan_amount': np.random.randint(10000, 500000, N),
    'credit_score': np.random.randint(580, 800, N),
    'employment_years': np.random.randint(0, 20, N),
    'dependents': np.random.randint(0, 5, N),
    'loan_status': np.random.choice(['Approved','Rejected'], N, p=[0.6,0.4])
})
# Add a few duplicates
loans = pd.concat([loans, loans.iloc[[5,10,15]]], ignore_index=True)
loans.to_csv('sample_loan.csv', index=False)
print(f"✅ sample_loan.csv — {len(loans)} rows")

# ── Staff Dataset ─────────────────────────────────────────────
names = ['Alice Johnson','Bob Smith','Carol White','David Brown','Emma Davis',
         'Frank Wilson','Grace Lee','Henry Taylor','Iris Martinez','Jack Anderson',
         'Kate Thomas','Liam Jackson','Mia Harris','Noah Martin','Olivia Garcia',
         'Paul Robinson','Quinn Lewis','Rachel Walker','Sam Hall','Tina Young']
staff = pd.DataFrame({
    'staff_id': [f'S{200+i}' for i in range(20)],
    'name': names,
    'department': np.random.choice(['Sales','Loans','Investments','Customer Service'], 20),
    'target': np.random.randint(80000, 200000, 20),
    'achieved': np.random.randint(40000, 220000, 20),
    'quarter': np.random.choice(['Q1 2024','Q2 2024','Q3 2024','Q4 2024'], 20)
})
staff.to_csv('sample_staff.csv', index=False)
print(f"✅ sample_staff.csv — {len(staff)} rows")

# ── Customer Dataset ──────────────────────────────────────────
customers = pd.DataFrame({
    'customer_id': [f'C{3000+i}' for i in range(N)],
    'age': np.random.randint(20, 70, N),
    'income': np.random.choice(
        np.concatenate([np.random.normal(60000, 25000, 97), [500000, 800000, 1200000]]), N
    ).clip(0).astype(int),
    'balance': np.random.normal(25000, 40000, N).clip(0).astype(int),
    'risk_appetite': np.random.choice(['Low','Medium','High'], N, p=[0.3,0.5,0.2]),
    'occupation': np.random.choice(['Engineer','Doctor','Teacher','Business Owner','Manager','Retired','Student'], N),
    'years_with_bank': np.random.randint(1, 25, N)
})
# Add duplicate
customers = pd.concat([customers, customers.iloc[[2,7]], pd.DataFrame({
    'customer_id':['C9997'],'age':[35],'income':[9999999],'balance':[0],
    'risk_appetite':['High'],'occupation':['Unknown'],'years_with_bank':[0]
})], ignore_index=True)
customers.to_csv('sample_customer.csv', index=False)
print(f"✅ sample_customer.csv — {len(customers)} rows")
print("\n📁 Files ready: sample_loan.csv, sample_staff.csv, sample_customer.csv")
