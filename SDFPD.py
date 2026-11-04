# %% 1: Getting Data
from mailbox import linesep
from operator import contains
from turtle import color

import pandas as pd

df = pd.read_csv("./Data/raw/ISB_areas.csv")
df.head()
# %% 2: Data Shape
print(df.shape)
print(df.columns)
# %% 3: Checking Null Values
df.isnull().sum()
# %% 4: Fixing Null Values with (Mean)
df["beds"] = df["beds"].fillna(df["beds"].mean())
df["baths"] = df["baths"].fillna(df["baths"].mean())

df.isnull().sum()
# %% 5: new
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

# %% Data Updated - (After Price in one cal)

df.head()
# %% 9: Area Fixing

area_values = {"marla": 1, "kanal":20}

def area_cal(text):
    area_matches = re.findall(r"(\d\.?\d*)\s*(marla|kanal)", str(text).lower())
    return sum(float(count) * area_values[area] for count, area in area_matches)

df["Area (Marla)"] = df["area"].apply(area_cal)

# %% Data Updated - (After Area in one cal)

df.tail()
