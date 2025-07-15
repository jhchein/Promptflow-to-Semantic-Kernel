# part2.py
#
# This file extends the process from part1.py by adding a proofreading step and updating the process flow to include a review/approval cycle.
# The changes here correspond to the next steps in the official Semantic Kernel Process Framework tutorial:
#   - https://learn.microsoft.com/en-us/semantic-kernel/frameworks/process/examples/example-cycles?pivots=programming-language-python
#

import asyncio
import os
from typing import ClassVar

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.chat_completion_client_base import (
    ChatCompletionClientBase,
)
from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion,
    OpenAIChatPromptExecutionSettings,
)
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import kernel_function
from semantic_kernel.processes import ProcessBuilder
from semantic_kernel.processes.kernel_process import (
    KernelProcessEvent,
    KernelProcessStep,
    KernelProcessStepContext,
)
from semantic_kernel.processes.local_runtime.local_kernel_process import start

# --- PART 2.1: Import and extend process steps from part1.py ---
# Import the original process steps and state from part1.py
from part1 import (
    GatherProductInfoStep,
    GeneratedDocumentationState,
    KernelProcessStepState,
    PublishDocumentationStep,
)

# --- PART 2.2: Add a Proofreading Step ---
# This step is new in part2 and is not present in part1.py.
# It will review the generated documentation and emit either an approval or rejection event.


class ProofreadingResponse(BaseModel):
    """Structured output for the ProofreadingStep."""

    meets_expectations: bool = Field(
        description="Specifies if the proposed docs meets the standards for publishing."
    )
    explanation: str = Field(
        description="An explanation of why the documentation does or does not meet expectations."
    )
    suggestions: list[str] = Field(
        description="List of suggestions, empty if there are no suggestions for improvement."
    )


class ProofreadStep(KernelProcessStep):
    """A process step to proofread documentation before publishing (new in part2)."""

    @kernel_function
    async def proofread_documentation(
        self, docs: str, context: KernelProcessStepContext, kernel: Kernel
    ) -> None:
        print(f"{ProofreadStep.__name__}\n\t Proofreading product documentation...")

        system_prompt = """
        Your job is to proofread customer facing documentation for a new product from Contoso. You will be provided with 
        proposed documentation for a product and you must do the following things:

        1. Determine if the documentation passes the following criteria:
            1. Documentation must use a professional tone.
            1. Documentation should be free of spelling or grammar mistakes.
            1. Documentation should be free of any offensive or inappropriate language.
            1. Documentation should be technically accurate.
        2. If the documentation does not pass 1, you must write detailed feedback of the changes that are needed to 
            improve the documentation. 
        """

        chat_history = ChatHistory(system_message=system_prompt)
        chat_history.add_user_message(docs)

        # Use structured output to ensure the response format is easily parsable
        chat_service, settings = kernel.select_ai_service(type=ChatCompletionClientBase)
        assert isinstance(chat_service, ChatCompletionClientBase)  # nosec
        assert isinstance(settings, OpenAIChatPromptExecutionSettings)  # nosec

        settings.response_format = ProofreadingResponse

        response = await chat_service.get_chat_message_content(
            chat_history=chat_history, settings=settings
        )

        formatted_response: ProofreadingResponse = (
            ProofreadingResponse.model_validate_json(response.content)
        )

        suggestions_text = "\n\t\t".join(formatted_response.suggestions)
        print(
            f"\n\tGrade: {'Pass' if formatted_response.meets_expectations else 'Fail'}\n\t"
            f"Explanation: {formatted_response.explanation}\n\t"
            f"Suggestions: {suggestions_text}"
        )

        if formatted_response.meets_expectations:
            await context.emit_event(process_event="documentation_approved", data=docs)
        else:
            await context.emit_event(
                process_event="documentation_rejected",
                data={
                    "explanation": formatted_response.explanation,
                    "suggestions": formatted_response.suggestions,
                },
            )


# --- PART 2.3: Update GenerateDocumentationStep to support suggestions ---
# This class is extended from part1.py to add a new kernel_function for applying suggestions.


class GenerateDocumentationStep(KernelProcessStep[GeneratedDocumentationState]):
    state: GeneratedDocumentationState = Field(
        default_factory=GeneratedDocumentationState
    )

    system_prompt: ClassVar[
        str
    ] = """
Your job is to write high quality and engaging customer facing documentation for a new product from Contoso. You will 
be provided with information about the product in the form of internal documentation, specs, and troubleshooting guides 
and you must use this information and nothing else to generate the documentation. If suggestions are provided on the 
documentation you create, take the suggestions into account and rewrite the documentation. Make sure the product 
sounds amazing.
"""

    async def activate(
        self, state: KernelProcessStepState[GeneratedDocumentationState]
    ):
        self.state = state.state
        if self.state.chat_history is None:
            self.state.chat_history = ChatHistory(system_message=self.system_prompt)
        self.state.chat_history

    @kernel_function
    async def generate_documentation(
        self, context: KernelProcessStepContext, product_info: str, kernel: Kernel
    ) -> None:
        print(
            f"{GenerateDocumentationStep.__name__}\n\t Generating documentation for provided product_info..."
        )

        self.state.chat_history.add_user_message(
            f"Product Information:\n{product_info}"
        )

        chat_service, settings = kernel.select_ai_service(type=ChatCompletionClientBase)
        assert isinstance(chat_service, ChatCompletionClientBase)  # nosec

        response = await chat_service.get_chat_message_content(
            chat_history=self.state.chat_history, settings=settings
        )

        await context.emit_event(
            process_event="documentation_generated", data=str(response)
        )

    @kernel_function
    async def apply_suggestions(
        self, suggestions: str, context: KernelProcessStepContext, kernel: Kernel
    ) -> None:
        print(
            f"{GenerateDocumentationStep.__name__}\n\t Rewriting documentation with provided suggestions..."
        )

        self.state.chat_history.add_user_message(
            f"Rewrite the documentation with the following suggestions:\n\n{suggestions}"
        )

        chat_service, settings = kernel.select_ai_service(type=ChatCompletionClientBase)
        assert isinstance(chat_service, ChatCompletionClientBase)  # nosec

        generated_documentation_response = await chat_service.get_chat_message_content(
            chat_history=self.state.chat_history, settings=settings
        )

        await context.emit_event(
            process_event="documentation_generated",
            data=str(generated_documentation_response),
        )


# --- PART 2.4: Update the process flow to include the new proofreading step and cycle ---
# This section shows the new event routing, which now includes the proofreader and a feedback loop if the docs are rejected.

load_dotenv()

# Create the process builder (same as part1, but with new steps added)
process_builder = ProcessBuilder(name="DocumentationGeneration")

# Add the steps (proofreader is new)
info_gathering_step = process_builder.add_step(GatherProductInfoStep)
docs_generation_step = process_builder.add_step(GenerateDocumentationStep)
docs_proofread_step = process_builder.add_step(ProofreadStep)  # New step
docs_publish_step = process_builder.add_step(PublishDocumentationStep)

# Orchestrate the events (note the new cycle for rejected docs)
process_builder.on_input_event("Start").send_event_to(target=info_gathering_step)

info_gathering_step.on_function_result("gather_product_information").send_event_to(
    target=docs_generation_step,
    function_name="generate_documentation",
    parameter_name="product_info",
)

docs_generation_step.on_event("documentation_generated").send_event_to(
    target=docs_proofread_step, parameter_name="docs"
)

docs_proofread_step.on_event("documentation_rejected").send_event_to(
    target=docs_generation_step,
    function_name="apply_suggestions",
    parameter_name="suggestions",
)

docs_proofread_step.on_event("documentation_approved").send_event_to(
    target=docs_publish_step
)

# Configure the kernel with an AI Service and connection details, if necessary (same as part1)
kernel = Kernel()
kernel.add_service(
    AzureChatCompletion(
        deployment_name=os.getenv("DEPLOYMENT_NAME"),
        api_key=os.getenv("API_KEY"),
        endpoint=os.getenv("ENDPOINT"),
        service_id=os.getenv("DEPLOYMENT_NAME"),
    )
)

# Build the process
kernel_process = process_builder.build()

# --- PART 2.5: Run the process (same as part1, but now with the extended flow) ---


async def main():
    # Start the process
    async with await start(
        process=kernel_process,
        kernel=kernel,
        initial_event=KernelProcessEvent(id="Start", data="Contoso GlowBrew"),
    ) as process_context:
        _ = await process_context.get_state()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
