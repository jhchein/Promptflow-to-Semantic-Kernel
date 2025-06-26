"""
Get Wiki URL Step - Gets Wikipedia URLs for a given entity
"""

from rich import print
from semantic_kernel.functions import kernel_function
from semantic_kernel.processes.kernel_process import KernelProcessStep

from ..utils.wiki_utils import get_wiki_urls


class GetWikiUrlStep(KernelProcessStep):
    """Process step to get Wikipedia URLs for a given entity"""

    @kernel_function
    async def get_urls(self, data: dict, count: int = 2) -> dict:
        """Get Wikipedia URLs for the given entity"""

        extracted_query = data["extracted_query"]

        print(f"Getting Wiki URLs for entity: [blue]{extracted_query}[/blue]")
        url_list = get_wiki_urls(extracted_query, count)
        print(f"Found {len(url_list)} URLs")

        return {
            "question": data["question"],
            "url_list": url_list,
        }
