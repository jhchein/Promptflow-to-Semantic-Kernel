"""
Wikipedia utilities - migrated from get_wiki_url.py
"""

import requests
import bs4
import re
from rich import print


def decode_str(string):
    return string.encode().decode("unicode-escape").encode("latin1").decode("utf-8")


def remove_nested_parentheses(string):
    pattern = r"\([^()]+\)"
    while re.search(pattern, string):
        string = re.sub(pattern, "", string)
    return string


def get_wiki_urls(entity: str, count=2):
    """Get Wikipedia URLs for a given entity"""
    url = f"https://en.wikipedia.org/w/index.php?search={entity}"
    url_list = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        mw_divs = soup.find_all("div", {"class": "mw-search-result-heading"})

        if mw_divs:  # mismatch
            result_titles = [decode_str(div.get_text().strip()) for div in mw_divs]
            result_titles = [
                remove_nested_parentheses(result_title)
                for result_title in result_titles
            ]
            print(
                f"Could not find [blue]{entity}[/blue]. Similar entity: [blue]{result_titles[:count]}[/blue]."
            )
            url_list.extend(
                [
                    f"https://en.wikipedia.org/w/index.php?search={result_title}"
                    for result_title in result_titles
                ]
            )
        else:
            page_content = [
                p_ul.get_text().strip()
                for p_ul in soup.find_all("p") + soup.find_all("ul")
            ]
            if any("may refer to:" in p for p in page_content):
                url_list.extend(get_wiki_urls("[" + entity + "]"))
            else:
                url_list.append(url)
    else:
        print(f"Get url failed with status code {response.status_code}")

    return url_list[:count]
