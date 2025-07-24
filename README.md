# PromptFlow to Semantic Kernel Process Framework Migration

This repository demonstrates how to migrate a PromptFlow application to the Semantic Kernel Process Framework, including evaluation and observability (tracing) capabilities.

## Workshop Guide

This repository contains a comprehensive [workshop.md](workshop.md) file that can be used as a guide for a hands-on workshop or for self-paced learning. It provides step-by-step instructions for all the concepts demonstrated in this repository, from setup and migration to evaluation and deployment.

## Project Structure

```text
.
├── main.py                       # Chat with Wiki Demo application
├── .env.sample                   # Environment variable template
├── pyproject.toml                # Project dependencies
└── src/
    ├── copywriting/              # Domain: Copywriting (Advanced SK Process Demo)
    └── wikipedia/                # Domain: Wikipedia (Chat with Wikipedia)
        ├── promptflow/           # Original PromptFlow implementation
        ├── process_framework/    # SK Process Framework implementation
        ├── evaluation/           # Evaluation suite for Wikipedia
        └── agent_service/        # Optional: Azure AI Agent Service demo
```

## Getting Started

### 1. Set up Environment Variables

Copy the sample `.env.sample` file to `.env` and update it.

```bash
cp .env.sample .env
```

### 2. Install Dependencies and Run

This project uses `uv` to manage the virtual environment and dependencies.

#### Running the Wikipedia Chat Demo

To run the interactive chat demo, which showcases the migrated Semantic Kernel process:

```bash
uv run wikipedia.py
```

#### Running the Copywriting Demo

To run the copywriting demo, which showcases a process with a feedback cycle:

```bash
uv run src/copywriting/process_framework/main.py
```

#### Running the Evaluation

To run the evaluation suite against the `wiki.jsonl` dataset:

```bash
uv run -m src.wikipedia.evaluation.evaluate
```

The script will run the evaluators (Relevance, Retrieval, Groundedness) and print a detailed, color-coded report to the console. The full results are saved to `src/wikipedia/evaluation/evaluation_result.json`.

## Wikipedia Example: PromptFlow Migration

### Process Flow

The application logic is modeled as a series of connected steps within the Semantic Kernel Process Framework.

```mermaid
graph TD
    A[Input: Question] -- question --> B(ExtractQueryStep);
    B -- extracted_query --> C(GetWikiUrlStep);
    C -- url_list --> D(SearchUrlStep);
    D -- search_results --> E(ProcessSearchResultStep);
    E -- context --> F(AugmentedChatStep);
    F -- answer --> G[Output: Final Answer];
```

### Migration Overview

The core logic from the PromptFlow DAG was migrated to distinct, reusable `ProcessStep` classes.

| PromptFlow Node               | Process Step              | Description                                      |
| ----------------------------- | ------------------------- | ------------------------------------------------ |
| `extract_query_from_question` | `ExtractQueryStep`        | LLM call to refine user query **(stateful)**     |
| `get_wiki_url`                | `GetWikiUrlStep`          | Python tool to find Wikipedia URLs               |
| `search_result_from_url`      | `SearchUrlStep`           | Python tool to fetch content from URLs           |
| `process_search_result`       | `ProcessSearchResultStep` | Python tool to format search results             |
| `augmented_chat`              | `AugmentedChatStep`       | LLM call to generate final answer **(stateful)** |

## Advanced Example: Copywriting Process with Cycles

This second example demonstrates a more advanced workflow: a process with a feedback loop (a cycle). While the Wikipedia example is a linear pipeline, this copywriting process can loop back on itself until a quality standard is met. This showcases the framework's ability to handle complex, non-linear orchestration.

### Process Flow

```mermaid
graph TD
    A[Input: Product Name] --> B(GatherProductInfoStep);
    B -- product_info --> C(GenerateDocumentationStep);
    C -- generated_docs --> D{ProofreadStep};
    D -- Approved --> E(PublishDocumentationStep);
    D -- Rejected --> C;
    E --> F[Output: Published Documentation];
```

### Key Concepts Demonstrated

- **Cycles and Feedback Loops**: The `ProofreadStep` can reject a document and send it back to the `GenerateDocumentationStep` with feedback, creating a loop that continues until the output is approved.
- **Dynamic Event Routing**: Unlike the static `send_event_to` used in the Wikipedia example, this process uses `context.emit_event()`. This allows a step to decide _at runtime_ which event to fire based on conditional logic (e.g., if a document is approved or rejected), enabling flexible and dynamic workflows.
- **Structured Output**: The `ProofreadStep` uses a Pydantic model to force the LLM to return a structured JSON object, making the output reliable and easy to parse for the conditional routing logic.

## Migration Status

- [x] Copy the Chat with Wikipedia Flow
- [x] Rewrite the code with Semantic Kernel Process Framework
  - [x] Created process steps from original DAG nodes
  - [x] Extracted prompts into parametrized templates
  - [x] Migrated utility functions
  - [x] Built event-driven process flow
- [x] Add tracing and observability
- [x] Create evaluation dataset and metrics
  - [x] Implemented Relevance, Retrieval, and Groundedness evaluators
  - [x] Added pretty-printing for evaluation results
- [ ] Add red teaming capabilities
- [ ] Add a more complex SK Process Framework demo (leverage events, more complex flows, structured outputs, and agents with tools) ... e.g. https://github.com/jennifermarsman/MultiagentResearch
