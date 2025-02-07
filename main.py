from crawl4ai import AsyncWebCrawler
import asyncio
import csv

from config import BASE_URL, CSS_SELECTOR, REQUIRED_KEYS
from utils.scraper_utils import fetch_and_process_page, get_browser_config, get_llm_strategy


async def crawl_venues():
    browser_config = get_browser_config()
    llm_strategy = get_llm_strategy()
    session_id = "venue_crawl_session"

    page_num = 1
    all_venues = []
    seen_names = set()

    async with AsyncWebCrawler(config=browser_config) as crawler:
        while True:
            venues, no_results_found = await fetch_and_process_page(
                crawler, 
                page_num, 
                BASE_URL,
                CSS_SELECTOR,
                llm_strategy,
                session_id,
                REQUIRED_KEYS,
                seen_names
            )
            page_num += 1
            if no_results_found:
                print("No more results found. Exiting...")
                break
            else:
                all_venues.extend(venues)
        if all_venues:
            with open('venues.csv', mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=REQUIRED_KEYS)
                writer.writeheader()
                writer.writerows(all_venues)

async def main():
    await crawl_venues()

if __name__ == "__main__":
    asyncio.run(main())