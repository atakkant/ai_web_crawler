import json
from typing import List, Set, Tuple
from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig, LLMExtractionStrategy
import os
from utils.data_utils import is_complete_repo

def get_browser_config():
    return BrowserConfig(
        browser_type="chromium",
        headless=False,
        verbose=True
    )

def get_llm_strategy(data_model, instructions):
    return LLMExtractionStrategy(
        provider="groq/deepseek-r1-distill-llama-70b",
        api_token=os.getenv("GROQ_API_KEY"),
        schema=data_model.model_json_schema(),
        extraction_type="schema",
        instruction=instructions,
        input_format="markdown",
        verbose=True
    )

async def check_no_results(crawler: AsyncWebCrawler, url: str, session_id: str) -> bool:
    result = await crawler.arun(
        url=url,
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            session_id=session_id
        ),
    )

    if result.success:
        if "no results found" in result.cleaned_html.lower():
            return True
    else:
        print(f"Failed to load page: {url} - {result.error_message}")
        return False

async def fetch_and_process_page(
    crawler: AsyncWebCrawler,
    base_url: str,
    css_selector: str,
    llm_strategy: LLMExtractionStrategy,
    session_id: str,
    required_keys: List[str],
    seen_names: Set[str]
) -> Tuple[List[dict], bool]:
    url = f"{base_url}"
    print(f"Loading page: {url}")
    
    no_results = await check_no_results(crawler, url, session_id)
    if no_results:
        return [], True

    result = await crawler.arun(
        url=url,
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=llm_strategy,
            css_selector=css_selector,
            session_id=session_id
        )
    )

    if not (result.success and result.extracted_content):
        print(f"Failed to load page: {url} - {result.error_message}")
        return [], False
    
    extracted_data = json.loads(result.extracted_content)

    if not extracted_data:
        print(f"No data extracted from page: {url}")
        return [], False
    
    print("length of Extracted data:", len(extracted_data))
    complete_repos = []
    for data in extracted_data:
        if data.get("error"):
            print(f"Error processing venue: {data['error']}")
            continue
        else:
            data['url'] = base_url
            completed_data = is_complete_repo(data, required_keys)
            complete_repos.append(completed_data)
            seen_names.add(data["name"])
    
    return complete_repos, False

async def fetch_tags(
    crawler: AsyncWebCrawler,
    tag: str,
    css_selector: str,
    llm_strategy: LLMExtractionStrategy,
    session_id: str,
    required_keys: List[str],
    seen_names: Set[str]
) -> Tuple[List[dict], bool]:
    url = f"http://github.com/topics/{tag}"
    print(f"Loading page: {url}")
    
    no_results = await check_no_results(crawler, url, session_id)
    if no_results:
        return [], True

    result = await crawler.arun(
        url=url,
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=llm_strategy,
            css_selector=css_selector,
            session_id=session_id
        )
    )

    if not (result.success and result.extracted_content):
        print(f"Failed to load page: {url} - {result.error_message}")
        return [], False
    
    extracted_data = json.loads(result.extracted_content)

    if not extracted_data:
        print(f"No data extracted from page: {url}")
        return [], False
    
    print("length of Extracted data:", len(extracted_data))
    complete_repos = []
    for data in extracted_data:
        if data.get("error"):
            print(f"Error processing venue: {data['error']}")
            continue
        else:
            data['tag'] = tag
            completed_data = is_complete_repo(data, required_keys)
            complete_repos.append(completed_data)
            seen_names.add(data["url"])
    
    return complete_repos, False