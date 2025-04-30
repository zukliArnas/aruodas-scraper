from playwright.sync_api import sync_playwright
import time
import requests
from bs4 import BeautifulSoup
import json
import random



web = "https://www.aruodas.lt/"
city = "Vilnius"
object_type = "Butai pardavimui"

all_listing_urls = []

BASE_URL = "https://www.aruodas.lt"
START_URL = "https://www.aruodas.lt/butai/vilniuje/"

def get_page_urls(page_number):
    url = START_URL + f"?FPage={page_number}"
    print(f"Fetching: {url}")
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, 'html.parser')

    listings = soup.select("a.list-item")
    urls = [BASE_URL + item.get("href") for item in listings if item.get("href")]
    return urls

def collect_all_urls(max_pages=10):
    for page in range(1, max_pages + 1):
        try:
            urls = get_page_urls(page)
            if not urls:
                print("No more listings found. Stopping.")
                break
            all_listing_urls.extend(urls)
            time.sleep(random.uniform(1, 3))
        except Exception as e:
            print(f"Error on page {page}: {e}")
            continue
    return all_listing_urls

def parse_flat_details(url):
    print(f"Scraping details from: {url}")
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    def safe_text(selector):
        el = soup.select_one(selector)
        return el.get_text(strip=True) if el else None

    return {
        "url": url,
        "title": safe_text("h1"),
        "price": safe_text(".price"),
        "location": safe_text(".obj-header .address"),
        "rooms": safe_text(".obj-details > dd:contains('Kamb.')"),
        "area": safe_text(".obj-details > dd:contains('Plotas')"),
        "description": safe_text(".obj-description p"),
    }


def collect_listing_urls(source=web):

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(web)

        # Give the parameters for searching
        page.click("[id='display_FRegion']")
        page.click("label[for='input_FRegion_461']")
        print("Clicked on Region - Vilnius")


        page.click('[id="buttonSearchForm"]')
        print("Click to search")

        raw_count_text = page.locator("div.mark-wrapper div.number").inner_text()
        print(raw_count_text)
        time.sleep(5)

        page.wait_for_selector("div.list-photo-v2 a")
        print("📄 Listings loaded")

        elements = page.locator("div.list-photo-v2 a").all()
        flat_links = [el.get_attribute("href") for el in elements if el.get_attribute("href")]
        full_urls = [BASE_URL + link for link in flat_links]
        return full_urls

def get_listing_urls(base_url, max_pages=100):
    """Scrape listing URLs from paginated search results"""
    all_listing_urls = set()

    for page in range(1, max_pages + 1):
        print(f"🔄 Processing page {page}...")
        page_url = f"{base_url}?FPage={page}"
        response = requests.get(page_url)
        if response.status_code != 200:
            print(f"⚠️ Failed to fetch page {page}")
            break

        soup = BeautifulSoup(response.content, 'html.parser')
        listings = soup.select("a.list-item")  # Confirm this CSS selector works

        if not listings:
            print("🚫 No listings found. Ending.")
            break

        for item in listings:
            href = item.get("href")
            if href and href.startswith("/"):
                full_url = "https://www.aruodas.lt" + href
                all_listing_urls.add(full_url)

        time.sleep(1)  # Respectful scraping

    print(f"✅ Collected {len(all_listing_urls)} unique listing URLs.")
    return list(all_listing_urls)


def main():
    base_url = "https://www.aruodas.lt/butai/vilniuje/"
    listing_urls = get_listing_urls(base_url, max_pages=120)    
    print(f"Collected {len(listing_urls)} URLs.")
    results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(parse_flat_details, url): url for url in listing_urls}
        for future in as_completed(future_to_url):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"Failed scraping {future_to_url[future]}: {e}")

    with open("aruodas_flats.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("Done! 🎉 Data saved to aruodas_flats.json")


if __name__ == "__main__":
    start_time = time.time()
    main()
    total_time = time.time() - start_time
    print(total_time)