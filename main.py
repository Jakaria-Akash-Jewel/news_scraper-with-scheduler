import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import schedule
import time

def get_headlines():
    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://edition.cnn.com/world"
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    headlines = []

    for tag in soup.find_all("a"):
        title = tag.get_text(strip=True)
        link = tag.get("href")
        if title and link and "/202" in link:
            full_link = f"https://edition.cnn.com{link}" if link.startswith("/") else link
            if (title, full_link) not in headlines:
                headlines.append((title, full_link))

    return headlines

def save_headlines_to_csv(headlines):
    date = datetime.now().strftime('%Y-%m-%d_%H-%M')
    filename = f"cnn_headlines_{date}.csv"

    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Headline', 'URL'])
        for title, link in headlines:
            writer.writerow([title, link])

    print(f"✅ {len(headlines)} headlines saved to '{filename}'")

def job():
    print(f"\n🕒 Running scheduled job at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    headlines = get_headlines()
    save_headlines_to_csv(headlines)

if __name__ == '__main__':
    schedule.every(1).hour.do(job)  # Run every hour

    print("📅 Scheduler started. Running every 1 hour...\nPress Ctrl+C to stop.\n")
    while True:
        schedule.run_pending()
        time.sleep(60)
