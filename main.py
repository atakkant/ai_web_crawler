from crawl4ai import AsyncWebCrawler
import asyncio
import csv
import time
import os

from models.repo import Repo, Tag
from groq import Groq



from config import URL_CSS_SELECTOR, URLS, CSS_SELECTOR, REQUIRED_KEYS_REPOS, REQUIRED_KEYS_TAGS, TAGS
from utils.scraper_utils import fetch_and_process_page, fetch_tags, get_browser_config, get_llm_strategy

async def crawl_tags():
    browser_config = get_browser_config()
    instructions = (
            "Extract all repo links concatenating with the base url: 'https://github.com'"
        )
    llm_strategy = get_llm_strategy(Tag,instructions)
    session_id = "tags_crawl_session"

    all_urls = []
    seen_urls = set()
    async with AsyncWebCrawler(config=browser_config) as crawler:
        for tag in TAGS:
            urls, no_results_found = await fetch_tags(
                crawler, 
                tag,
                URL_CSS_SELECTOR,
                llm_strategy,
                session_id,
                REQUIRED_KEYS_TAGS,
                seen_urls
            )
            if no_results_found:
                print("No more results")
                break
            else:
                all_urls.extend(urls)
        if all_urls:
            with open('tags.csv', mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=REQUIRED_KEYS_TAGS)
                writer.writeheader()
                writer.writerows(all_urls)

async def crawl_repos():
    browser_config = get_browser_config()
    instructions = (
            "Extract all repo objects with 'name', 'description', 'url'"
        )
    llm_strategy = get_llm_strategy(Repo,instructions)    
    session_id = "repo_crawl_session"

    all_repos = []
    seen_names = set()

    with open('tags.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            URLS.append(row['url'])

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for url in URLS:
            repos, no_results_found = await fetch_and_process_page(
                crawler, 
                url,
                CSS_SELECTOR,
                llm_strategy,
                session_id,
                REQUIRED_KEYS_REPOS,
                seen_names
            )
            if no_results_found:
                print("No more results found. Exiting...")
                break
            else:
                all_repos.extend(repos)
        if all_repos:
            with open('allrepos.csv', mode='a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=REQUIRED_KEYS_REPOS)
                writer.writeheader()
                writer.writerows(all_repos)
        time.sleep(10)

async def analyse_repos():
    all_repos = []
    with open('repos.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            all_repos.append((row['name'], row['description']))
    
    client = Groq(
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Group these repos based on their description: {str(all_repos)}",
            }
        ],
        model="llama3-8b-8192",
    )
    print(chat_completion.choices[0].message.content)


async def main():
    await crawl_tags()
    await crawl_repos()
    await analyse_repos()

if __name__ == "__main__":
    asyncio.run(main())