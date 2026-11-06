import csv
from datetime import datetime
import time
from bs4 import BeautifulSoup
import requests

csv_filename = "stockgumshoe_latest_articles.csv"

def get_past_12_months():
    """Generates a list of (year, month) tuples for the past 12 months, chronologically."""
    current_date = datetime.now()
    months = []
    for i in range(12):
        y = current_date.year
        m = current_date.month - i
        while m <= 0:
            m += 12
            y -= 1
        months.append((y, m))
    # Reverse so it scrapes from oldest to newest
    months.reverse()
    return months

def scrape_stockgumshoe_latest():
    all_articles = []

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    target_months = get_past_12_months()
    print("Starting dynamic scrape for Stock Gumshoe (past 12 months archive)...")

    for year, month in target_months:
        month_str = f"{month:02d}"
        page = 1

        while True:
            if page == 1:
                url = f"https://www.stockgumshoe.com/{year}/{month_str}/"
            else:
                url = f"https://www.stockgumshoe.com/{year}/{month_str}/page/{page}/"

            print(f"Fetching: {url}")

            try:
                response = requests.get(url, headers=headers, timeout=10)

                if response.status_code == 404:
                    break
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")
                article_items = soup.select("li.article")

                if not article_items:
                    print(f"  -> No articles found on page {page} for {year}-{month_str}.")
                    break

                articles_found = False
                for item in article_items:
                    title_link = item.select_one("h2 a")
                    date_meta = item.select_one(".article-meta")

                    if title_link:
                        title = title_link.get_text(strip=True)
                        link = title_link.get("href")
                        date_str = date_meta.get_text(strip=True) if date_meta else ""

                        if title and link:
                            all_articles.append({
                                "Year": year,
                                "Month": month_str,
                                "DateText": date_str,
                                "Title": title,
                                "URL": link
                            })
                            articles_found = True

                # Check for next page pagination
                next_page = soup.select_one("a.next.page-numbers, .pagination .next")
                if not next_page or not articles_found:
                    break

                page += 1
                time.sleep(1)

            except requests.exceptions.RequestException as e:
                print(f"  -> Error fetching {url}: {e}")
                break

    # Save to CSV
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as csv_file:
        fieldnames = ["Year", "Month", "DateText", "Title", "URL"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for article in all_articles:
            writer.writerow(article)

    print(
        f"\nScraping complete! Found {len(all_articles)} articles. Saved to {csv_filename}"
    )

if __name__ == "__main__":
    scrape_stockgumshoe_latest()