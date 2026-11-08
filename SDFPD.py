# %% 1: Getting Data
from enum import unique

from requests.compat import numeric_types

import pandas as pd

df = pd.read_csv("./Data/raw/ISB_areas.csv")
df.head()
# %% 2: Data Shape
print(df.shape)
print(df.columns)
# %% 3: Checking Null Values
print("Null Values:",df.isnull().sum())
print("-"*30)
print("Duplicates: ",df.duplicated().sum())
# %% 4: Fixing Null Values with (Mean)
df["beds"] = df["beds"].fillna(df["beds"].median())
df["baths"] = df["baths"].fillna(df["baths"].median())

df.isnull().sum()
# %% 5: Duplicates Dropped
df = df.drop_duplicates()
df.dtypes
df.head()
# %% 6: Unique

print(df["area"].unique())
print(df["price"].unique())
# %% 7: Total Stuff
print(df["price"].str.findall(r"[a-zA-Z]+").explode().value_counts())
print("-" * 30)
print(df["area"].str.findall(r"[a-zA-Z]+").explode().value_counts())
# %% 8: Price Fixing
import re
price_values = {"lakh": 1, "crore": 100, "arab": 10000}

def price_cal(text):
    matches = re.findall(r"(\d+\.?\d*)\s*(crore|lakh|arab)", str(text).lower())
    return sum(float(count) * price_values[price] for count, price in matches)

df["Price (Lakh)"] = df["price"].apply(price_cal)

# %% 9: Data Updated - (After Price in one cal)

df.head()
# %% 10: Area Fixing

area_values = {"marla": 1, "kanal":20}

def area_cal(text):
    area_matches = re.findall(r"(\d+\.?\d*)\s*(marla|kanal)", str(text).lower())
    return sum(float(count) * area_values[area] for count, area in area_matches)

df["Area (Marla)"] = df["area"].apply(area_cal)

# %% 11: Data Updated - (After Area in one cal)

df.tail()
# %% 12: Checking 0 Values

print((df["Area (Marla)"] == 0). sum())
print((df["Price (Lakh)"] == 0). sum())

# %% 13:
df[df["Area (Marla)"] == 0][["area", "price", "location"]]
bad = [16881, 16582, 13622, 4374, 4780]
df = df[df["Area (Marla)"] > 0].drop(index=bad)
# %%
print(df[["Price (Lakh)", "Area (Marla)", "beds", "baths"]].describe())
# %%

df["ppm"] = df["Price (Lakh)"] / df["Area (Marla)"]

print(df["ppm"].describe())

cols = ["location", "area", "beds", "price", "ppm"]
print("-" * 50)
print("Head")
print(df.sort_values("ppm").head(10)[cols])
print("-" * 50)
print("Tail")
print(df.sort_values("ppm").tail(10)[cols])
print("-" * 50)
print("Quantile")
print(df["ppm"].quantile([0.01, 0.05, 0.95,0.99]))
# %%

df = df.drop(columns="ppm").reset_index(drop=True)
df.to_csv("./Data/processed/ISB_clean.csv", index=False, encoding="utf-8")
print(df.shape)

# %% 14: Histogram Plot
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(7,4))
sns.histplot(data=df, x="Price (Lakh)", kde=True, bins=50)
plt.title("Price (Lakh) Distribution")
plt.show()

# %% 14: Scatter Plot

plt.figure(figsize=(7,4))
sns.scatterplot(data=df, x="Area (Marla)", y="Price (Lakh)", s=15, alpha=.3)
plt.title("Area vs Price")
plt.show()
# %% 14: Box Plot

plt.figure(figsize=(7,4))
sns.boxenplot(data=df, x="beds", y="Price (Lakh)", palette='Set2')
plt.title("Beds vs Baths")
plt.show()
# %% 15: Bar Plot

plt.figure(figsize=(12,6))
sns.barplot(data=df, x="Area (Marla)", y="Price (Lakh)", errorbar=None, color="teal")
plt.title("Bar Plot")
plt.show()
# %% 16: Heatmap

plt.figure(figsize=(7,4))
corr_matrix = df[['Price (Lakh)','Area (Marla)','beds','baths']].corr()
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1, linewidths=0.5)
plt.title("Numerical Feature Correlations")

# %% 17: New Histogram using Numpy
import numpy as np
new = np.log1p(df["Price (Lakh)"])
plt.figure(figsize=(7,4))
sns.histplot(new)
plt.xlabel("Log")
# %%
df['ppm'] = df['Price (Lakh)'] / df['Area (Marla)']
df.head()
# %%
cleaned_df = df.groupby('location', as_index=False).agg(
    Median_Price = ('ppm','median'),
    Max_Price = ('ppm','max'),
    Mean_Price = ('ppm','mean'),
    Min_Price = ('ppm','min'),
    loc_count = ('location','count')
)

# %%
cleaned_df = cleaned_df[cleaned_df['loc_count'] >= 50]
cleaned_df = cleaned_df.sort_values(by='Median_Price', ascending=False)
print(cleaned_df.shape)
cleaned_df.head(15)

# %%
plt.figure(figsize=(12,10))
sns.barplot(data=cleaned_df, x='Median_Price', y='location')
plt.title('BarPlot')
plt.show()
# %%
plt.figure(figsize=(8,6))
sns.barplot(data=df, y='Price (Lakh)', x='beds')
plt.title('Price x Beds')
plt.show()
