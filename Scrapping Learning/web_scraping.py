# %% [markdown]
# # Web Scraping with Python: Learn by Building
#
# *Learn by building, not by theory.*
#
# This notebook takes you from your very first HTTP request to a working **price tracker**. Every section follows the same rhythm: a short explanation, code you run yourself, the mistakes beginners really make, and a small **Try it** task.
#
# ## Contents
#
# 1. [Requests: asking a website for a page](#1.-Requests)
# 2. [Parsing HTML with BeautifulSoup](#2.-Parsing-HTML)
# 3. [Finding tags: `find` and `find_all`](#3.-Finding-tags)
# 4. [CSS selectors: `select` and `select_one`](#4.-CSS-selectors)
# 5. [Storing data: list of dictionaries, pandas, CSV](#5.-Storing-data)
# 6. [Scraping many pages: functions and pagination](#6.-Pagination)
# 7. [Polite scraping: robots.txt, delays, error handling](#7.-Polite-scraping)
# 8. [Final project: a price tracker](#8.-Final-project)
# 9. [Cheat sheet, common mistakes, next steps](#9.-Cheat-sheet)
#
# ## How to use this notebook
#
# - Run cells from top to bottom.
# - Do not just read: **type the code yourself**, then change it and break it on purpose.
# - Sections 1 to 7 practise on **Hacker News** (`news.ycombinator.com`), a static site that is friendly to learners. Section 8 uses a real shop-comparison site.
#
# ## Requirements
#
# Python 3.9+ and three libraries:
#
# ```bash
# pip install requests beautifulsoup4 pandas
# ```
#
# ## Be a good citizen
#
# Scraping touches someone else's server. Before scraping any site, check its `robots.txt` and Terms of Service, keep your request count small, wait between requests, and identify problems instead of hammering the server. Section 7 covers this properly. Use what you learn here responsibly.

# %%
# Setup: all imports for the whole notebook live here
import os
import re
import time
from datetime import date
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs

print("requests", requests.__version__)

# %% [markdown]
# # 1. Requests
#
# ## What is web scraping?
#
# When you open a page in a browser, three things happen:
#
# 1. The browser sends a **request** to a server ("give me this page").
# 2. The server sends back **HTML** (the page's text and structure).
# 3. The browser **renders** that HTML into the page you see.
#
# A scraper does steps 1 and 2 with Python, skips step 3, and then **extracts only the data it wants** from the HTML.
#
# ## The `requests` library
#
# `requests.get(url)` sends the request and returns a **Response object**. The two attributes you will use all the time:
#
# | Attribute | Meaning |
# |---|---|
# | `response.status_code` | A number saying how the request went |
# | `response.text` | The page's HTML as one long string |
#
# ### Status codes worth knowing
#
# | Code | Meaning |
# |---|---|
# | 200 | OK, you got the page |
# | 403 | Forbidden, the server refused you (often bot blocking) |
# | 404 | Page not found (wrong URL) |
# | 429 | Too many requests, slow down |
# | 500 | The server itself failed |

# %%
url = "https://news.ycombinator.com/"

response = requests.get(url, timeout=10)

print(response.status_code)   # 200 means success
print(response.text[:300])    # the first 300 characters of raw HTML

# %% [markdown]
# ### Common mistake: forgetting `https://`
#
# A URL must start with a **scheme** (`http://` or `https://`). Browsers add it for you, Python does not. Without it you get `MissingSchema`.
#
# Tip for reading any Python error: **start from the last line** and match the name it mentions against your code.

# %%
try:
    requests.get("news.ycombinator.com")   # no https://
except requests.exceptions.MissingSchema as error:
    print("Error:", error)

# %% [markdown]
# ### Try it
#
# 1. Fetch `https://news.ycombinator.com/` and print the status code and the first 200 characters of the HTML.
# 2. Change the URL to a page that does not exist (add `/this-page-does-not-exist`). What status code do you get?
#
# > Do not practise on social networks such as Facebook. Their pages are built with JavaScript and their terms do not allow scraping. Use sites made for learning, or sites whose `robots.txt` allows what you are doing.

# %% [markdown]
# # 2. Parsing HTML
#
# Right now the HTML is one giant string. Searching a string for "the title" is painful. **BeautifulSoup** turns the string into a **tree** of tags, so you can say "give me all the links".
#
# ```python
# soup = bs(html_text, "html.parser")
# ```
#
# - The first argument is the HTML text.
# - The second is the **parser** name, the engine that reads the HTML. `"html.parser"` is built into Python.
# - A tag object gives you the whole tag; add `.text` to get only the text inside it.

# %%
soup = bs(response.text, "html.parser")

print(soup.title)        # the whole tag
print(soup.title.text)   # only the text inside

# %% [markdown]
# ### Common mistake: a typo in the parser name
#
# `"html-parser"` (hyphen) fails with `FeatureNotFound: Couldn't find a tree builder`. The error even suggests installing a library, but the real problem is the spelling. The correct name is `"html.parser"` (dot).
#
# ### Try it
#
# Print `soup.title` and `soup.title.text` and describe the difference in one sentence.

# %% [markdown]
# # 3. Finding tags
#
# | Method | Returns |
# |---|---|
# | `soup.find("a")` | the **first** matching tag |
# | `soup.find_all("a")` | a **list** of all matching tags |
#
# Once you hold a tag, you can read three things from it:
#
# - its text: `tag.text`
# - an attribute, such as a link's address: `tag["href"]` (or `tag.get("href")`)
# - tags nested inside it: `tag.find(...)`
#
# `tag["href"]` raises a `KeyError` if the attribute is missing, while `tag.get("href")` quietly returns `None`.

# %%
first_link = soup.find("a")
print(first_link)

all_links = soup.find_all("a")
print("Links on the page:", len(all_links))

for link in all_links[:5]:
    print(repr(link.text), "->", link.get("href"))

# %% [markdown]
# ### Two things to notice in that output
#
# 1. The first link has **empty text**, because it only contains an image. A tag with no text gives `""`, which is not an error.
# 2. Some `href` values are full URLs and some are **relative** (`newest`, `front`). Relative links cannot be fetched directly. You join them to the site address (see section 5).
#
# ### Common mistake: `.text` on a list
#
# `find_all` returns a **list**, and a list has no `.text`. You must loop and call `.text` on **each tag**.

# %%
try:
    print(all_links.text)
except AttributeError as error:
    print("Error:", error)

# %% [markdown]
# ### Another problem: `find_all("a")` grabs everything
#
# The first five links were menu items, not stories. Real scraping is mostly about selecting **only the tags you want**. That is what CSS selectors do.
#
# ### Try it
#
# Loop over the first 5 links and print each one's text and `href`. Which ones have no text?

# %% [markdown]
# # 4. CSS selectors
#
# `soup.select("...")` finds tags using the same selector language as CSS. It returns a **list**. `soup.select_one("...")` returns only the **first match** (or `None` if there is none).
#
# | Selector | Means |
# |---|---|
# | `a` | every `<a>` tag |
# | `.price` | any tag with class `price` |
# | `span.titleline` | a `<span>` with class `titleline` |
# | `div.card > p` | a `<p>` that is a **direct child** of `div.card` |
# | `div.card p` | a `<p>` **anywhere inside** `div.card` |
# | `a[href]` | an `<a>` that has an `href` attribute |
#
# The `>` means *direct child only*. Without it, the selector also matches deeper descendants.
#
# ## How to find the right selector
#
# 1. Open the page in your browser.
# 2. Right-click the data you want and choose **Inspect**.
# 3. Read the tag name, its class, and what it sits inside.
# 4. Write a selector, test it in the notebook, and check how many items it returns.

# %%
# A tiny offline example so you can see selectors in action
sample_html = """
<div class="card"><h2>Phone</h2><p>Rs 500</p></div>
<div class="card"><h2>Watch</h2><p>Rs 900</p></div>
"""
sample = bs(sample_html, "html.parser")

print(sample.select_one("div.card > h2").text)     # first card's title
print([p.text for p in sample.select("div.card > p")])   # all prices

# %%
# Now the real thing: Hacker News story titles
story_links = soup.select("span.titleline > a")
print("Stories found:", len(story_links))

for number, story in enumerate(story_links[:10], start=1):
    print(f"{number}. {story.text}")
    print("   ", story["href"])

# %% [markdown]
# `enumerate(..., start=1)` numbers the items from 1. By default `enumerate` starts at 0.
#
# ### Try it
#
# 1. Inspect a Hacker News story title and build the selector yourself.
# 2. Remove the `>` from the selector. Does the number of results change?
# 3. Also print each story's **points** (hint: the score lives in the *next* row, and some posts have no score, so handle `None`).

# %% [markdown]
# # 5. Storing data
#
# A scraper that only prints is not very useful. Store what you find.
#
# ## List of dictionaries
#
# Make **one dictionary per item** and collect them in a list:
#
# ```python
# stories = [
#     {"title": "...", "link": "..."},
#     {"title": "...", "link": "..."},
# ]
# ```
#
# `stories[0]["title"]` means: first item, then its `"title"` value.
#
# ## pandas and CSV
#
# `pd.DataFrame(list_of_dicts)` builds a table. The dictionary keys become column names. `df.to_csv(...)` writes it to a file.
#
# ## Relative links
#
# `urljoin(base, link)` turns relative links into full ones. Full links stay unchanged.

# %%
print(urljoin("https://news.ycombinator.com/", "item?id=123"))
print(urljoin("https://news.ycombinator.com/", "https://example.com/post"))

# %%
stories = []
for story in story_links:
    stories.append({
        "title": story.text,
        "link": urljoin(url, story["href"]),
    })

df = pd.DataFrame(stories)
df.to_csv("stories.csv", index=False, encoding="utf-8")

print(len(df), "stories saved")
df.head()

# %% [markdown]
# - `index=False` stops pandas from writing the 0, 1, 2... row numbers as an extra column.
# - `encoding="utf-8"` makes sure non-English characters are saved correctly.
#
# ### Try it
#
# Print `stories[0]["title"]` and explain what each part (`[0]` and `["title"]`) does.

# %% [markdown]
# # 6. Pagination
#
# Most sites split data over many pages. The page number is usually **hidden in the URL**. On Hacker News, click "More" and the address becomes `?p=2`, then `?p=3`.
#
# ## Three tools
#
# - `range(1, 4)` gives `1, 2, 3` (the end number is **not** included).
# - An **f-string** puts a variable inside a URL: `f"https://site.com/?p={page}"`.
# - A **function** wraps code so you can reuse it.
#
# ## The function rule: one function, one job
#
# `scrape_page(page_no)` should only **scrape one page and `return` the result**. Saving to CSV and printing belong **outside** the function, once, after the loop.
#
# | | `print` | `return` |
# |---|---|---|
# | Purpose | shows text on screen | hands a value back to the caller |
# | Usable in code afterwards? | no | yes |
#
# ### Mistakes that cost time
#
# - Creating the results list **outside** the function so it keeps growing across calls.
# - Writing the CSV **inside** the function so it is rewritten on every page.
# - Calling `scrape_page(i)` but not saving what it returns.
# - Writing `return print("error")`: `print` returns `None`, so the loop later crashes with `'NoneType' object is not iterable`.

# %%
BASE = "https://news.ycombinator.com/"


def scrape_page(page_no):
    """Scrape one Hacker News page and return a list of dicts."""
    stories = []
    response = requests.get(f"{BASE}?p={page_no}", timeout=10)
    page_soup = bs(response.text, "html.parser")

    for story in page_soup.select("span.titleline > a"):
        stories.append({"title": story.text, "link": urljoin(BASE, story["href"])})

    return stories


all_stories = []
for page_no in range(1, 4):          # pages 1, 2, 3
    if page_no > 1:
        time.sleep(2)                # explained in section 7
    all_stories += scrape_page(page_no)

df = pd.DataFrame(all_stories)
df.to_csv("stories_all.csv", index=False, encoding="utf-8")
print(len(df))                       # 3 pages x 30 stories = 90

# %% [markdown]
# ### Try it
#
# 1. What numbers does `range(2, 6)` produce?
# 2. Why is `all_stories += scrape_page(page_no)` correct, but `scrape_page(page_no)` alone is useless?
# 3. Keep the page count small. Every request is real load on a real server.

# %% [markdown]
# # 7. Polite scraping
#
# Your scraper works. Now make it **responsible** and **robust**.
#
# ## 1. `robots.txt`
#
# Every site can publish rules for bots at `site.com/robots.txt`.
#
# | Line | Meaning |
# |---|---|
# | `User-agent: *` | the rules below apply to all bots |
# | `Disallow: /path` | do not fetch this path |
# | `Allow: /path` | this path is fine |
# | `Crawl-delay: 30` | wait 30 seconds between requests |
# | `Sitemap: ...` | the official list of the site's pages |
#
# `robots.txt` is not a law, but it is the site owner's stated wish. Also read the site's **Terms of Service**, which are a separate document.
#
# Python's built-in `urllib.robotparser` does not fully understand the `*` wildcards many sites use, so read the file yourself.

# %%
robots = requests.get("https://news.ycombinator.com/robots.txt", timeout=10)
print(robots.text)

# %% [markdown]
# ## 2. Wait between requests
#
# `time.sleep(seconds)` pauses your program. If the site lists a `Crawl-delay`, use at least that. If it does not, still pick a modest delay (2 to 5 seconds). Without delays, a loop fires requests as fast as your computer can, which can overload small sites and get you blocked.
#
# Only sleep **between** requests. Sleeping after the last page just wastes time.
#
# ## 3. Handle failures
#
# On the real internet, things fail: no connection, site down, page missing. One failed page should not destroy a 100-page job.
#
# - `timeout=10` stops a request from hanging forever.
# - Check `status_code` and skip pages that are not `200`.
# - Wrap the request in `try` / `except`.
#
# ### Where does `requests.exceptions.RequestException` come from?
#
# All `requests` errors inherit from one base class, so one `except` catches them all:
#
# ```
# RequestException        (the parent of all requests errors)
#  ├── ConnectionError    (no internet, site unreachable)
#  ├── Timeout            (the server answered too slowly)
#  └── MissingSchema      (URL has no https://)
# ```
#
# You can verify this yourself with `requests.exceptions.MissingSchema.__mro__`.

# %%
print(requests.exceptions.MissingSchema.__mro__)

# %%
def scrape_page_safe(page_no):
    """Like scrape_page, but never crashes. Returns [] and explains on failure."""
    page_url = f"{BASE}?p={page_no}"

    try:
        response = requests.get(page_url, timeout=10)
    except requests.exceptions.RequestException as error:
        print(f"Page {page_no}: request failed ({type(error).__name__})")
        return []

    if response.status_code != 200:
        print(f"Page {page_no}: HTTP {response.status_code}, skipping")
        return []

    page_soup = bs(response.text, "html.parser")
    return [
        {"title": s.text, "link": urljoin(BASE, s["href"])}
        for s in page_soup.select("span.titleline > a")
    ]


DELAY = 30   # Hacker News lists Crawl-delay: 30. Use 1 only while testing.

all_stories = []
for page_no in range(1, 4):
    if page_no > 1:
        time.sleep(DELAY)
    all_stories += scrape_page_safe(page_no)

print(len(all_stories))

# %% [markdown]
# ### Test that your error handling really works
#
# Break the URL on purpose and confirm the function returns `[]` with a message instead of crashing.

# %%
def broken_request():
    try:
        requests.get("https://news.ycombinatorr.com", timeout=5)   # typo in the domain
        return "worked?!"
    except requests.exceptions.RequestException as error:
        return f"handled: {type(error).__name__}"


print(broken_request())

# %% [markdown]
# ### Try it
#
# 1. Open the `robots.txt` of a site you like. Is there a `Crawl-delay`? Which paths are disallowed?
# 2. Make `scrape_page_safe` print the reason when a page fails (it already does; try triggering a 404).
# 3. In your own words: why is skipping a failed page better than stopping the whole program?

# %% [markdown]
# # 8. Final project: a price tracker
#
# **Goal:** collect product names, prices and links from a Pakistani price-comparison site (PriceOye), save them with a date, and compare each price to the category median.
#
# This is where scraping becomes real: messy data, changing pages, and a few decisions you must make yourself.
#
# ## 8.1 Pre-flight checklist (before writing any scraper)
#
# 1. **Read `robots.txt`.**
# 2. **Check whether the site is static or JavaScript-driven.**
# 3. **Read the Terms of Service.**
# 4. **Plan a polite request schedule.**
#
# ### What PriceOye's `robots.txt` says (at the time of writing)
#
# The file has two parts:
#
# 1. A very long list of **named bots and downloaders**, each blocked with `Disallow: /` (for example `Wget`, `HTTrack`, `SemrushBot`). A normal `python-requests` client is not named there, but the list shows the site is careful about automation.
# 2. The general rules under `User-agent: *`:
#
# ```
# Disallow: *?                    any URL containing a query string is disallowed...
# Disallow: *&
# Disallow: /account/
# Disallow: /orders
# Disallow: /administrateur/
# Allow: /
# Allow: *?page=                  ...except pagination
# Allow: *?source=ppc
# Sitemap: https://priceoye.pk/sitemap/sitemap-index.xml
# ```
#
# What that means for us:
#
# - Plain category pages (like `/wireless-earbuds`) are allowed.
# - Pagination as `?page=N` is allowed. `*` is a wildcard, so this covers any page number, not just one.
# - Filter and sort URLs (extra `?brand=...`, `&sort=...`) are **not** allowed. Keep pagination to exactly `?page=N`.
# - No `Crawl-delay` is listed, so we choose a modest delay ourselves.
# - Always re-read `robots.txt` before running a scraper; it can change.
#
# ### Static or JavaScript?
#
# In the browser press **Ctrl+U** (View Source, not Inspect) and search for a price.
#
# - **Price is in the source:** the site is static, so `requests` + BeautifulSoup is enough.
# - **Price is only visible in Inspect:** JavaScript builds the page after loading. You need a browser-automation tool (Selenium, Playwright) or the site's own API.
#
# PriceOye's category pages put prices in the HTML source, so `requests` works.

# %% [markdown]
# ## 8.2 First attempt: two parallel lists
#
# The quick approach selects all titles, all prices, and joins them with `zip`:
#
# ```python
# titles = soup.select("h4.p-title")[:10]
# prices = soup.select("div.price-box > span")
# for index, (title, price) in enumerate(zip(titles, prices), start=1):
#     print(index, title.text, ":", price.text)
# ```
#
# Output at the time of writing:
#
# ```
# 1  Ldnio T13 Wireless TWS Earbuds : Rs3,599
# 2  Kisonli F2 TWS Wireless Earbuds : Rs3,149
# 3  Audionic Hammer 110 Ultra On-Ear Headphone : Rs6,749
# ...
# ```
#
# It works, but it is **fragile**. `zip` pairs items by position. If one product has two price tags (old price and sale price) or none (out of stock), the prices list shifts, and **every later product silently gets the wrong product's price**. No error appears, the data is just wrong.
#
# ## 8.3 Better: one card at a time
#
# Select **each product's card first**, then read the title and price **inside that card**. Values can never be mixed up between products, and a missing price shows up as `None` for that product only.
#
# We do not need to know the card's class name. Starting from a title tag, we walk **up** the tree while the parent still contains exactly one title. The last such tag is the product's own card.
#
# If you prefer, Inspect the page, find the card's class, and replace `find_card` with a direct `soup.select("div.your-card-class")`.
#
# > Selectors such as `h4.p-title` and `div.price-box > span` were found with Inspect and describe the site's HTML at the time of writing. Sites change their markup. If your scraper suddenly returns nothing, re-inspect the page first.

# %%
def clean_price(text):
    """'Rs3,599' -> 3599. Returns None when there is no number."""
    digits = re.sub(r"[^\d]", "", text or "")
    return int(digits) if digits else None


def find_card(title_tag):
    """Walk up from a title until the next parent would contain more than one title."""
    card = title_tag
    while card.parent is not None and len(card.parent.select("h4.p-title")) == 1:
        card = card.parent
    return card


def parse_products(html, base_url):
    """Extract title, price and link for every product in one page of HTML."""
    page_soup = bs(html, "html.parser")
    products = []

    for title_tag in page_soup.select("h4.p-title"):
        card = find_card(title_tag)
        price_tag = card.select_one("div.price-box > span")
        link_tag = card.select_one("a[href]")

        products.append({
            "title": title_tag.get_text(strip=True),
            "price": clean_price(price_tag.get_text()) if price_tag else None,
            "link": urljoin(base_url, link_tag["href"]) if link_tag else None,
        })

    return products


# Quick checks of the helper functions
print(clean_price("Rs3,599"), clean_price("Rs 75,399"), clean_price(""), clean_price(None))

# %% [markdown]
# ### Why numbers, not strings?
#
# `"Rs3,599"` is text, so you cannot sort it, average it, or compare it correctly (as text, `"Rs9,000"` is bigger than `"Rs10,000"`). Convert to an `int` once, early, and everything downstream (sorting, median, charts) just works.
#
# `select_one` returns `None` when nothing matches, and calling `.text` on `None` raises `AttributeError`. That is why the code checks `if price_tag` first.
#
# ## 8.4 Fetch pages politely
#
# The fetch function reuses everything from section 7: timeout, status check, `try` / `except`. Pagination uses only `?page=N`, which `robots.txt` allows.

# %%
PRICEOYE_URL = "https://priceoye.pk/wireless-earbuds"
PRICE_DELAY = 5   # seconds between requests; PriceOye lists no Crawl-delay


def fetch_html(page_url):
    try:
        response = requests.get(page_url, timeout=10)
    except requests.exceptions.RequestException as error:
        print(f"Request failed: {type(error).__name__}")
        return None

    if response.status_code != 200:
        print(f"HTTP {response.status_code} for {page_url}, skipping")
        return None

    return response.text


def scrape_category(category_url, pages=2):
    """Scrape the first `pages` pages of a category. Returns a DataFrame."""
    rows = []

    for page_no in range(1, pages + 1):
        if page_no > 1:
            time.sleep(PRICE_DELAY)

        page_url = category_url if page_no == 1 else f"{category_url}?page={page_no}"
        html = fetch_html(page_url)
        if html is None:
            continue                       # skip a failed page, keep going

        rows += parse_products(html, category_url)

    df = pd.DataFrame(rows)
    df["date"] = date.today().isoformat()
    return df


df = scrape_category(PRICEOYE_URL, pages=2)
print(len(df), "products")
df.head(10)

# %% [markdown]
# ## 8.5 Save with a date (this makes it a tracker)
#
# A *detector* needs **history**. Overwriting the CSV each run throws the history away. Instead **append** new rows with the date, and write the header only when the file is first created.
#
# Running the scraper twice on the same day adds duplicate rows. Drop them when analysing (`drop_duplicates`).

# %%
def append_to_csv(frame, path="prices.csv"):
    """Append rows to a CSV, writing the header only if the file does not exist yet."""
    frame.to_csv(
        path,
        mode="a",
        header=not os.path.exists(path),
        index=False,
        encoding="utf-8",
    )


append_to_csv(df)
history = pd.read_csv("prices.csv").drop_duplicates(subset=["link", "date"])
print(len(history), "rows in history")

# %% [markdown]
# ## 8.6 Is the price fair? A first answer
#
# A simple starting point: compare every price with the **median** price of the category. The median is better than the average because one very expensive item does not drag it upward.
#
# Limits to keep in mind:
#
# - A category page mixes different kinds of products (earbuds and over-ear headphones, cheap and premium). Comparing a Rs75,000 headset with Rs3,000 earbuds is not meaningful.
# - Better later: track **the same product's price over time** using its `link` as an ID, and compare today's price with its own history.

# %%
priced = df.dropna(subset=["price"]).copy()
median_price = priced["price"].median()

priced["vs_median_%"] = ((priced["price"] / median_price - 1) * 100).round(1)

print("Median price: Rs", int(median_price))
priced.sort_values("vs_median_%")[["title", "price", "vs_median_%"]].head(10)

# %% [markdown]
# ### Try it
#
# 1. Run `scrape_category` for pages 1 to 2 only (keep it small) and save the result.
# 2. Run it again tomorrow. Does any product's price change? Use `link` to compare.
# 3. Add a column that flags products priced more than 20% below the median.
# 4. Pick a second category page on the same site. Re-read `robots.txt` first.
#
# ### Ideas to extend the project
#
# - Store history in SQLite instead of CSV.
# - Plot a product's price over time with matplotlib.
# - Schedule the script once per day (Task Scheduler on Windows, cron on Linux/macOS).
# - Add an alert when a tracked product drops below a target price.

# %% [markdown]
# # 9. Cheat sheet
#
# ## The whole workflow in nine lines
#
# ```python
# import requests
# from bs4 import BeautifulSoup as bs
#
# response = requests.get(url, timeout=10)              # 1. fetch
# if response.status_code == 200:                       # 2. check
#     soup = bs(response.text, "html.parser")           # 3. parse
#     for tag in soup.select("css.selector"):           # 4. select
#         print(tag.get_text(strip=True), tag.get("href"))   # 5. extract
# ```
#
# ## Methods at a glance
#
# | Task | Code |
# |---|---|
# | Fetch a page | `requests.get(url, timeout=10)` |
# | HTML to tree | `bs(html, "html.parser")` |
# | First match / all matches | `soup.find(...)` / `soup.find_all(...)` |
# | CSS selector, first / all | `soup.select_one(...)` / `soup.select(...)` |
# | Text of a tag | `tag.get_text(strip=True)` |
# | Attribute of a tag | `tag.get("href")` |
# | Join relative link | `urljoin(base, link)` |
# | Wait | `time.sleep(seconds)` |
# | Save table | `df.to_csv(path, index=False, encoding="utf-8")` |
#
# ## Common mistakes and what they mean
#
# | Symptom | Cause | Fix |
# |---|---|---|
# | `MissingSchema` | URL has no `https://` | add the scheme |
# | `FeatureNotFound: html-parser` | typo in the parser name | use `"html.parser"` |
# | `'list' object has no attribute 'text'` | `.text` on the result of `find_all` / `select` | loop over the list |
# | `'NoneType' object has no attribute 'text'` | `find` / `select_one` found nothing | check for `None` first |
# | `'NoneType' object is not iterable` | function returned `None` (for example `return print(...)`) | return `[]` |
# | Prices attached to wrong products | two parallel lists joined with `zip` | select the product card first |
# | CSV overwritten every page | saving inside the page function | save once, after the loop |
# | Empty results from a normal-looking page | JavaScript builds the page | View Source test; use Playwright |
# | Status 403 or 429 | blocked or rate limited | slow down, check the rules, stop if asked |
# | Selector returns nothing today | the site changed its HTML | re-inspect the page |
#
# ## When `requests` is not enough
#
# - **JavaScript-rendered pages:** Selenium or Playwright drive a real browser.
# - **Sites with an API:** if the page loads its data from a JSON endpoint (visible in the browser's Network tab) and the terms allow it, use that instead of scraping HTML.
# - **Large crawls:** look at the Scrapy framework.
#
# ## Responsible scraping checklist
#
# - [ ] I read `robots.txt` and the Terms of Service.
# - [ ] My request rate is low, with a delay and a timeout.
# - [ ] I only fetch pages the rules allow (no logins, accounts or private data).
# - [ ] I handle errors and stop if the site asks me to.
# - [ ] I do not republish scraped data without checking the site's terms.
