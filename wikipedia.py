"""
Chat with Wikipedia using Semantic Kernel Process Framework
This is a migration from PromptFlow to Semantic Kernel Process Framework
"""

import asyncio

from rich import print

from src.wikipedia.process_framework import WikiChatProcess


async def main():
    """Main function to demonstrate the migrated Wikipedia chat process"""

    # Initialize the process
    wiki_chat = WikiChatProcess()

    # Example conversation
    print("=== Chat with Wikipedia Demo ===")
    print("Migrated from PromptFlow to Semantic Kernel Process Framework\n")

    # Example 1: Simple question
    print("Example 1: Simple Question")
    question1 = "Tell me about Leonardo da Vinci."
    answer1 = await wiki_chat.chat(question1)
    print(f"Answer: {answer1['response']}\nContext: {answer1['context']}\n")

    # Example 2: Question with chat history
    print("---\n\nExample 2: Question with Chat History (stateful)")
    question2 = "Tell me about his most famous piece of art."
    answer2 = await wiki_chat.chat(question2)
    print(f"Answer: {answer2['response']}\nContext: {answer2['context']}\n")

    # Example 3: A question without context
    print("---\n\nExample 3: Question without Context")
    question3 = "Who will win the next Super Bowl?"
    answer3 = await wiki_chat.chat(question3)
    print(f"Answer: {answer3['response']}\nContext: {answer3['context']}\n")
    print("=== End of Demo ===\n")


if __name__ == "__main__":
    asyncio.run(main())
