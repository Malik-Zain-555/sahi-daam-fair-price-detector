# Sahi Daam: Islamabad House Listings Scraper

A beginner-friendly Python scraper that collects **house listings for every area of Islamabad** from [zameen.com](https://www.zameen.com) and saves them into one CSV file.

This is the **data collection step** of the *Sahi Daam (Fair Price Detector)* project. The goal of the full project is to train a machine learning model that can tell whether a house price is fair. A model needs data, and this script gets it.

---

## Table of Contents

1. [What does this script do?](#1-what-does-this-script-do)
2. [What data do you get?](#2-what-data-do-you-get)
3. [Requirements and installation](#3-requirements-and-installation)
4. [How to run it](#4-how-to-run-it)
5. [How it works, step by step](#5-how-it-works-step-by-step)
6. [Key features explained simply](#6-key-features-explained-simply)
7. [Understanding the output files](#7-understanding-the-output-files)
8. [Examples](#8-examples)
9. [Known issues and limitations](#9-known-issues-and-limitations)
10. [Troubleshooting](#10-troubleshooting)
11. [Customizing the script](#11-customizing-the-script)
12. [Responsible scraping](#12-responsible-scraping)

---

## 1. What does this script do?

Imagine you open zameen.com, pick an area like **F-7**, and scroll through every page of houses, writing down each house's price, size, beds and baths by hand. Now imagine doing that for **501 areas**.

This script does exactly that, automatically:

1. It downloads the list of all Islamabad areas from zameen.com.
2. For each area, it opens page 1, page 2, page 3 and so on, until there are no more pages.
3. On every page, it reads each house card and picks out the details.
4. It saves everything into `ISB_areas.csv`.

---

## 2. What data do you get?

Each row in the CSV is **one house listing** with 5 columns:

| Column | Meaning | Example (illustrative) |
|---|---|---|
| `location` | Where the house is | `F-7, Islamabad` |
| `area` | Size of the house (as written on the site) | `1 Kanal` |
| `beds` | Number of bedrooms | `5` |
| `baths` | Number of bathrooms | `6` |
| `price` | Asking price (as written on the site) | `12.5 Crore` |

If a detail is missing on a listing, the script writes `N/A` instead of crashing.

> **Note:** All values are saved as **raw text**, exactly as shown on the website. Prices like "12.5 Crore" and sizes like "1 Kanal" must be converted to numbers before training a model.

---

## 3. Requirements and installation

You need **Python 3.8 or newer** (developed and tested on Python 3.12).

Install the three libraries the script uses:

```bash
pip install requests beautifulsoup4 pandas
```

| Library | Why we need it |
|---|---|
| `requests` | Downloads web pages (like a browser, but in code) |
| `beautifulsoup4` | Reads the HTML of a page and lets us pick out the parts we want |
| `pandas` | Builds tables and writes the CSV file |

The script also uses `time`, `os`, `threading` and `concurrent.futures`, which come built into Python.

---

## 4. How to run it

1. Put `main.py` in a folder.
2. Open a terminal in that folder.
3. Run:

```bash
python main.py
```

You will see progress like this, one line per finished area:

```
0 already done, 501 to go
D_12-160 done (407 houses)
Bani_Gala-340 done (449 houses)
G_13-330 done (516 houses)
...
All finished!
```

Scraping all 501 areas takes a long time (it can be hours). **You do not have to watch it.** If it stops for any reason, just run the same command again and it continues where it left off (see [Resume](#resume-pick-up-where-you-stopped)).

> **Tip for Windows users:** Stop your PC from going to sleep while the script runs. A sleeping PC drops the internet connection and causes errors. Set *Settings → System → Power → Sleep* to **Never**, or run `powercfg /change standby-timeout-ac 0`.

### Using it in Jupyter / VS Code / Spyder

The file is split into cells marked with `# %%`. You can run each cell one by one from top to bottom. Cell names tell you what each part does.

---

## 5. How it works, step by step

The script is divided into 6 sections (cells).

### Section 0: Imports & Setup
Loads the libraries and defines three settings:

- `headers`: a browser-like **User-Agent**. Without it, many sites recognize the default Python request and refuse to answer.
- `OUT_FILE = "ISB_areas.csv"`: where the data is saved.
- `DONE_FILE = "done_areas.txt"`: where finished areas are recorded.

It also creates a `lock` (explained in [Parallel scraping](#parallel-scraping-5-areas-at-once)).

> **Why is `requests` imported as `re`?** In this project, `import requests as re` is just a short nickname. It is **not** Python's regex module `re`. Do not add `import re` anywhere in this file, or it will replace the nickname and break the scraper.

### Section 1: Helper, fetch a page with retries
`get_page()` downloads one web page. If the download fails (internet drops, server resets the connection), it **waits and tries again**, up to 5 times. The wait doubles each time: 2s, 4s, 8s, 16s, 32s. This is called *exponential backoff*.

### Section 2: Scrape one area (all pages) and save
`area_scrapper(name)` is the main worker. For one area it:

1. Builds the page link, for example `https://www.zameen.com/Houses_Property/Islamabad_F_7-165-1.html`
2. Downloads the page and finds all **house cards** on it
3. For every card, reads price, location, beds, baths and area
4. Looks for a **Next** button. If it exists, goes to the next page. If not, the area is finished.
5. Saves all rows of that area to the CSV and marks the area as done

### Section 3: Get all Islamabad area names
Opens zameen.com's "all locations" page for Islamabad and collects the link of every area (up to 501). Then it cuts each link down to just the area name.

Example of the cutting:

```
Link:  /Houses_Property/Islamabad_F_7-165-1.html
Name:  F_7-165
```

The number (`165`) is zameen's internal ID for that area.

### Section 4: Skip already finished areas
Reads `done_areas.txt` and removes finished areas from the to-do list. On the first run the file does not exist, so everything is to-do. You will see:

```
0 already done, 501 to go
```

### Section 5: Run the scraper
Starts the scraping with 5 areas running at the same time. Prints `All finished!` at the end.

---

## 6. Key features explained simply

### Parallel scraping: 5 areas at once

Doing areas one by one is slow because the script spends most of its time *waiting* for websites to reply. Instead, we use **5 workers (threads)**. While one worker waits for a page, the others keep going.

```
Worker 1: F_7    -> page 1, page 2, page 3 ...
Worker 2: D_12   -> page 1, page 2 ...
Worker 3: G_13   -> page 1, page 2, page 3, page 4 ...
Worker 4: B_17   -> ...
Worker 5: DHA_2  -> ...
```

**Is the data mixed up between workers?** No. Each worker scrapes **one whole area** with its own session and its own list of rows. The only shared thing is the CSV file, and a `lock` makes sure only one worker writes to it at a time, like a single-person door.

Because of this, areas finish **out of order**. That is why your log does not follow the same order as the area list. This is normal.

### Retries: surviving bad connections

Websites sometimes close the connection (`ConnectionResetError`). Without protection, one failure would stop the whole run. With `get_page()`, a failure just prints a message and tries again:

```
ConnectionError on https://www.zameen.com/... | retry 1/5 in 2s
```

If all 5 tries fail, that area is **not** marked as done, so the next run tries it again.

### Save as you go

Each area is appended to the CSV **the moment it finishes**. If your PC crashes at area 300, areas 1 to 299 are safe in the file.

### Resume: pick up where you stopped

Every finished area name is written to `done_areas.txt`. When you run the script again, it reads this file and skips those areas.

```
First run  : 0 already done, 501 to go     (you press Ctrl+C after 120 areas)
Second run : 120 already done, 381 to go   (continues from there)
Third run  : 501 already done, 0 to go     (nothing left, exits)
```

**To start completely fresh,** delete **both** `ISB_areas.csv` and `done_areas.txt`. If you delete only `done_areas.txt`, every area is scraped again and **appended a second time**, creating duplicates.

### Polite delay

The script waits 0.5 seconds between pages of the same area so it does not hammer the website.

---

## 7. Understanding the output files

| File | Created by | What it holds |
|---|---|---|
| `ISB_areas.csv` | Script | All scraped house rows |
| `done_areas.txt` | Script | One finished area name per line (used for resume) |

Both are generated files. You normally do **not** commit them to Git. Add them to `.gitignore`:

```
ISB_areas.csv
done_areas.txt
```

---

## 8. Examples

### Load and look at the data

```python
import pandas as pd

df = pd.read_csv("ISB_areas.csv")
print(df.shape)      # (rows, columns)
print(df.head())     # first 5 rows
```

### Count how many values are missing

```python
print((df == "N/A").sum())
```

### Check how many exact duplicate rows exist

```python
print(df.duplicated().sum())
```

### Re-scrape everything from scratch

```bash
# Windows PowerShell
del ISB_areas.csv, done_areas.txt
python main.py
```

### Scrape only one area (quick test)

Before running all 501 areas, test with one small area. In `main.py`, temporarily change section 4:

```python
todo = ["F_7-165"]
```

---

## 9. Known issues and limitations

Being honest about these helps anyone using the data.

1. **Some areas return 0 houses.** Areas whose link is a full URL (for example Taxila or Rawalpindi areas) do not contain `/Islamabad_`, so the script builds a broken link and finds nothing. These were marked as done with 0 houses.

   *Fix idea:* inside `area_scrapper`, if `name` starts with `http`, use `f"{name}-{page_no}.html"` as the link.

2. **Duplicate listings.** Areas overlap. A parent area such as `DHA_Defence_Phase_2` already includes its sectors, so the same house can appear 2 to 3 times in the CSV. Remove duplicates before training a model. Scraping each listing's own link and removing duplicates by that link is the most reliable method.

3. **No status-code check.** If zameen.com blocks you (HTTP 403 or 429), the page has no house cards, and that area would be saved as 0 houses and marked done.

4. **No area column in the CSV.** You cannot tell which scraped area a row came from. Adding `"source_area": name` inside `rows.append({...})` fixes this.

5. **Data is raw text.** Prices and sizes include units (Crore, Lakh, Kanal, Marla, Sq. Yd.) and must be cleaned into numbers.

6. **Selectors can break.** The script finds houses with CSS class names such as `ul.e20beb46 li.a37d52f0` and `layout-grid_layoutGrid__htd53`. These look auto-generated and may change when zameen updates its website. If the CSV comes out empty, they are the first thing to check.

---

## 10. Troubleshooting

| Problem | Likely cause | What to do |
|---|---|---|
| `ConnectionResetError 10054` | Server closed the connection, or PC went to sleep | Already handled by retries. Disable sleep. Lower workers to 3 |
| CSV is empty or has very few rows | Blocked, or CSS classes changed | Print `html.status_code`. Re-inspect the page in your browser |
| `501 already done, 0 to go` | All areas finished earlier | Delete `ISB_areas.csv` and `done_areas.txt` to start over |
| `AttributeError: module 're' has no attribute 'get'` | You imported Python's `re` and replaced the `requests` nickname | Remove `import re`, or use `import re as regex` for regex code |
| Duplicate rows after rerun | Deleted only `done_areas.txt` | Delete both files together |
| Many retry messages | Too many requests too fast | Set `max_workers=3` and raise the delay |

---

## 11. Customizing the script

| What you want | What to change |
|---|---|
| Faster or slower scraping | `max_workers=5` in section 5. Higher is faster but riskier |
| Gentler on the server | `time.sleep(0.5)` in section 2. Raise to `1` or `2` |
| More or fewer retries | `retries=5` in `get_page()` |
| Different city | Change the `all_locations` link and the `/Islamabad_` text in sections 2 and 3 |
| Output file name | `OUT_FILE` in section 0 |
| Extra data per house | Add another `select_one(...)` in section 2 and a new key in `rows.append({...})` |

---

## 12. Responsible scraping

- Keep the delays and the low worker count. Do not overload the website.
- Check zameen.com's Terms of Service and `robots.txt` before using the data, especially for anything beyond personal learning.
- Do not publish or sell scraped data without permission.
- This project is for **education and learning**.

---

## Project structure

```
sahi-daam-fair-price-detector/
└── Data/
    └── raw/
        ├── main.py           # the scraper (this README explains it)
        ├── ISB_areas.csv     # generated: scraped houses
        └── done_areas.txt    # generated: finished areas (for resume)
```

## What comes next

1. Fix the skipped full-URL areas
2. Remove duplicate listings
3. Convert price and size text into numbers
4. Train the fair price model
