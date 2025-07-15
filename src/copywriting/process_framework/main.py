import asyncio
import os
from typing import ClassVar

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from rich import print
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
    KernelProcessStepState,
)
from semantic_kernel.processes.local_runtime.local_kernel_process import start

load_dotenv()


# A process step to gather information about a product
class GatherProductInfoStep(KernelProcessStep):
    @kernel_function
    def gather_product_information(self, product_name: str) -> str:
        print(
            f"[yellow]{GatherProductInfoStep.__name__}\n\tGathering product information for Product Name: {product_name}[/yellow]"
        )

        return """
Product Description:

GlowBrew is a revolutionary AI driven coffee machine with industry leading number of LEDs and 
programmable light shows. The machine is also capable of brewing coffee and has a built in grinder.

Product Features:
1. **Luminous Brew Technology**: Customize your morning ambiance with programmable LED lights that sync 
    with your brewing process.
2. **AI Taste Assistant**: Learns your taste preferences over time and suggests new brew combinations 
    to explore.
3. **Gourmet Aroma Diffusion**: Built-in aroma diffusers enhance your coffee's scent profile, energizing 
    your senses before the first sip.

Troubleshooting:
- **Issue**: LED Lights Malfunctioning
    - **Solution**: Reset the lighting settings via the app. Ensure the LED connections inside the 
        GlowBrew are secure. Perform a factory reset if necessary.
"""


# A sample step state model for the GenerateDocumentationStep
class GeneratedDocumentationState(BaseModel):
    """State for the GenerateDocumentationStep."""

    chat_history: ChatHistory | None = None


# A process step to generate documentation for a product
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

    @kernel_function
    async def generate_documentation(
        self, context: KernelProcessStepContext, product_info: str, kernel: Kernel
    ) -> None:
        print(
            f"[blue]{GenerateDocumentationStep.__name__}\n\tGenerating documentation for provided product_info...[/blue]"
        )

        self.state.chat_history.add_user_message(
            f"Product Information:\n{product_info}"
        )

        chat_service, settings = kernel.select_ai_service(type=ChatCompletionClientBase)
        assert isinstance(chat_service, ChatCompletionClientBase)

        response = await chat_service.get_chat_message_content(
            chat_history=self.state.chat_history, settings=settings
        )

        await context.emit_event(
            process_event="documentation_generated", data=str(response)
        )

    @kernel_function
    async def apply_suggestions(
        self,
        rejected_docs_info: dict[str, any],
        context: KernelProcessStepContext,
        kernel: Kernel,
    ) -> None:
        print(
            f"[blue]{GenerateDocumentationStep.__name__}\n\tRewriting documentation with provided suggestions...[/blue]"
        )

        suggestions = rejected_docs_info.get("suggestions", [])
        suggestions_text = "\n\t\t".join(suggestions)
        self.state.chat_history.add_user_message(
            f"Rewrite the documentation with the following suggestions:\n\n{suggestions_text}"
        )

        chat_service, settings = kernel.select_ai_service(type=ChatCompletionClientBase)
        assert isinstance(chat_service, ChatCompletionClientBase)

        generated_documentation_response = await chat_service.get_chat_message_content(
            chat_history=self.state.chat_history, settings=settings
        )

        await context.emit_event(
            process_event="documentation_generated",
            data=str(generated_documentation_response),
        )


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
    """A process step to proofread documentation before publishing."""

    @kernel_function
    async def proofread_documentation(
        self, docs: str, context: KernelProcessStepContext, kernel: Kernel
    ) -> None:
        print(
            f"[cyan]{ProofreadStep.__name__}\n\tProofreading product documentation...[/cyan]"
        )

        system_prompt = """
        Your job is to proofread customer facing documentation for a new product from Contoso. You will be provided with 
        proposed documentation for a product and you must do the following things:

        1. Determine if the documentation passes the following criteria:
            1. Documentation must use a professional tone.
            2. Documentation should be free of spelling or grammar mistakes.
            3. Documentation should be free of any offensive or inappropriate language.
            4. Documentation should be technically accurate.
            5. Documentation must use emojis to enhance engagement.
        2. If the documentation does not pass 1, you must write detailed feedback of the changes that are needed to 
            improve the documentation. 
        """

        chat_history = ChatHistory(system_message=system_prompt)
        chat_history.add_user_message(docs)

        chat_service, settings = kernel.select_ai_service(type=ChatCompletionClientBase)
        assert isinstance(chat_service, ChatCompletionClientBase)
        assert isinstance(settings, OpenAIChatPromptExecutionSettings)

        settings.response_format = ProofreadingResponse

        response = await chat_service.get_chat_message_content(
            chat_history=chat_history, settings=settings
        )

        formatted_response: ProofreadingResponse = (
            ProofreadingResponse.model_validate_json(response.content)
        )

        suggestions_text = "\n\t\t".join(formatted_response.suggestions)
        print(
            f"[magenta]{ProofreadStep.__name__}\n\tGrade: {'Pass' if formatted_response.meets_expectations else 'Fail'}\n\t"
            f"Explanation: {formatted_response.explanation}\n\t"
            f"Suggestions: {suggestions_text}[/magenta]"
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


# A process step to publish documentation
class PublishDocumentationStep(KernelProcessStep):
    @kernel_function
    async def publish_documentation(self, docs: str) -> None:
        print(
            f"[green]{PublishDocumentationStep.__name__}\n\tPublishing product documentation:\n\n{docs}[/green]"
        )


async def main():
    # Configure the kernel with an AI Service
    kernel = Kernel()
    kernel.add_service(
        AzureChatCompletion(
            deployment_name=os.getenv("DEPLOYMENT_NAME"),
            api_key=os.getenv("API_KEY"),
            endpoint=os.getenv("ENDPOINT"),
            service_id=os.getenv("DEPLOYMENT_NAME"),
        )
    )

    # Create the process builder
    process_builder = ProcessBuilder(name="DocumentationGeneration")

    # Add the steps
    info_gathering_step = process_builder.add_step(GatherProductInfoStep)
    docs_generation_step = process_builder.add_step(GenerateDocumentationStep)
    docs_publish_step = process_builder.add_step(PublishDocumentationStep)
    docs_proofread_step = process_builder.add_step(ProofreadStep)

    # Orchestrate the events
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
        parameter_name="rejected_docs_info",
    )

    docs_proofread_step.on_event("documentation_approved").send_event_to(
        target=docs_publish_step
    )

    # Build and start the process
    kernel_process = process_builder.build()
    async with await start(
        process=kernel_process,
        kernel=kernel,
        initial_event=KernelProcessEvent(id="Start", data="Contoso GlowBrew"),
    ) as process_context:
        _ = await process_context.get_state()


if __name__ == "__main__":
    asyncio.run(main())
