"""
Chat with Wikipedia Process - Main implementation
"""

import asyncio
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from rich import print
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.processes import ProcessBuilder
from semantic_kernel.processes.kernel_process import KernelProcess, KernelProcessEvent
from semantic_kernel.processes.local_runtime.local_kernel_process import start

from .steps.augmented_chat_step import AugmentedChatStep
from .steps.extract_query_step import ExtractQueryStep
from .steps.get_wiki_url_step import GetWikiUrlStep
from .steps.process_search_result_step import ProcessSearchResultStep
from .steps.search_url_step import SearchUrlStep
from .utils.observability_utils import (
    set_up_logging,
    set_up_metrics,
    set_up_tracing,
)

if not load_dotenv(dotenv_path=Path(__file__).parents[2] / ".env", verbose=True):
    print("Failed to load environment variables")
    exit(1)

# This must be done before any other telemetry calls
set_up_logging()
set_up_tracing()
set_up_metrics()

logger = logging.getLogger(__name__)


class WikiChatProcess:
    """Main process for chat with Wikipedia"""

    def __init__(self):
        self.kernel = self._setup_kernel()
        self.process = self._build_process()

    def _setup_kernel(self) -> Kernel:
        """Setup the kernel with Azure OpenAI service"""
        kernel = Kernel()

        # Add Azure OpenAI service
        kernel.add_service(
            AzureChatCompletion(
                deployment_name=os.getenv("DEPLOYMENT_NAME"),
                api_key=os.getenv("API_KEY"),
                endpoint=os.getenv("ENDPOINT"),
                service_id=os.getenv("DEPLOYMENT_NAME"),
            )
        )

        return kernel

    def _build_process(self):
        """Build the process with all steps and connections"""
        process_builder = ProcessBuilder(name="ChatWithWikipedia")  # type: ignore

        # Add the steps
        extract_query_step = process_builder.add_step(ExtractQueryStep)
        get_wiki_url_step = process_builder.add_step(GetWikiUrlStep)
        search_url_step = process_builder.add_step(SearchUrlStep)
        process_search_result_step = process_builder.add_step(ProcessSearchResultStep)
        augmented_chat_step = process_builder.add_step(AugmentedChatStep)

        # Define the flow - Start with question and chat_history
        process_builder.on_input_event("Start").send_event_to(
            target=extract_query_step,
            function_name="extract_query",
            parameter_name="data",
        )

        # Extract query -> Get URLs
        extract_query_step.on_function_result("extract_query").send_event_to(
            target=get_wiki_url_step,
            function_name="get_urls",
            parameter_name="data",
        )

        # Get URLs -> Search URLs
        get_wiki_url_step.on_function_result("get_urls").send_event_to(
            target=search_url_step,
            function_name="search_urls",
            parameter_name="data",
        )

        # Search URLs -> Process Results
        search_url_step.on_function_result("search_urls").send_event_to(
            target=process_search_result_step,
            function_name="process_results",
            parameter_name="data",
        )

        # Process Results -> Generate Answer
        process_search_result_step.on_function_result("process_results").send_event_to(
            target=augmented_chat_step,
            function_name="generate_answer",
            parameter_name="data",
        )

        return process_builder.build()

    async def _run_process(self, question: str) -> KernelProcess:
        """Helper to run the process and get the final state."""
        data = {"question": question}
        async with await start(
            process=self.process,
            kernel=self.kernel,
            initial_event=KernelProcessEvent(id="Start", data=data),
        ) as process_context:
            return await process_context.get_state()

    async def chat(self, question: str) -> dict[str, str]:
        """Run the chat process with a question"""
        print(f"Starting chat process with question: [green]{question}[/green]")

        final_state = await self._run_process(question)
        final_answer = final_state.steps[-1].state.state.answer  # type: ignore
        context = final_state.steps[-1].state.state.context  # type: ignore

        return {
            "response": final_answer,
            "context": context,
        }


def get_answer(question: str):
    result = asyncio.run(WikiChatProcess().chat(question))
    return {"response": result["response"], "context": result["context"]}


async def main():
    """Main function to demonstrate the process"""
    wiki_chat = WikiChatProcess()

    # Example usage
    question = "What is artificial intelligence?"
    result = await wiki_chat.chat(question)
    print(f"Final result: {result['response']}")


if __name__ == "__main__":
    asyncio.run(main())
