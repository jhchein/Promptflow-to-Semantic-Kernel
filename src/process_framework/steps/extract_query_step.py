"""
Extract Query Step - Refines the user's question based on chat history
"""

from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel, Field
from rich import print
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.chat_completion_client_base import (
    ChatCompletionClientBase,
)
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import kernel_function
from semantic_kernel.processes.kernel_process import (
    KernelProcessStep,
)
from semantic_kernel.processes.kernel_process.kernel_process_step_state import (
    KernelProcessStepState,
)

from ..prompts.extract_query_prompt import EXTRACT_QUERY_SYSTEM_PROMPT


class ExtractQueryStepState(BaseModel):
    chat_history: ChatHistory = Field(default_factory=ChatHistory)


class ExtractQueryStep(KernelProcessStep):
    """Process step to extract and refine the user's query from question and chat history"""

    state: ExtractQueryStepState = Field(default_factory=ExtractQueryStepState)

    system_prompt: ClassVar[str] = EXTRACT_QUERY_SYSTEM_PROMPT.format(
        date=datetime.today().strftime("%Y-%m-%d")
    )

    async def activate(self, state: KernelProcessStepState):
        """Activate the step and ensure chat history is initialized"""
        self.state = state.state  # type: ignore
        if self.state.chat_history is None:
            self.state.chat_history = ChatHistory(system_message=self.system_prompt)
        self.state.chat_history.system_message = self.system_prompt

    @kernel_function
    async def extract_query(
        self,
        kernel: Kernel,
        data: dict[str, ChatHistory],
    ) -> dict:
        """Extract the real intent from user question and chat history"""

        chat_service, settings = kernel.select_ai_service(type=ChatCompletionClientBase)
        assert isinstance(chat_service, ChatCompletionClientBase)

        question = data.get("question")

        self.state.chat_history.add_user_message(question)

        response = await chat_service.get_chat_message_content(
            chat_history=self.state.chat_history, settings=settings
        )

        extracted_query = str(response).strip()

        print(f"Extracted query: [blue]{extracted_query}[/blue]")

        return {"extracted_query": extracted_query, "question": question}
