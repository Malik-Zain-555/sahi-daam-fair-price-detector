# %% 1: Getting Data
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
