import requests
from bs4 import BeautifulSoup

url = "https://github.com/trending"

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; LearningScraper/1.0)"
}

response = requests.get(url, headers=headers, timeout=20)

response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

print("Status: ", response.status_code)
print("Page title: ", soup.title.get_text(strip=True))
print("Repository cards: ", len(soup.select("article.Box-row")))
