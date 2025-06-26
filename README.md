# PromptFlow to Semantic Kernel Process Framework Migration

This repository demonstrates how to migrate a PromptFlow application to the Semantic Kernel Process Framework.

## Project Structure

```text
├── promptflow/                   # Original PromptFlow implementation
│   ├── flow.dag.yaml             # Original DAG definition
│   ├── *.py                      # Original Python tools
│   └── *.jinja2                  # Original prompt templates
├── src/
│   └── process_framework/        # New Semantic Kernel implementation
│       ├── steps/                # Process steps (migrated from DAG nodes)
│       ├── prompts/              # Parametrized prompt templates
│       ├── utils/                # Utility functions
│       └── wiki_chat_process.py  # Main process implementation
└── main.py                       # Demo application
```

## Migration Overview

### Original PromptFlow Nodes → Process Steps

| PromptFlow Node               | Process Step              | Description                            |
| ----------------------------- | ------------------------- | -------------------------------------- |
| `extract_query_from_question` | `ExtractQueryStep`        | LLM call to refine user query          |
| `get_wiki_url`                | `GetWikiUrlStep`          | Python tool to find Wikipedia URLs     |
| `search_result_from_url`      | `SearchUrlStep`           | Python tool to fetch content from URLs |
| `process_search_result`       | `ProcessSearchResultStep` | Python tool to format search results   |
| `augmented_chat`              | `AugmentedChatStep`       | LLM call to generate final answer      |

### Key Changes

1. **DAG Definition**: Moved from YAML to Python with `ProcessBuilder`
2. **Node Logic**: Converted to `KernelProcessStep` classes with `@kernel_function` decorators
3. **Event-Driven Flow**: Data flows through events between steps
4. **Prompt Templates**: Separated into parametrized Python files for variant testing
5. **Utilities**: Extracted reusable functions to utils modules

## Migration Status

- [x] Copy the Chat with Wikipedia Flow
- [x] Rewrite the code with Semantic Kernel Process Framework
  - [x] Created process steps from original DAG nodes
  - [x] Extracted prompts into parametrized templates
  - [x] Migrated utility functions
  - [x] Built event-driven process flow
- [ ] Add tracing and observability
- [ ] Create evaluation dataset and metrics
- [ ] Add red teaming capabilities

## Running the Demo

```bash
# Setup environment variables in .env
# API_KEY=your_azure_openai_key
# ENDPOINT=your_azure_openai_endpoint
# DEPLOYMENT_NAME=your_model_deployment

# Run the demo
python main.py
```

## Key Benefits of Migration

- **Better Integration**: Native integration with Semantic Kernel ecosystem
- **Type Safety**: Better type checking and IDE support
- **Modularity**: Easier to test and maintain individual steps
- **Event-Driven**: More flexible flow control with events
- **Scalability**: Better support for complex workflows and cycles

## Next Steps

- Add tracing and observability
- Implement evaluation metrics
- Add error handling and retry logic
- Create more sophisticated event handling
