# %% 0: Imports & Setup

import requests as re
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

OUT_FILE = "ISB_areas.csv"
DONE_FILE = "done_areas.txt"
lock = Lock()


# %% 1: Helper - Fetch Page With Retries

def get_page(session, link, retries=5):
    for attempt in range(retries):
        try:
            return session.get(link, timeout=20)
        except re.exceptions.RequestException as e:
            wait = 2 * (2 ** attempt)
            print(f"{type(e).__name__} on {link} | retry {attempt + 1}/{retries} in {wait}s")
            time.sleep(wait)
    return None


# %% 2: Scrape One Area (All Pages) & Save To CSV

def area_scrapper(name):
    rows = []
    page_no = 1
    session = re.Session()
    session.headers.update(headers)

    while True:
        link = f"https://www.zameen.com/Houses_Property/Islamabad_{name}-{page_no}.html"
        html = get_page(session, link)

        if html is None:
            print(f"{name}: failed after retries, skipping (will retry on next run)")
            return  # not marked as done, so the next run picks it up again

        soup = bs(html.text, "html.parser")

        houses_card = soup.select("ul.e20beb46 li.a37d52f0")

        if not houses_card:
            break

        for hc in houses_card:
            prices = hc.select_one('[aria-label="Price"]')
            prices_text = prices.text.strip() if prices else "N/A"

            locs = hc.select_one('[aria-label="Location"]')
            locs_text = locs.text.strip() if locs else "N/A"

            beds = hc.select_one('[aria-label="Beds"]')
            beds_text = beds.text.strip() if beds else "N/A"

            baths = hc.select_one('[aria-label="Baths"]')
            baths_text = baths.text.strip() if baths else "N/A"

            areas = hc.select_one('[aria-label="Area"]')
            areas_text = areas.text.strip() if areas else "N/A"

            rows.append({
                "location": locs_text,
                "area": areas_text,
                "beds": beds_text,
                "baths": baths_text,
                "price": prices_text,
            })

        next_button = soup.select_one('[title="Next"]')
        if not next_button:
            break

        page_no += 1
        time.sleep(0.5)

    # save this area right away
    with lock:
        if rows:
            pd.DataFrame(rows).to_csv(
                OUT_FILE, mode="a", index=False, encoding="utf-8",
                header=not os.path.exists(OUT_FILE),
            )
        with open(DONE_FILE, "a", encoding="utf-8") as f:
            f.write(name + "\n")
    print(f"{name} done ({len(rows)} houses)")


# %% 3: Get All Islamabad Area Names From Zameen

area_links = []

link_ISB = "https://www.zameen.com/all_locations/Islamabad-3-1-9.html"
html_ISB = re.get(link_ISB, headers=headers, timeout=20)
soup_ISB = bs(html_ISB.text, "html.parser")
links = soup_ISB.select("div.layout-grid_layoutGrid__htd53 a")[:501]
for link in links:
    clean_links = link.get("href", "").strip()
    area_links.append(clean_links)

ISB_areas = [area_link.split("/Islamabad_")[-1].split("-1.html")[0] for area_link in area_links]


# %% 4: Skip Already-Finished Areas (Resume Support)

done = set()
if os.path.exists(DONE_FILE):
    with open(DONE_FILE, encoding="utf-8") as f:
        done = {line.strip() for line in f}

todo = [a for a in ISB_areas if a not in done]
print(f"{len(done)} already done, {len(todo)} to go")


# %% 5: Run The Scraper (5 Areas In Parallel)

with ThreadPoolExecutor(max_workers=5) as executor:
    list(executor.map(area_scrapper, todo))

print("All finished!")
