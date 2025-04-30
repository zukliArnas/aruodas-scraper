import os
import csv
import json
import time
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

from logger_config import get_logger

logger = get_logger("info.log")


def collect_flat_urls(flat_urls: list[str], element) -> list[str]:
    for el in element:
        href = el.get_attribute("href")
        if href:
            flat_urls.append(href)

    return flat_urls


def accept_cookies(page) -> bool:
    try:
        cookie_button = page.locator('[id="onetrust-reject-all-handler"]')
        if cookie_button.is_visible():
            logger.info("Accepting cookies")
            cookie_button.click()
            time.sleep(1)
            return True
    except Exception as e:
        logger.error(f"Cookie acceptance failed or no needed - {e}")
    return False


def get_total_pages(page) -> int:
    page.wait_for_selector(".pagination")
    pagination_elements = page.locator(".pagination a.page-bt").all()
    page_numbers = []
    for el in pagination_elements:
        text = el.inner_text().strip()
        if text.isdigit():
            page_numbers.append(int(text))
    max_page = max(page_numbers) if page_numbers else 1
    logger.info(f"Total pages: {max_page}")
    return max_page


def scrape_page(page, page_number: int, start_url: str) -> list[str]:
    url = start_url if page_number == 1 else urljoin(start_url, f"puslapis/{page_number}/")
    logger.info(f"Navigating to page {page_number}: {url}")
    page.goto(url)
    page.wait_for_selector("div.list-photo-v2 a")
    elements = page.locator("div.list-photo-v2 a").all()
    flat_links = collect_flat_urls([], elements)
    return flat_links


def scrape_flat_page(url) -> dict:
    flat_data = {
        "url": url,
        "price": None,
        "address": None,
        "rooms": None,
        "size": None,
        "year_built": None
    }

    try:
        with sync_playwright() as p:
            headless_mode = os.getenv("HEADLESS", "true").lower() == "true"
            browser = p.chromium.launch(headless=headless_mode)
            page = browser.new_page()
            page.goto(url, timeout=15000)
            page.wait_for_selector("dl.obj-details", timeout=5000)

            accept_cookies(page)

            soup = BeautifulSoup(page.content(), "html.parser")

            price_tag = soup.find("span", class_ = "price-eur")
            if price_tag:
                flat_data["price"] = price_tag.get_text(strip=True)

            address_tag = soup.find("span", class_ = "obj-header-text")
            if address_tag:
                flat_data["address"] = address_tag.get_text(strip=True)

            details = soup.select("dl.obj-details dd")
            labels = soup.select("dl.obj-details dt")

            for label, detail in zip(labels, details):
                label_text = label.get_text(strip=True)
                detail_text = detail.get_text(strip=True)    

                if "Kambarių sk." in label_text:
                    flat_data["rooms"] = detail_text
                elif "Plotas" in label_text:
                    flat_data["size"] = detail_text
                elif "Statybos metai" in label_text:
                    flat_data["year_built"] = detail_text

            browser.close()
    except Exception as e:
        logger.error(f"Error occured while scraping flat page {url}: {e}")

    return flat_data


def save_listing_csv(listing: dict, filename: str = 'flats.csv') -> None:
    file_exists = os.path.isfile(filename)

    with open(filename, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=listing.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(listing)


def get_existing_urls(filename: str = 'flats.csv') -> set:
    if not os.path.isfile(filename):
        return set()
    with open(filename, newline='', encoding='utf-8') as f:
        return set(row['url'] for row in csv.DictReader(f))


def save_listing_json(listing: dict, filename: str = 'flats.json') -> None:
    data = []

    if os.path.isfile(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

    if listing['url'] not in [entry['url'] for entry in data]:
        data.append(listing)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def save_if_new(listing: dict) -> None:
    existing_urls = get_existing_urls()
    if listing['url'] not in existing_urls:
        save_listing_csv(listing)
        save_listing_json(listing)
