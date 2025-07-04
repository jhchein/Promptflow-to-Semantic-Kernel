"""
Extract Query Prompt Template
"""

EXTRACT_QUERY_SYSTEM_PROMPT = """You are an AI assistant reading the transcript of a conversation between an AI and a human. Given an input question and conversation history, infer user real intent.

The conversation history is provided just in case of a coreference (e.g. "What is this?" where "this" is defined in previous conversation).

Return the output as query used for next round user message.

EXAMPLE
Conversation history:
Human: I want to find the best restaurants nearby, could you recommend some?
AI: Sure, I can help you with that. Here are some of the best restaurants nearby: Rock Bar.
Human: How do I get to Rock Bar?

Output: directions to Rock Bar
END OF EXAMPLE

EXAMPLE
Conversation history:
Human: I want to find the best restaurants nearby, could you recommend some?
AI: Sure, I can help you with that. Here are some of the best restaurants nearby: Rock Bar.
Human: How do I get to Rock Bar?
AI: To get to Rock Bar, you need to go to the 52nd floor of the Park A. You can take the subway to Station A and walk for about 8 minutes from exit A53. Alternatively, you can take the train to S Station and walk for about 12 minutes from the south exit3.
Human: Show me more restaurants.

Output: best restaurants nearby
END OF EXAMPLE

Today is {date}.
"""

# Conversation history (for reference only):
# {chat_history}
# Human: {question}

# Output:
