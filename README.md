# Sahi Daam: Fair Price Detector 🏠

> **"Sahi Daam"** (Urdu/Hindi for *the right price*): a machine learning project that learns what houses in Islamabad should cost, so a buyer can tell if a listing is **fairly priced, overpriced or a good deal**.

**Status:** Phase 1 Data Collection ✅ · Phase 2 Data Cleaning ✅ · Phase 3 EDA ✅ · Phase 4 Feature Engineering ⏳ next

---

## Table of Contents

1. [Project Goal](#1-project-goal)
2. [Quick Summary of What Is Done](#2-quick-summary-of-what-is-done)
3. [Tech Stack](#3-tech-stack)
4. [Repository Structure](#4-repository-structure)
5. [Glossary: Pakistani Property Units](#5-glossary-pakistani-property-units)
6. [Phase 0: Learning Web Scraping](#6-phase-0-learning-web-scraping)
7. [Phase 1: Data Collection](#7-phase-1-data-collection-web-scraping)
8. [Phase 2: Data Cleaning](#8-phase-2-data-cleaning)
9. [Final Cleaned Dataset](#9-final-cleaned-dataset)
10. [Phase 3: Exploratory Data Analysis (EDA)](#10-phase-3-exploratory-data-analysis-eda)
11. [EDA Findings in One Place](#11-eda-findings-in-one-place)
12. [Mistakes I Made and Fixed](#12-mistakes-i-made-and-fixed)
13. [Limitations](#13-limitations)
14. [Next Steps and Roadmap](#14-next-steps-and-roadmap)
15. [How to Run](#15-how-to-run)
16. [Ethics and Responsible Scraping](#16-ethics-and-responsible-scraping)

---

## 1. Project Goal

Property prices in Pakistan are hard to judge. The same 1 Kanal house can be listed at very different prices, and a buyer usually has no quick way to know whether the asking price is reasonable.

**The goal of this project is to:**

1. Collect real listing data for houses for sale in **Islamabad** from zameen.com.
2. Clean it into a reliable dataset.
3. Explore it to understand what drives price.
4. Train a model that predicts the **fair sale price** from a house's location, area (size), bedrooms and bathrooms.
5. Compare any listing's asking price with the model's predicted price and flag it as **overpriced / fair / underpriced**.

**Scope decisions made so far:**

| Decision | Choice | Why |
|---|---|---|
| Rent or sale? | **Sale** | Sale price is the more meaningful "fair price" question. The very first practice scrape was on rentals, but the project itself targets sale. |
| Which city? | **Islamabad only (for now)** | Build the whole pipeline on one city first, then repeat for Rawalpindi. |
| Data source | **zameen.com** | Largest property portal in Pakistan, with listing cards available in plain HTML. |

---

## 2. Quick Summary of What Is Done

| Step | What | Result |
|---|---|---|
| 0 | Learned web scraping with `requests` + `BeautifulSoup` | Practice scripts in `Data/raw/` and `Scrapping Learning/` |
| 1 | Collected the list of all Islamabad areas (societies, sectors, blocks) | **501** area links |
| 2 | Built a paginated scraper for listing cards | **~17,000** raw listings |
| 3 | Cleaned the data: nulls, units, duplicates, outliers | **~8,400** clean listings |
| 4 | Saved the processed dataset | `Data/processed/ISB_clean.csv` |
| 5 | Exploratory Data Analysis (histograms, scatter, heatmap, bar plots) | Findings in [Section 11](#11-eda-findings-in-one-place) |

---

## 3. Tech Stack

| Tool | Used for |
|---|---|
| Python 3.12 | Main language |
| `requests` | Downloading web pages |
| `BeautifulSoup4` (`bs4`) | Reading the HTML and picking out data using CSS selectors |
| `pandas` | Tables (DataFrames), cleaning, grouping, saving CSV |
| `numpy` | Log transform of price |
| `matplotlib` + `seaborn` | Visualisation (EDA) |
| `re` (regex) | Pulling numbers and units out of text like `"1.5 Crore"` |
| Zed editor | Coding (with `# %%` cell markers, which work like notebook cells) |
| Git / GitHub | Version control |

---

## 4. Repository Structure

> Update this tree if your folders differ.

```
sahi-daam-fair-price-detector/
│
├── Data/
│   ├── raw/                  # Untouched scraped data + scraping scripts
│   │   ├── data.py           # First practice scraper
│   │   ├── data.csv          # Output of the practice scraper
│   │   ├── main.py           # Main scraper (areas -> listing cards)
│   │   └── ISB_areas.csv     # Raw scraped Islamabad listings
│   └── processed/
│       └── ISB_clean.csv     # Cleaned dataset (output of cleaning)
│
├── Scrapping Learning/       # Practice files while learning scraping
│
├── SDFPD.py                  # Cleaning + EDA script (cell-based, # %%)
└── README.md
```

**Rule I follow:** raw data is never edited by hand. All changes happen in code, and the result goes into `processed/`.

---

## 5. Glossary: Pakistani Property Units

Listings use local units, and a model cannot understand text like `"1.5 Crore"`, so everything is converted to **one number in one unit**.

**Price units → converted to Lakh**

| Unit | Meaning | In Lakh |
|---|---|---|
| 1 Lakh | 100,000 PKR | 1 |
| 1 Crore | 100 Lakh = 10,000,000 PKR | 100 |
| 1 Arab | 100 Crore = 10,000,000,000 PKR | 10,000 |

**Area units → converted to Marla**

| Unit | In Marla |
|---|---|
| 1 Marla | 1 (about 225 sq ft) |
| 1 Kanal | 20 Marla |

Compound values also exist, for example `"1 Kanal 5 Marla"` = 25 Marla and `"1 Arab 20 Crore"` = 12,000 Lakh. The cleaning code handles these.

---

## 6. Phase 0: Learning Web Scraping

Before starting the real project I learned scraping on a small task: the **rental** listings page for DHA Phase 2 (`Data/raw/data.py`).

What that practice covered:

1. `requests.get(url)` downloads the page HTML.
2. `BeautifulSoup(html.text, "html.parser")` turns that HTML into a searchable object.
3. `soup.select("css selector")` finds all elements that match, for example every price.
4. Looping over the results and saving to CSV with pandas.

That first scrape only got 20 listings (title and price). It taught the basic skill, but also showed its limits: scraping `prices` and `areas` as separate lists is fragile (see [Section 12](#12-mistakes-i-made-and-fixed)).

---

## 7. Phase 1: Data Collection (Web Scraping)

### 7.1 How zameen.com URLs work

Every listing page looks like this:

```
https://www.zameen.com/Houses_Property/Islamabad_DHA_Defence_Phase_2-339-1.html
                                         └────────── area name ────────┘ │  └ page number
                                                                         └ area id
```

- The **area id** (`339`) is required. A made-up URL like `/Houses_Property/Faisalabad` does not work.
- The last number is the **page number**, so `...-339-1.html`, `...-339-2.html` and so on are consecutive pages.
- A city has its own id too (for example Islamabad is `3`).

### 7.2 Why the city dropdown did not work

The city/location dropdown on the zameen.com search bar is built by JavaScript **after** the page loads. `requests` only downloads the raw HTML, so selecting that dropdown returned empty `<div>` tags.

**Solution:** do not use the dropdown at all. Zameen has a plain HTML page that lists all locations of a city:

```
https://www.zameen.com/all_locations/Islamabad-3-1-9.html
```

### 7.3 Step A: Collect all area links

```python
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd

link = "https://www.zameen.com/all_locations/Islamabad-3-1-9.html"
html = requests.get(link, timeout=10)
soup = bs(html.text, "html.parser")

areas = soup.select("div.layout-grid_layoutGrid__htd53 span")
links = soup.select("div.layout-grid_layoutGrid__htd53 a")

clean_areas = [a.text.strip() for a in areas[:501]]
clean_links = [l.get("href", "").strip() for l in links[:501]]

df_areas = pd.DataFrame({"areas": clean_areas, "links": clean_links})
```

**Line by line:**

| Code | What it does |
|---|---|
| `requests.get(link, timeout=10)` | Downloads the page. `timeout` stops the script from hanging forever. |
| `bs(html.text, "html.parser")` | Parses the HTML text. |
| `soup.select("div.layout-grid_layoutGrid__htd53 span")` | Gets the area **names** inside the locations grid. |
| `soup.select("... a")` | Gets the area **links** (`<a href="...">`). |
| `[:501]` | The page has 501 real areas. Everything after that is footer text (address, phone number, "Add as preferred source"), which I cut off. |
| `.get("href", "")` | Reads the link. Returns an empty string if missing. |
| `.strip()` | Removes extra spaces and line breaks. |

**Result:** 501 areas with their full URLs, for example DHA Defence Phase 2, Bani Gala, G-13, B-17, F-7 and so on.

> ⚠️ A few links start with `Taxila_` or `Rawalpindi_` (such as Faisal Hills and Model Town Humak) even though they appear on the Islamabad page. They are kept for now and flagged for review.

### 7.4 Step B: Scrape listing cards of one area

On a listing page, each house is a **card** (an `li` inside a `ul`). Inside each card, Zameen puts accessibility labels (`aria-label`) on the important values:

| `aria-label` | Value |
|---|---|
| `Price` | e.g. `1.5 Crore` |
| `Location` | e.g. `DHA Defence Phase 2, DHA Defence` |
| `Beds` | e.g. `5` |
| `Baths` | e.g. `6` |
| `Area` | e.g. `1 Kanal` |

**Why `aria-label` and not CSS classes?** Class names like `_6d9b9b83` or `dc381b54` are auto-generated and can change whenever Zameen updates its site. The `aria-label` text is meant for accessibility, so it is far more stable.

### 7.5 Step C: The scraper function

```python
import time

combined_rows = []

def area_scrapper(area_name, area_url):
    base = area_url[:-len("-1.html")]          # ".../Islamabad_Bani_Gala-340"
    page_no = 1

    while True:
        r = requests.get(f"{base}-{page_no}.html", timeout=10)
        if r.status_code != 200:
            print(area_name, "status", r.status_code, "- skipping")
            break

        soup = bs(r.text, "html.parser")
        cards = soup.select("ul.e20beb46 li.a37d52f0")
        if not cards:
            break

        for hc in cards:
            def get(label):
                tag = hc.select_one(f'[aria-label="{label}"]')
                return tag.text.strip() if tag else "N/A"

            combined_rows.append({
                "area_name": area_name,
                "location": get("Location"),
                "area": get("Area"),
                "beds": get("Beds"),
                "baths": get("Baths"),
                "price": get("Price"),
            })

        if not soup.select_one('[title="Next"]'):
            break

        page_no += 1
        time.sleep(1)

    time.sleep(2)
```

**How it works, line by line:**

| Code | Purpose |
|---|---|
| `base = area_url[:-len("-1.html")]` | Cuts the `-1.html` off the end so the page number can be changed. |
| `while True` | Keeps going page by page until a stop condition is hit. |
| `r.status_code != 200` | If the site blocks me or the page is missing, stop and do not keep hammering it. |
| `cards = soup.select(...)` | All house cards on this page. |
| `if not cards: break` | An empty page means no more listings. |
| `get(label)` | A small helper. Finds the element with that `aria-label` inside the **current card**. Returns `"N/A"` if the card does not have it. |
| `combined_rows.append({...})` | Adds **one dictionary per house**, so each row always stays aligned. |
| `soup.select_one('[title="Next"]')` | If there is no "Next" button, this is the last page. |
| `time.sleep(1)` / `time.sleep(2)` | Polite delay between pages and between areas. |

### 7.6 Step D: Run over all areas

```python
areas_df = pd.read_csv("ISB_areas.csv")           # name + link of each area

for _, row in areas_df.iterrows():
    area_scrapper(row["areas"], row["links"])

df = pd.DataFrame(combined_rows)
df.to_csv("Data/raw/ISB_areas.csv", index=False, encoding="utf-8")
```

**Result:** around **17,000 raw listings** with columns `location, area, beds, baths, price` (plus the area name).

---

## 8. Phase 2: Data Cleaning

All cleaning lives in `SDFPD.py` as numbered cells (`# %% 1: Getting Data`, ...). The raw file is **read-only**: it is loaded, cleaned in memory, and saved as a new file.

### Step 1 to 3: Load and inspect

```python
df = pd.read_csv("./Data/raw/ISB_areas.csv")
df.head()
print(df.shape)
print(df.columns)
df.isnull().sum()
```

I always look first: how many rows, which columns, and how many values are missing.

### Step 4: Missing values in beds and baths

Some listings (plots, commercial, incomplete ads) have no beds/baths. Dropping them would waste data, so they are filled.

```python
df["beds"]  = df["beds"].fillna(df["beds"].mean())
df["baths"] = df["baths"].fillna(df["baths"].mean())
```

> **Known weakness:** mean-filling creates values like `5.136261` beds, which is not realistic. Better options: the **median/mode** (a whole number), or `0` for plots. Also, to avoid *data leakage*, the fill value should be calculated from the **training set only** after a train/test split. Both are on the to-do list ([Section 14](#14-next-steps-and-roadmap)).

### Step 5 to 7: Look at what the text really contains

```python
print(df["area"].unique())
print(df["price"].unique())

print(df["price"].str.findall(r"[a-zA-Z]+").explode().value_counts())
print(df["area"].str.findall(r"[a-zA-Z]+").explode().value_counts())
```

This step answers: *which units actually appear?* `findall(r"[a-zA-Z]+")` extracts every word, `.explode()` puts one word per row, and `.value_counts()` counts them. It confirmed the price units are **lakh, crore, arab** and the area units are **marla, kanal**, so the conversion dictionaries only need those.

### Step 8: Convert price to Lakh

```python
import re

price_values = {"lakh": 1, "crore": 100, "arab": 10000}

def price_cal(text):
    matches = re.findall(r"(\d+\.?\d*)\s*(crore|lakh|arab)", str(text).lower())
    return sum(float(count) * price_values[unit] for count, unit in matches)

df["Price (Lakh)"] = df["price"].apply(price_cal)
```

**The regex, piece by piece:**

| Part | Meaning |
|---|---|
| `\d+` | one or more digits (`14`) |
| `\.?` | an optional decimal point |
| `\d*` | more digits after the point (`.5`) |
| `\s*` | optional spaces |
| `(crore\|lakh\|arab)` | the unit word |

- `.lower()` makes `Crore` and `crore` the same.
- `findall` returns **all** matches, so `"1 Arab 20 Crore"` gives two pairs.
- `sum(...)` adds the pairs up: `1×10000 + 20×100 = 12000` Lakh.

| Original | Converted |
|---|---|
| `5.5 Crore` | 550 |
| `16 Crore` | 1600 |
| `5 Crore` | 500 |
| `1.5 Arab` | 15000 |

### Step 9: Convert area to Marla

```python
area_values = {"marla": 1, "kanal": 20}

def area_cal(text):
    area_matches = re.findall(r"(\d+\.?\d*)\s*(marla|kanal)", str(text).lower())
    return sum(float(count) * area_values[unit] for count, unit in area_matches)

df["Area (Marla)"] = df["area"].apply(area_cal)
```

| Original | Converted |
|---|---|
| `4 Marla` | 4 |
| `14 Marla` | 14 |
| `1 Kanal` | 20 |
| `2.6 Kanal` | 52 |
| `13.6 Marla` | 13.6 |

> 🐞 **Bug found here:** the first version used `\d` (one digit) instead of `\d+` (one or more). That turned `13.6 Marla` into `3.6` and `14 Marla` into `4`. Fixed with `\d+`. See [Section 12](#12-mistakes-i-made-and-fixed).

### Step 10: Check zero values

```python
print((df["Area (Marla)"] == 0).sum())
print((df["Price (Lakh)"] == 0).sum())
```

A `0` means the conversion failed. Results: **0 zero prices** and **4 zero areas**. The 4 rows were DHA Valley listings with `0 Marla` and prices of only 45 to 90 Lakh. These are junk entries, so they were dropped.

```python
df = df[df["Area (Marla)"] > 0]
```

### Step 11: Remove duplicates

```python
print("Duplicates: ", df.duplicated().sum())
df = df.drop_duplicates()
```

**8,503 duplicate rows** were found and removed. Likely cause: Zameen areas are nested (for example "DHA Defence Phase 2" also contains "DHA Phase 2 - Sector A"), so the same listing appeared under more than one area page.

> Because the data has no listing URL/ID, two truly different houses with identical details would also be treated as duplicates. Saving each listing's link in the next scrape fixes this.

### Step 12: Check outliers with price per Marla

`describe()` showed the price is heavily skewed (mean 1098 Lakh vs median 550 Lakh) and the maximum area was 1800 Marla. To find bad rows, I made a temporary column:

```python
df["ppm"] = df["Price (Lakh)"] / df["Area (Marla)"]     # price per Marla
print(df["ppm"].describe())
print(df.sort_values("ppm").head(10))
print(df.sort_values("ppm").tail(10))
```

**Why price per Marla?** A big plot is naturally expensive, so price alone does not show errors. Price per Marla puts every listing on the same scale. The median came out around **57.7 Lakh per Marla**, which is realistic for Islamabad.

**Rules used when deciding what to remove:**

| Case | Decision | Reason |
|---|---|---|
| 90 Kanal for 1.05 Crore (I-16) | ❌ Drop | Area typo |
| 1 Kanal for 19.5 Lakh (F-15) | ❌ Drop | Price typo |
| 12.5 Kanal for 6 Crore (Zaraj Scheme) | ❌ Drop | Impossible rate |
| 6 Kanal in an apartment tower (Askari Tower 1) | ❌ Drop | Wrong area for an apartment building |
| 3.6 Marla for 42 Crore (F-6/3) | ❌ Drop | Area typo (no such house in F-6) |
| 1.5 Arab for 2.6 Kanal in F-6 / G-6 / F-7 | ✅ Keep | Real. These are the most expensive sectors in the city. |
| Large Bhara Kahu / Sarai Kharbuza plots at a low rate | ✅ Keep | Real. Outskirts with big plots and low prices. |

**Key lesson:** I did *not* apply one global cut-off (like "drop everything above ppm 300"). That would have deleted real F-6 and F-7 houses. Every suspicious row was judged using its **location**.

**After cleaning:** median ppm ≈ 57.7, the 1st to 99th percentile range is about 17.5 to 200 Lakh per Marla, and about **8,408 rows** remained.

### Step 13: Drop the helper column and save

```python
df = df.drop(columns=["ppm"]).reset_index(drop=True)
df.to_csv("./Data/processed/ISB_clean.csv", index=False, encoding="utf-8")
print(df.shape)
```

> ⚠️ **`ppm` is removed on purpose.** It is calculated from the price, which is the thing the model must predict. Keeping it as a feature would leak the answer to the model (**data leakage**) and give fake, over-optimistic accuracy. (It is recreated temporarily during EDA, but never used as a model feature.)

---

## 9. Final Cleaned Dataset

**File:** `Data/processed/ISB_clean.csv`

| Column | Type | Description |
|---|---|---|
| `location` | text | Location text on the card, e.g. `DHA Defence Phase 2, DHA Defence` |
| `area` | text | Original area text, e.g. `1 Kanal` |
| `beds` | number | Bedrooms |
| `baths` | number | Bathrooms |
| `price` | text | Original price text, e.g. `1.5 Crore` |
| `Price (Lakh)` | number | **Target.** Price in Lakh PKR |
| `Area (Marla)` | number | Plot size in Marla |

**Quick facts (after cleaning):** about 8,400 listings · median price ≈ 550 Lakh · median ≈ 57.7 Lakh per Marla · beds 1 to 11 · baths 1 to 10 · price is right-skewed.

---

## 10. Phase 3: Exploratory Data Analysis (EDA)

**What is EDA?** Before building a model, I ask the data questions and answer them with charts. Each plot below answers one question. This phase uses `matplotlib` and `seaborn`, which I learned by building the plots myself and searching the docs when stuck.

```python
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
```

### 10.1 How is the price distributed? (histogram)

```python
plt.figure(figsize=(7, 4))
sns.histplot(data=df, x="Price (Lakh)", kde=True, bins=50)
plt.title("Price (Lakh) Distribution")
plt.show()
```

| Code | Meaning |
|---|---|
| `figsize=(7, 4)` | Size of the chart in inches (width, height) |
| `histplot` | Counts how many houses fall in each price range (bar = range) |
| `bins=50` | Splits the price range into 50 bars |
| `kde=True` | Adds a smooth line over the bars |

**What I saw:** most houses sit at the low end (the tallest bar is on the far left), while a few very expensive houses stretch the tail out to 35,000 Lakh. This is a **right-skewed** distribution. It is why the mean (≈1098 Lakh) is far above the median (≈550 Lakh).

### 10.2 Can the skew be fixed? (log transform)

```python
log_price = np.log1p(df["Price (Lakh)"])
plt.figure(figsize=(7, 4))
sns.histplot(log_price)
plt.show()
```

`np.log1p(x)` is `log(1 + x)`. It squeezes large values together so that a 350 Crore house does not dominate.

**What I saw:** the skew almost disappears and the shape becomes a bell. That is the shape most models learn best from. Two bumps are visible (around 6 and 7 on the log scale), which probably means **two separate markets** (smaller plots vs 1 Kanal+ houses).

> Note: the x-axis is now `log(price)`, not Lakh (6 ≈ 400 Lakh, 7 ≈ 1,100 Lakh, 8 ≈ 3,000 Lakh).
> **Decision:** the model will be trained on `log1p(Price (Lakh))` and predictions converted back with `np.expm1`.

### 10.3 Does a bigger plot cost more? (scatter plot)

```python
plt.figure(figsize=(7, 4))
sns.scatterplot(data=df, x="Area (Marla)", y="Price (Lakh)", s=15, alpha=0.3)
plt.title("Area vs Price")
plt.show()
```

(`s` = dot size, `alpha` = transparency, so crowded areas become visible.)

**What I saw:** price rises with area, but not as a straight line. The dots form a **fan shape**: for small plots the price range is narrow, for big plots it is huge (80 Marla houses range from about 1,500 to 35,000 Lakh). **Area alone cannot decide the price. Location matters a lot too.**
Three suspicious points (about 400, 280 and 140 Marla) are possible farmhouses or area typos, to be reviewed later.

### 10.4 Do beds and baths move together? (boxen plot)

```python
plt.figure(figsize=(7, 4))
sns.boxenplot(data=df, x="beds", y="baths")
plt.title("Beds vs Baths")
plt.show()
```

**What I saw:** as the number of beds goes up, baths go up too. The two columns carry similar information.

### 10.5 A plot that did not work (bar plot of Area vs Price)

I drew a bar for every unique area value. With hundreds of bars the x-axis labels overlapped and nothing could be read. **Lesson:** bar plots are for *categories* (like locations), not for continuous numbers. A scatter plot is the right tool for two numbers. This plot was dropped.

### 10.6 Which columns are related? (correlation heatmap)

```python
plt.figure(figsize=(7, 4))
corr = df[["Price (Lakh)", "Area (Marla)", "beds", "baths"]].corr()
sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1, linewidths=0.5)
plt.title("Numerical Feature Correlations")
plt.show()
```

How to read it: a number near **1** means "moves strongly together", near **0** means "no linear relation".

| Pair | Correlation | Meaning |
|---|---|---|
| Price ↔ Area | **0.76** | Strong. Area is the most important numeric feature. |
| Price ↔ Beds | 0.34 | Weak/moderate |
| Price ↔ Baths | 0.22 | Weak |
| Area ↔ Beds | 0.40 | Bigger houses have more beds |
| Area ↔ Baths | 0.28 | Slight |
| Beds ↔ Baths | **0.68** | Strongly related to each other |

### 10.7 Which locations are the most expensive? (groupby + bar plot)

First a temporary `ppm` (price per Marla) column is created (used for **exploration only**, never as a model feature):

```python
df["ppm"] = df["Price (Lakh)"] / df["Area (Marla)"]

loc_df = df.groupby("location", as_index=False).agg(
    Median_Price=("ppm", "median"),
    Max_Price=("ppm", "max"),
    Mean_Price=("ppm", "mean"),
    Min_Price=("ppm", "min"),
    loc_count=("location", "count"),
)

loc_df = loc_df[loc_df["loc_count"] >= 50]
loc_df = loc_df.sort_values(by="Median_Price", ascending=False)
```

| Code | Meaning |
|---|---|
| `groupby("location")` | Puts all listings of the same location together |
| `.agg(...)` | Calculates several statistics in one go (median, max, mean, min, count) |
| `loc_count >= 50` | Keeps only locations with at least 50 listings, because the average of 3 listings is not trustworthy. 489 locations → **42** |
| `sort_values(..., ascending=False)` | Most expensive first |

```python
plt.figure(figsize=(12, 10))
sns.barplot(data=loc_df, x="Median_Price", y="location")
plt.title("Median Price per Marla by Location")
plt.show()
```

(`x` and `y` are swapped so that long location names are written horizontally and stay readable.)

**Result (median price per Marla):**

| Rank | Location | Median (Lakh / Marla) |
|---|---|---|
| 1 | F-6 | ~150 |
| 2 | F-7 | ~143 |
| 3 | D-12 (D-12/1) | ~118 to 120 |
| 4 | F-8 | ~115 |
| 5 | I-8/3 | ~106 |
| … | … | … |
| 16 | DHA Defence Phase 5 | ~64 |
| 17 | DHA Defence Phase 2 | ~62 |
| last | Bani Gala | ~34 |

### 10.8 Does the number of bedrooms change price? (bar plot)

```python
plt.figure(figsize=(8, 6))
sns.barplot(data=df, y="Price (Lakh)", x="beds")
plt.title("Price x Beds")
plt.show()
```

Each bar is the **average** price for that number of beds, and the black line shows how uncertain that average is (a long line = few listings or very mixed prices).

**What I saw:** average price rises from about 180 Lakh (2 beds) to about 3,400 Lakh (11 beds). The rise is steep rather than a straight line, which is why the correlation was only 0.34. The 1-bed bar has a very long line, so those few listings are odd (probably plots or commercial entries with beds filled wrongly). The 8 to 11 bed bars have long lines too, because they have only a handful of listings.

---

## 11. EDA Findings in One Place

1. **Price is right-skewed** (mean ≈ 1098 vs median ≈ 550 Lakh, max 35,000 Lakh). A **log transform** makes it bell-shaped, so the model will be trained on log price.
2. **Area is the strongest numeric feature** (correlation 0.76 with price), but the relationship is a fan, not a line. Area alone is not enough.
3. **Beds and baths** are strongly related to each other (0.68) and only weakly to price (0.34 and 0.22). Price rises *steeply* with beds, but part of that effect is simply "more beds = bigger house".
4. **Location has a huge effect on price.** The most expensive location is more than 4 times as expensive per Marla as the cheapest.
5. **There are two different markets in Islamabad:**
   - **Developed sectors** (F, D, I, G, E series): median about **77 to 150** Lakh per Marla. All of the top 15 are sectors.
   - **Housing societies** (DHA, Bahria Enclave, B-17 societies, Top City, Jinnah Gardens): median about **34 to 64** Lakh per Marla.
6. **Bigger plots have a lower rate per Marla** (for example Bani Gala has large plots and the lowest rate), so price per Marla reflects size as well as location.
7. **Location names are messy.** The same sector appears several times (`D-12`, `D-12/1`, `G-9`, `G-9/4`...). These need to be merged.
8. **Rare values are unreliable**: houses with 1 bed or 8 to 11 beds have very few listings.

**Caveats:** all prices are *asking* prices. The location chart only covers the 42 locations with 50+ listings. Correlation does not prove cause (for example, sectors are expensive partly because they are older, central and well developed).

---

## 12. Mistakes I Made and Fixed

These are written here on purpose, because they were the most valuable part of learning.

| # | Mistake | Symptom | Fix |
|---|---|---|---|
| 1 | Scraped each field into its **own list** (`prices`, `beds`, `areas`...) | `ValueError: All arrays must be of the same length`, and values shifting into the wrong columns (listings without beds/baths misaligned everything) | Scrape **card by card**, one dictionary per house, with `"N/A"` when a field is missing |
| 2 | Beds and baths used the **same selector** | Both columns showed the same value | Use the specific `aria-label` for each field |
| 3 | `while True` with no page increment | The same page requested forever | Increase `page_no`, stop on empty page or missing "Next" |
| 4 | `print(...)` outside the `for` loop | Only the last card printed | Fix indentation |
| 5 | `combined_rows.extend(rows)` **inside** the `while` loop | Every page's rows added again and again | Append once per row (or extend after the loop) |
| 6 | `index="False"` (a string) in `to_csv` | An extra index column was still saved (non-empty string is `True`) | Use `index=False` (boolean, no quotes) |
| 7 | `for l in areas` instead of `for l in links` | The `links` column came out empty | Loop over the correct list |
| 8 | Area regex used `\d` instead of `\d+` | `13.6 Marla` → `3.6` | Use `\d+\.?\d*` |
| 9 | Global outlier threshold idea | Would have removed real F-6 / F-7 houses | Judge outliers using location |
| 10 | Keeping `ppm` as a column | Would leak the target into the model | Drop it before saving |
| 11 | `groupby` on the wrong column (`Area (Marla)` instead of `ppm`) | Got the median *size* of each location instead of the median *price per Marla* | Aggregate the right column |
| 12 | Sorted the location table by `loc_count` before plotting | Bars were not in price order, so no ranking was visible | Sort by `Median_Price` |
| 13 | Bar plot of two numeric columns (`Area` vs `Price`) | Unreadable x-axis | Use a scatter plot for two numeric columns |
| 14 | Passed `palette` without `hue` | Seaborn warnings | Remove `palette` or assign `hue` |

---

## 13. Limitations

Being honest about what this data cannot do:

- **Asking prices, not sale prices.** Listings show what sellers *want*, not what the house finally sold for.
- **One-time snapshot.** Prices change; the data reflects the day it was scraped (add the date here).
- **No listing ID/URL saved**, so exact duplicates cannot be told apart from similar houses.
- **No exact location** (latitude/longitude), construction year, floors, condition or furnishing. Many things that move a price are missing.
- **~490 distinct locations** is a lot of categories for a few thousand rows; many have very few listings, and location names are inconsistent.
- **Possible junk entries** still remain (typos, token/installment prices, commercial properties listed as houses, odd 1-bed listings).
- **Scrapers break.** Zameen can change its HTML at any time.

---

## 14. Next Steps and Roadmap

### Phase 3: Exploratory Data Analysis ✅
- [x] Price distribution and log transform
- [x] Area vs price, beds vs baths, beds vs price
- [x] Correlation heatmap
- [x] Median price per Marla by location

### Phase 4: Feature Engineering ⏳ (next)
- [ ] **Clean location names**: merge `D-12/1`, `D-12/3`, `D-12, Islamabad` into one `D-12`, `G-9/4` into `G-9`, etc.
- [ ] Create a **`location_type` feature**: sector (F, G, D, I, E...) vs housing society (DHA, Bahria, B-17...), since EDA showed they are two different markets
- [ ] Group rare locations into an `Other` category
- [ ] Encode locations (one-hot, or target encoding done carefully)
- [ ] Handle missing beds/baths properly (median/mode, or `0` for plots)
- [ ] Review the odd 1-bed listings and the extreme areas (140, 280, 400 Marla)
- [ ] Apply the log transform to price

### Phase 5: Modelling
- [ ] Train/test split **before** any imputation or encoding (to avoid leakage)
- [ ] Baseline: Linear Regression
- [ ] Better models: Random Forest, Gradient Boosting / XGBoost
- [ ] Cross-validation and hyperparameter tuning
- [ ] Metrics: MAE, RMSE, R², and MAPE (percentage error is easiest to explain)
- [ ] Compare models and pick one

### Phase 6: The "Fair Price Detector"
- [ ] Predicted price vs asking price → difference in %
- [ ] Label: **Underpriced / Fair / Overpriced** using a threshold (e.g. ±10 to 15%)
- [ ] Function: `check_price(location, area, beds, baths, asking_price)`

### Phase 7: App and Deployment
- [ ] Simple web app (for example Streamlit) where a user enters details and sees a verdict
- [ ] Deploy it and add screenshots to this README

### Phase 8: Improvements
- [ ] Re-scrape saving each listing's **URL/ID** and the scrape **date**
- [ ] Extend to **Rawalpindi** with a `city` column (same pipeline, a different `all_locations` link)
- [ ] Add more features (floors, age of house) if available on the listing page
- [ ] Track prices over time

---

## 15. How to Run

**1. Clone and install**
```bash
git clone https://github.com/Malik-Zain-555/sahi-daam-fair-price-detector.git
cd sahi-daam-fair-price-detector
pip install requests beautifulsoup4 pandas numpy matplotlib seaborn
```

**2. Scrape** (slow on purpose, there are 500+ areas; test on 3 areas first)
```bash
python Data/raw/main.py
```

**3. Clean + explore**
Run `SDFPD.py` (cell by cell in Zed/VS Code, or as a normal script). The cleaned data is saved to `Data/processed/ISB_clean.csv`, and the EDA plots appear while the cells run.

> 💡 When testing, loop over `areas_df.head(3)` instead of all 501 areas, to avoid sending thousands of requests by mistake.

---

## 16. Ethics and Responsible Scraping

- I checked `robots.txt`. The `/Houses_Property/` listing pages are **not** in its disallow list, but the file does disallow many other paths, and the website's **Terms of Service** may apply separately. This project is for **learning and portfolio use only**.
- A delay (`time.sleep`) is added between requests, and the scraper stops if the status code is not 200.
- Only **public listing details** are collected (price, location, size, beds, baths). **No phone numbers, names or seller information** are scraped or stored.
- If the site blocks the scraper or asks for a captcha, the scraper stops. It must not be bypassed.
- Raw scraped data should not be redistributed as a product.

---

*Built by [Malik Zain](https://github.com/Malik-Zain-555), a BS Computer Science student, as a learn-by-building machine learning project.*
