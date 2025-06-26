"""
Web scraping utilities - migrated from search_result_from_url.py
"""

import requests
import bs4
import time
import random
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from rich import print


def decode_str(string):
    return string.encode().decode("unicode-escape").encode("latin1").decode("utf-8")


def get_page_sentence(page, count: int = 10):
    """Extract first count sentences from page content"""
    paragraphs = page.split("\n")
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    sentences = []
    for p in paragraphs:
        sentences += p.split(". ")
    sentences = [s.strip() + "." for s in sentences if s.strip()]

    return " ".join(sentences[:count])


def fetch_text_content_from_url(url: str, count: int = 10):
    """Fetch text content from a URL"""
    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35"
    }

    delay = random.uniform(0, 0.5)
    time.sleep(delay)

    response = session.get(url, headers=headers)
    if response.status_code == 200:
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        page_content = [
            p_ul.get_text().strip() for p_ul in soup.find_all("p") + soup.find_all("ul")
        ]

        page = ""
        for content in page_content:
            if len(content.split(" ")) > 2:
                page += content + "\n"

        text = get_page_sentence(page, count=count)
        return (url, text)
    else:
        print(f"Get url failed with status code {response.status_code} for URL: {url}")
        return (url, "No available content")


def search_results_from_urls(url_list: list, count: int = 10):
    """Get search results from multiple URLs concurrently"""
    results = []
    partial_func = partial(fetch_text_content_from_url, count=count)

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = executor.map(partial_func, url_list)
        for result in futures:
            results.append(result)

    return results
