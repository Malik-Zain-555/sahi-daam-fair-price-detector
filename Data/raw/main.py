# %% 0: Import Libraries
import requests as re
from bs4 import BeautifulSoup as bs

# DHA_Url = "https://www.zameen.com/Rentals_Houses_Property/Islamabad_DHA_Defence-3188-1.html"
#
# html = re.get(DHA_Url)
# soup = bs(html.text, "html.parser")
#
# # %% 2: Load Data
#
# areas = soup.select("h2._36dfb99f")[:20]
# prices = soup.select("div._2923a568 > span.dc381b54")[:20]
# for index, (area, price) in enumerate(zip(areas, prices), start=1):
#     print(index, area.text, price.text)
# # %% 3: Save Data
#
# import pandas as pd
#
# clean_areas = [a.text.strip() for a in areas]
# clean_prices = [p.text.strip() for p in prices]
#
# df = pd.DataFrame({"area": clean_areas, "Price": clean_prices})
# df.head()
# # %% 4: Submitting in the File
#
# df.to_csv("data.csv", index=False, encoding="utf-8")
# print("File created!")

# # %% 5: Listing Cities
#
# soup.select("div.d7c48502 span._569dbe30")
#
# # %% 6: t1
#
# link = "https://www.zameen.com/all_locations/Islamabad-3-1-9.html"
# html_I = re.get(link)
# sop = bs(html_I.text, "html.parser")

# %% 7: t2

# areas = sop.select("div.layout-grid_layoutGrid__htd53 span")[:501]
# links = sop.select("div.layout-grid_layoutGrid__htd53 a")[:501]
# for index, (area, link) in enumerate(zip(areas, links), start=1):
#     clean_areas = [a.text.strip() for a in areas]
#     clean_links = [l.get("href", "").strip() for l in links]

# df = pd.DataFrame({"areas": clean_areas, "links": clean_links})
# df.to_csv("ISB_areas.csv", index=False, encoding="utf-8")
# print("File Created!")

# %% 8: House Card Details

import pandas as pd
import time

combined_rows = []

def area_scrapper(name):
    rows = []
    page_no = 1
    while True:
        # print(f"Scarping Page No.{page_no}")
        link = f"https://www.zameen.com/Houses_Property/Islamabad_{name}-{page_no}.html"
        html = re.get(link)
        soup = bs(html. text, "html.parser")

        houses_card = soup.select("ul.e20beb46 li.a37d52f0")

        if not houses_card:
            print("No more houses found. Finished scraping!")
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

        combined_rows.extend(rows)

        next_button = soup.select_one('[title="Next"]')
        if not next_button:
            print("Reached the final Page. Stopping...")
            break

        page_no += 1
        time.sleep(1)

    print(f"{name} File Created!")

# %% 9: Getting All Area Data

area_links = []

link_ISB = "https://www.zameen.com/all_locations/Islamabad-3-1-9.html"
html_ISB = re.get(link_ISB)
soup_ISB = bs(html_ISB.text, "html.parser")
links = soup_ISB.select("div.layout-grid_layoutGrid__htd53 a")[:501]
for link in links:
    clean_links = link.get("href", "").strip()
    area_links.append(clean_links)

ISB_areas = [area_link.split("/Islamabad_")[-1].split("-1.html")[0] for area_link in area_links]

for areas_name in ISB_areas:
    area_scrapper(name=areas_name)

df = pd.DataFrame(combined_rows)
df.to_csv("ISB_areas.csv", index=False, encoding="utf-8")
