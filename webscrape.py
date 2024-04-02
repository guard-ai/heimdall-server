from bs4 import BeautifulSoup
import requests

URL = "https://www.broadcastify.com/listen/top" # change to scrape from different feed list
TOP = set()

response = requests.get(URL)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.find_all("a")
    
    with open("top50.txt", "w") as f:
        for link in links:
            href = link.get("href")
            if href and href.startswith("/listen/feed"):
                # remove duplicates
                TOP.add(href)

        for link in TOP:
            f.write("https://www.broadcastify.com"+link + "\n")
else:
    print("Failed to fetch HTML page. Status code:", response.status_code)
