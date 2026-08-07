"""Summarise the quarterly revenue data."""
import pandas as pd

df = pd.read_csv("quarterly_revenue.csv")
df["margin"] = (df.revenue - df.cost) / df.revenue * 100

print(df.to_string(index=False))
print()
print(f"total revenue   {df.revenue.sum():.2f}M")
print(f"average margin  {df.margin.mean():.1f}%")
print(f"best quarter    {df.loc[df.revenue.idxmax(), 'quarter']}")
