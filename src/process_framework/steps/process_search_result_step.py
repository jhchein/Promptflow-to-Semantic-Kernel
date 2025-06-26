"""
Process Search Result Step - Formats search results for the final answer
"""

from rich import print
from semantic_kernel.functions import kernel_function
from semantic_kernel.processes.kernel_process import KernelProcessStep


class ProcessSearchResultStep(KernelProcessStep):
    """Process step to format search results"""

    @kernel_function
    async def process_results(self, data: dict) -> dict:
        """Format search results into context string"""

        def format_doc(doc_tuple):
            url, content = doc_tuple
            return f"Content: {content}\nSource: {url}"

        context_list = []
        for url, content in data["search_results"]:
            context_list.append({"Content": content, "Source": url})

        # ToDo: Aren't we doing this in the previous lines already?
        context_str = "\n\n".join(
            [format_doc((c["Source"], c["Content"])) for c in context_list]
        )

        print(f"Formatted {len(context_list)} search results")

        return {"question": data["question"], "context": context_str}
