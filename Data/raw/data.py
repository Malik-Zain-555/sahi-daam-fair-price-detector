# %% 0: Import Libraries

import requests as re
from bs4 import BeautifulSoup as bs

DHA_Url = "https://www.zameen.com/Rentals_Houses_Property/Islamabad_DHA_Defence-3188-1.html"

html = re.get(DHA_Url)
soup = bs(html.text, "html.parser")

# %% 2: Load Data

areas = soup.select("h2._36dfb99f")[:20]
prices = soup.select("div._2923a568 > span.dc381b54")[:20]
for index, (area, price) in enumerate(zip(areas, prices), start=1):
    print(index, area.text, price.text)
# %% 3: Save Data

import pandas as pd

clean_areas = [a.text.strip() for a in areas]
clean_prices = [p.text.strip() for p in prices]

df = pd.DataFrame({"area": clean_areas, "Price": clean_prices})
df.head()
# %% 4: Submitting in the File

df.to_csv("data.csv", index="False", encoding="utf-8")
print("File created!")
