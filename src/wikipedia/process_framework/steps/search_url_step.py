"""
Search URL Step - Fetches content from Wikipedia URLs
"""

from rich import print
from semantic_kernel.functions import kernel_function
from semantic_kernel.processes.kernel_process import KernelProcessStep

from ..utils.web_utils import search_results_from_urls


class SearchUrlStep(KernelProcessStep):
    """Process step to fetch content from URLs"""

    @kernel_function
    async def search_urls(self, data: dict, count: int = 10) -> dict:
        """Fetch content from the provided URLs"""

        url_list = data["url_list"]
        print(f"Searching {len(url_list)} URLs for content")
        search_results = search_results_from_urls(url_list, count)
        print(f"Retrieved content from {len(search_results)} URLs")

        return {
            "question": data["question"],
            "search_results": search_results,
        }
