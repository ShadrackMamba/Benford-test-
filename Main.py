import pandas as pd
import math
from collections import Counter
import matplotlib.pyplot as plt

# 1. Load your data — put amount column name here
df = pd.read_excel("tenders.xlsx") # or .csv
amounts = df['amount']  # change to your column

# 2. Get first digit of each amount
def first_digit(n):
    n = abs(int(n))
    while n >= 10:
        n //= 10
    return n

first_digits = [first_digit(x) for x in amounts if x > 0]

# 3. Count what you found
counted = Counter(first_digits)
total = len(first_digits)
observed = {d: counted.get(d,0)/total*100 for d in range(1,10)}

# 4. What Benford expects
expected = {d: math.log10(1 + 1/d)*100 for d in range(1,10)}

# 5. Print
for d in range(1,10):
    print(f"{d}: You found {observed[d]:.1f}% | Benford expects {expected[d]:.1f}%")

# 6. Plot — fraud pops out visually
plt.bar(expected.keys(), expected.values(), alpha=0.6, label="Expected (Benford)")
plt.bar(observed.keys(), observed.values(), alpha=0.6, label="Observed (Your data)")
plt.legend()
plt.title("Benford Test - Fake invoices = big gap on 8,9")
plt.savefig("benford.png")
