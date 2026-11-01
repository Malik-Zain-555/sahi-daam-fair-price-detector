# Sahi Daam: The Fair-Price Detector

*A beginner-friendly guidebook to building a real machine learning project from scratch*

---

## 1. What is this project?

**Sahi Daam** ("the right price") is a tool that answers one question: **"Is this listing overpriced?"**

You collect real property listings (or car listings) from Pakistani marketplaces, train a model to predict what each listing *should* cost, and then compare that prediction to the actual asking price. Listings priced far above the prediction are flagged as **likely overpriced**. Listings far below are flagged as **possible bargains**.

The key idea: **the model's mistakes become the product.** Most beginner projects stop at "predict the price." You go one step further and use the errors to find deals.

### Who is it for?

Anyone buying a plot, house, or car who wonders, "Am I paying too much?"

### What will you have at the end?

- A cleaned dataset that you collected yourself
- A trained model that beats a simple baseline
- A written error analysis (where and why the model fails)
- A ranked list of overpriced and underpriced listings
- A Streamlit web app anyone can try
- A GitHub repo with a professional README

---

## 2. Why this project teaches more than a Kaggle download

| Normal beginner project | Sahi Daam |
| --- | --- |
| Data is already clean | You collect and clean messy real data |
| Goal: get a high score | Goal: solve a real problem |
| Stop at accuracy | Investigate errors and turn them into a feature |
| Only calls libraries | You also write one algorithm from scratch |

You will practice the full ML workflow: **collect, clean, engineer features, model, evaluate, investigate, deploy.**

---

## 3. Choose your version

|  | Property (Zameen-style) | Cars (PakWheels-style) |
| --- | --- | --- |
| Key columns | City, area, size (marla/kanal), bedrooms, baths, price | Make, model, year, mileage, engine, city, price |
| Difficulty | Medium (messy units like marla, crore, lakh) | Easier (cleaner columns) |
| Best for | Learning data cleaning | Getting to modeling faster |

**Recommendation:** If you want maximum learning, pick property. If you want a faster win, pick cars. The steps below work for both. Examples use property.

---

## 4. Tools you need

- **Python 3.10+** and **Jupyter Notebook** (you already use these)
- **pandas, numpy, matplotlib, seaborn** (you know these)
- **scikit-learn** (you know this)
- **requests + BeautifulSoup** (new: for collecting data)
- **XGBoost or LightGBM** (new: a stronger model)
- **Streamlit** (you used this in the churn project)
- **Git/GitHub** (you already use this)

Install the new ones:

```
pip install requests beautifulsoup4 xgboost lightgbm
```

---

## 5. The plan at a glance

Plan for **6 weeks at roughly 5 to 7 hours per week**. Go faster or slower as you like, but do the phases **in order**.

| Week | Phase | Main output |
| --- | --- | --- |
| 1 | Set up and collect data | `raw_listings.csv` |
| 2 | Clean the data | `clean_listings.csv` |
| 3 | Explore and engineer features | EDA notebook, feature table |
| 4 | Baseline and models | Results table |
| 5 | Investigate errors and flag deals | Error analysis, overpriced list |
| 6 | Build the app and write the README | Live app, finished repo |

**Optional side-quest** (any time after week 4): Linear Regression from scratch in NumPy.

---

## 6. Phase-by-phase guide

### Week 1: Set up and collect data

**Goal:** Get at least **2,000 listings** into one CSV.

**Step 1: Create the repo.** Name it `sahi-daam`. Make this folder structure:

```
sahi-daam/
  data/raw/
  data/clean/
  notebooks/
  app/
  README.md
```

**Step 2: Decide how to get data.** Try these in order:

1. **Check for an existing dataset first.** Search Kaggle for Zameen or PakWheels datasets. This is the safest start and gives you something to work with immediately.
2. **Read the site's rules.** Before scraping any website, open its `robots.txt` (for example `site.com/robots.txt`) and read its terms of service. If scraping is not allowed, do not scrape. Use a dataset instead.
3. **If scraping is allowed:** be polite. Add a delay between requests (`time.sleep(2)`), collect only what you need, do not hammer the server, and never collect personal data like phone numbers or seller names.
4. **Manual option:** If both fail, collect 200 to 300 listings by hand into a spreadsheet. It is slow, but you will understand the data deeply, and you can combine it with a Kaggle dataset.

**Step 3: Columns to collect (property):** city, area/locality, property type (house, plot, flat), size and size unit, bedrooms, bathrooms, price, date listed.

**Starter code for scraping (adapt to the real page structure):**

```python
import requests, time
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0 (learning project)"}
rows = []

for page in range(1, 6):
    url = f"https://EXAMPLE-SITE/listings?page={page}"
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    # Inspect the page in your browser (right click > Inspect)
    # to find the right tags and classes, then fill in below.
    # for card in soup.select("CARD_SELECTOR"):
    #     rows.append({...})
    time.sleep(2)
```

**Checkpoint:** You have a `raw_listings.csv` with 2,000+ rows (or your best realistic number). Commit it to Git.

**What you learn:** how websites are structured, how real data looks, and how to be a responsible data collector.

---

### Week 2: Clean the data

**Goal:** Turn messy text into clean numbers. This is the hardest and most valuable phase.

**Typical problems you will find:**

| Problem | Example | Fix |
| --- | --- | --- |
| Price as text | "1.5 Crore", "85 Lakh" | Convert to a single number in PKR |
| Mixed size units | "5 Marla", "1 Kanal" | Convert everything to one unit (marla) |
| Missing values | No bedrooms listed | Decide: drop, fill with median, or add an "unknown" flag |
| Duplicates | Same listing posted twice | `df.drop_duplicates()` |
| Outliers | Price of 1 PKR or 50 billion | Investigate, then remove or cap with a written reason |
| Inconsistent names | "DHA Phase 5" vs "dha phase-5" | Lowercase, strip, standardize |

**Helpful conversions:** 1 lakh = 100,000. 1 crore = 10,000,000. 1 kanal = 20 marla.

**Starter code for prices:**

```python
def price_to_pkr(text):
    text = str(text).lower().replace(",", "").strip()
    number = float("".join(c for c in text if c.isdigit() or c == "."))
    if "crore" in text:
        return number * 10_000_000
    if "lakh" in text:
        return number * 100_000
    return number

df["price_pkr"] = df["price"].apply(price_to_pkr)
```

**Rules for good cleaning:**

- Never overwrite raw data. Always save cleaned data to a new file.
- Keep a cleaning log in your notebook: "Removed 43 rows because price was under 100,000, since these looked like rent or typos."
- Count rows before and after every step.

**Checkpoint:** `clean_listings.csv` with no text prices, one size unit, and a written list of every decision you made.

---

### Week 3: Explore and engineer features

**Goal:** Understand the data and create columns that help the model.

**Exploration questions to answer with charts:**

1. What does the price distribution look like? (It will be heavily skewed.)
2. Which cities and areas are the most expensive?
3. How does price relate to size? To bedrooms?
4. Where are the weird points?

**Feature engineering ideas:**

- **Price per marla** (great for understanding, but do **not** use it as an input feature for predicting price, since it contains the answer)
- **Log of price.** Prices are skewed, so training on `np.log1p(price)` often works much better.
- **Locality grouping.** Areas with fewer than 10 listings get grouped into "other".
- **Area average price.** Calculate it using **training data only** (see the warning below).
- **Rooms total** = bedrooms + baths
- **Is plot** (yes/no)

**Warning: data leakage.** If you compute something like "average price in this area" using the *whole* dataset and then split into train and test, the test answers leak into your features. Always split first, then compute statistics from the training set only. Writing about this mistake in your README is a strong signal of understanding.

**Checkpoint:** An EDA notebook with 6 to 8 charts, each followed by one sentence about what you learned.

---

### Week 4: Baseline and models

**Goal:** Build a model that clearly beats a simple baseline.

**Step 1: Split the data.** Use `train_test_split` with a fixed `random_state`. (If your listings have dates, a time-based split is even better.)

**Step 2: Build the baseline.** The baseline is deliberately simple: predict the **median price per marla in that area, multiplied by the size**. Record its error. Every model must beat this, or it is not adding value.

**Step 3: Train models in this order:**

1. Linear Regression (on log price)
2. Random Forest
3. XGBoost or LightGBM

**Step 4: Evaluate with the right metrics:**

- **MAE** (mean absolute error): "on average, we are off by X rupees"
- **RMSE**: like MAE but punishes big mistakes more
- **MAPE or median % error**: "we are off by about 12%", which is easier to explain to non-technical people
- **R-squared**: how much variation the model explains (use it as a secondary metric)

**Step 5: Use cross-validation.** Use 5-fold CV so your result does not depend on one lucky split.

**Step 6: Make a results table** like this and put it at the top of your README:

| Model | MAE (PKR) | Median % error | Beats baseline? |
| --- | --- | --- | --- |
| Baseline (area median) | ... | ... | n/a |
| Linear Regression | ... | ... | ... |
| Random Forest | ... | ... | ... |
| XGBoost | ... | ... | ... |

**Checkpoint:** A results table and a one-paragraph explanation of why the best model won.

---

### Week 5: Investigate errors and flag deals

This is the heart of the project and what makes it different.

**Part A: Error analysis (your strength)**

- Plot predicted vs. actual price. Where do the dots drift from the diagonal line?
- Which cities or areas have the biggest errors? Is the model worse for expensive listings?
- Look at the 20 worst predictions by hand. Why were they wrong? (Typo in the data? Luxury property with no luxury feature in your columns? Rare location?)
- Plot feature importance. Does it match common sense (size and location matter most)?

**Part B: The overpriced detector**

```python
df_test["predicted"] = np.expm1(model.predict(X_test))
df_test["gap_pct"] = (df_test["price_pkr"] - df_test["predicted"]) / df_test["predicted"] * 100

overpriced = df_test.sort_values("gap_pct", ascending=False).head(20)
bargains   = df_test.sort_values("gap_pct").head(20)
```

**Be honest about what this means.** A listing flagged as overpriced is not *proven* overpriced. The model may simply be missing information (a corner plot, a renovated house, a typo in the listing). So label your output as **"priced above what similar listings suggest"** rather than "this is a scam." Writing this limitation clearly is a mark of maturity.

**Part C: Sanity check.** Pick 5 flagged listings and look at them manually. Do any have an obvious reason for the gap? Write down what you find.

**Checkpoint:** An error-analysis notebook, a list of top overpriced and top bargain listings, and a "Where the model fails" section.

---

### Week 6: Build the app and write the README

**The app (Streamlit):**

1. Inputs: city, area, size, bedrooms, bathrooms
2. Output: **estimated fair price range** (for example, prediction plus or minus your typical error)
3. Optional input: "Asking price". If the user types the seller's price, show whether it is above, near, or below the estimate
4. A chart showing how that area's prices are spread out

**Save and load your model:**

```python
import joblib
joblib.dump(model, "model.pkl")        # in your notebook
model = joblib.load("model.pkl")        # in your app
```

Deploy it free on **Streamlit Community Cloud** or **Hugging Face Spaces**.

**README structure (copy this):**

1. **One-line pitch:** "Sahi Daam estimates fair prices for Pakistani property and flags listings priced far above similar ones."
2. **Demo:** screenshot or GIF plus live link
3. **Results table** (baseline vs. models)
4. **Key findings:** 3 to 5 bullets
5. **How it works:** a short pipeline diagram or list
6. **Where the model fails:** your error analysis
7. **Limitations and ethics:** data source, scraping rules followed, no personal data stored, what the tool cannot know
8. **How to run it:** install and run commands
9. **What I would do next**

**Checkpoint:** A live app and a README that a stranger could understand in two minutes.

---

## 7. Side-quest: Linear Regression from scratch

Do this after Week 4. It takes about 2 hours and teaches you what `.fit()` actually does.

**Idea:** Prediction = weight × size + bias. Start with random weights, measure the error, nudge the weights in the direction that reduces error, and repeat. This is **gradient descent**.

```python
import numpy as np

def fit_linear(X, y, lr=0.01, epochs=1000):
    n, d = X.shape
    w = np.zeros(d)
    b = 0.0
    for _ in range(epochs):
        pred = X @ w + b
        error = pred - y
        w -= lr * (2 / n) * (X.T @ error)
        b -= lr * (2 / n) * error.sum()
    return w, b
```

**Tips:** Scale your features first (standardize them) or the numbers will explode. Then compare your weights to scikit-learn's `LinearRegression`. If they are close, you have understood it. Put the comparison in your repo as `from_scratch.ipynb`.

---

## 8. Common mistakes to avoid

| Mistake | Why it hurts | Do this instead |
| --- | --- | --- |
| Using price per marla as a feature | Leaks the answer | Use it only for exploration |
| Computing area averages on all data | Test data leaks into training | Split first, then compute |
| Removing outliers without a reason | Hides real behavior | Log every removal and why |
| Trusting R-squared alone | Can look great while errors are large | Report MAE and % error |
| Celebrating a high score immediately | May be a bug or leak | Check feature importance and sample predictions |
| Scraping aggressively | Can break rules and harm the site | Read terms, add delays, collect minimal data |
| Collecting personal data | Privacy risk | Never store names, phone numbers, or exact addresses |

---

## 9. Your weekly routine

- **Start of session:** read your last notes and write today's single goal
- **During:** commit to Git after every meaningful step
- **End of session:** write 3 lines in a `LEARNING_LOG.md`: what I did, what confused me, what I will do next
- **If stuck for more than 45 minutes:** write the problem down in plain words, search the exact error message, then ask for help with your notebook and the error attached

The learning log becomes great material for your README and for interviews.

---

## 10. Level-up ideas (after you finish)

1. **Repeat the collection after a month** and measure how prices changed. This gives you a time series dataset for free.
2. **Add a map** of average price by area using Folium or Plotly.
3. **Try cars as well** and compare how the pipeline differs.
4. **Explain predictions with SHAP**: "This price is high because of size and location."
5. **Add prediction intervals** so the app shows a realistic range, not one number.

---

## 11. Final checklist

- [ ] Dataset of 2,000+ listings (or best realistic amount), source and rules documented
- [ ] Cleaning log with every decision explained
- [ ] EDA notebook with 6 to 8 annotated charts
- [ ] Baseline plus at least 3 models, with a results table
- [ ] Cross-validation used
- [ ] Error analysis with the 20 worst predictions examined
- [ ] Overpriced and bargain lists, with honest caveats
- [ ] Linear Regression from scratch (optional but recommended)
- [ ] Streamlit app deployed
- [ ] README with pitch, results, failures, limitations
- [ ] Learning log

---

## 12. Why the name "Sahi Daam"?

"Sahi daam" means "the right price" in Urdu and Hindi. It is short, easy to say, easy to remember, and clearly tells people what the tool is about.

**Other name options if you prefer:**

- **Munasib** (fair or reasonable)
- **DaamCheck**
- **FairRate PK**
- **Kitna Sahi** ("how right is it?")

**Repo name suggestion:** `sahi-daam-fair-price-detector`

**GitHub description:** *Estimates fair prices for Pakistani property listings with ML and flags listings priced far above similar ones. Python, scikit-learn, XGBoost, Streamlit.*

**Suggested GitHub topics:** `python`, `machine-learning`, `regression`, `data-cleaning`, `feature-engineering`, `xgboost`, `streamlit`, `pakistan`

---

*Start with Week 1, Step 1: create the repo. One small step today beats a perfect plan tomorrow.*
