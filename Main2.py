import pandas as pd
import numpy as np
import math
from collections import Counter
import matplotlib.pyplot as plt

# ===== LOAD YOUR DATA =====
# Excel must have columns: amount, supplier, invoice_no, date, description (rename as needed)
df = pd.read_excel("tenders.xlsx")
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
df = df[df['amount'] > 0].copy()

print(f"Loaded {len(df)} transactions")

# ===== HELPER: first digit =====
def first_digit(n): 
    n = int(abs(n))
    while n >= 10: n //= 10
    return n

def second_digit(n):
    n = int(abs(n))
    s = str(n)
    return int(s[1]) if len(s) > 1 else 0

df['first'] = df['amount'].apply(first_digit)
df['second'] = df['amount'].apply(second_digit)
df['last2'] = df['amount'].astype(int).astype(str).str[-2:]

# ===== 1. BENFORD 1ST DIGIT =====
print("\n--- 1. BENFORD 1ST DIGIT ---")
exp1 = {d: math.log10(1+1/d)*100 for d in range(1,10)}
obs1 = df['first'].value_counts(normalize=True).sort_index()*100
for d in range(1,10):
    print(f"{d}: Observed {obs1.get(d,0):.1f}% vs Expected {exp1[d]:.1f}%")

# ===== 2. BENFORD 2ND DIGIT =====
print("\n--- 2. BENFORD 2ND DIGIT (catches smart thieves) ---")
# Expected 2nd digit formula
exp2 = {}
for d in range(10):
    s = sum(math.log10(1+1/(10*k+d)) for k in range(1,10))
    exp2[d] = s*100
obs2 = df['second'].value_counts(normalize=True).sort_index()*100
for d in range(10):
    print(f"{d}: Observed {obs2.get(d,0):.1f}% vs Expected {exp2[d]:.1f}%")

# ===== 3. LAST TWO DIGITS (round number fraud) =====
print("\n--- 3. LAST TWO DIGITS ---")
last2_counts = df['last2'].value_counts().head(10)
print("Top 10 last2 digits (if 00,50,99 dominate = fraud):")
print(last2_counts)
round_pct = (df['amount'] % 1000 == 0).mean()*100 + (df['amount'] % 100 == 0).mean()*100
print(f"Round number % (amount ending 00): {(df['amount'] % 100 == 0).mean()*100:.1f}% — >20% is red flag")

# ===== 4. FIRST-TWO DIGITS (49,999 trick) =====
print("\n--- 4. FIRST-TWO DIGITS (approval limit dodging) ---")
df['first2'] = df['amount'].astype(int).astype(str).str[:2].astype(int)
top_first2 = df['first2'].value_counts().head(10)
print(top_first2)
print("If you see 49, 99, 24, 49 as top — they are dodging 50k/100k limits")

# ===== 5. PARETO - SUPPLIER CONCENTRATION =====
print("\n--- 5. PARETO - WHO EATS ALL MONEY? ---")
supplier_sum = df.groupby('supplier')['amount'].sum().sort_values(ascending=False)
top2_pct = supplier_sum.head(2).sum() / supplier_sum.sum() * 100
print(f"Top 2 suppliers take {top2_pct:.1f}% of all money. >50% = cartel")
print(supplier_sum.head(5))

# ===== 6. RSF - BIGGEST OUTLIER =====
print("\n--- 6. RSF - LARGEST TRANSACTION CHECK ---")
sorted_amounts = df['amount'].sort_values(ascending=False).values
