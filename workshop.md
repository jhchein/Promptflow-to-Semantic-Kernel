# Semantic Kernel Process Framework Workshop

Welcome to the hands-on workshop for migrating Prompt Flow applications to the Semantic Kernel (SK) Process Framework, with a focus on evaluation, observability, and Azure AI integrations. This workshop is designed for developers and AI practitioners interested in modernizing their LLM workflows using Microsoft's latest open-source frameworks and Azure AI Foundry.

## Workshop Goals

- Understand the motivation and architecture behind the SK Process Framework
- Migrate a Prompt Flow (RAG) example to SK Process Framework (Wikipedia use case)
- Explore a second SK Process Framework example (Copywriting)
- Enable and forward tracing/observability to Azure AI Foundry
- Run LLM-based evaluation pipelines
- (Optional) Compare with Azure AI Agent Service implementation

---

## Agenda & Step-by-Step Instructions

### 0. Introduction & Setup

- **Overview:** Briefly introduce Prompt Flow, SK Process Framework, and Azure AI Foundry.
- **Clone the repository**

- **Local Setup**

  - Install Python 3.13+
  - Install [uv](https://github.com/astral-sh/uv) for dependency management.
  - Install the Azure CLI (optional, for resource management).

- **Azure Prerequisites**

  - An Azure Subscription with access to Azure AI services.
  - An **Azure AI Foundry Project**. You can create this directly in the [Azure AI Foundry Portal](https://ai.azure.com/?cid=learnDocs) by selecting "Create new" and choosing "Foundry project". The resource is created for you automatically.
  - **Deploy a Model** (e.g., `gpt-4.1-mini`, recommended for this workshop for simplicity):
    - In your Foundry project, go to the Model Catalog, search for your desired model, and select "Deploy".
    - Leave the default deployment name or choose your own.
    - Wait for deployment to complete.
  - **Get your Project Connection String:**
    - In your Foundry project, go to the Overview page and copy the connection string.

- **Configure Your Environment**
  - Copy the `.env.sample` file to a new file named `.env` at the root of the repository.
  - Fill in the required values based on your Azure AI Project setup.

### 1. (Optional) Recap: How Prompt Flow Works

- **Review the Prompt Flow DAG**  
  Open `src/wikipedia/promptflow/flow.dag.yaml`.

  - Identify the main steps: query extraction, Wikipedia URL search, context retrieval, answer generation.
  - Observe how each step is defined and connected in the YAML.

    ```mermaid
    graph TD
        A[Input: Question] -- question --> B(ExtractQueryStep);
        B -- extracted_query --> C(GetWikiUrlStep);
        C -- url_list --> D(SearchUrlStep);
        D -- search_results --> E(ProcessSearchResultStep);
        E -- context --> F(AugmentedChatStep);
        F -- answer --> G[Output: Final Answer];
    ```

- **Understand Prompt Engineering**  
  Open `src/wikipedia/promptflow/extract_query_from_question.jinja2`.

  - See how the prompt is structured for extracting a search query from a user question.
  - Observe the use of Jinja2 templating for dynamic prompt creation.

- **Explore Python Tool Integration**  
  Open `src/wikipedia/promptflow/get_wiki_url.py`.

  - Notice the use of the `@tool` decorator—this exposes the function as a step in the flow.
  - Check how the function receives input, processes it, and returns output to the flow.

- **Key Takeaways:**
  - The YAML file orchestrates the workflow and data flow between steps.
  - Prompt templates define how LLMs are instructed at each step.
  - Python code (with decorators) implements custom logic and integrates external tools.

### 2. Migrating to Semantic Kernel Process Framework

- **Understand the Process Framework Concepts**

  - The SK Process Framework lets you define modular, extensible, and stateful AI workflows in Python.
  - **Processes** are composed of **Steps** (Python classes), which can be stateless or stateful.
  - **Steps** communicate via **Events**, enabling flexible orchestration (e.g., sequential pipelines, cycles, branches).

- **Deconstructing the Migrated Wikipedia Process**

  - **1. The Entry Point (`wikipedia.py`)**

    - Open [`wikipedia.py`](c:\code\customer\Lufthansa\DigitalHangar\wikipedia.py).
    - This file shows how a consumer would use the process. It initializes the `WikiChatProcess` and calls the `.chat()` method with a user's question.

  - **2. The Orchestrator (`wiki_chat_process.py`)**

    - Open [`src/wikipedia/process_framework/wiki_chat_process.py`](c:\code\customer\Lufthansa\DigitalHangar\src\wikipedia\process_framework\wiki_chat_process.py).
    - The `_build_process` method is the core of the orchestration.
    - **`ProcessBuilder`**: This is used to define the workflow's structure.
    - **`add_step()`**: Each Python class representing a step in the workflow is registered here.
    - **Event Routing**: The flow is defined by wiring events between steps. Notice the pattern: `step.on_function_result(...).send_event_to(...)`. This creates a directed graph that routes data from one step's output to the next step's input.

  - **3. Deep Dive into a Step (`extract_query_step.py`)**

    - Open [`src/wikipedia/process_framework/steps/extract_query_step.py`](c:\code\customer\Lufthansa\DigitalHangar\src\wikipedia\process_framework\steps\extract_query_step.py). This is a great example of a stateful step.
    - **`KernelProcessStep`**: All steps inherit from this base class.
    - **`@kernel_function`**: This decorator exposes a method within the step that can be called by the process orchestrator.
    - **State Management**:
      - Notice the `ExtractQueryStepState` class defined with `pydantic`. This model defines the data that persists for this step across multiple turns.
      - The `activate` method is called by the framework to load the step's current state, enabling it to remember things like `chat_history`.
    - **Prompt Integration**:
      - Now, open [`src/wikipedia/process_framework/prompts/extract_query_prompt.py`](c:\code\customer\Lufthansa\DigitalHangar\src\wikipedia\process_framework\prompts\extract_query_prompt.py).
      - You can see this prompt template is imported and used within the `ExtractQueryStep` to instruct the LLM. This is a good practice for separating prompts from logic.

  - **4. Understanding the Utilities (`utils/`)**
    - The `utils` directory contains helper code. It's important to distinguish between application logic and framework integration.
    - **Framework-Relevant (`observability_utils.py`)**: Open [`src/wikipedia/process_framework/utils/observability_utils.py`](c:\code\customer\Lufthansa\DigitalHangar\src\wikipedia\process_framework\utils\observability_utils.py). This file is crucial for understanding how to integrate the Process Framework with standard tooling like OpenTelemetry for logging, tracing, and metrics that can be sent to services like Azure Monitor.
    - **Custom Logic (`wiki_utils.py`, `web_utils.py`)**: These files contain application-specific code for searching Wikipedia and scraping web content. They are called by the steps but are not part of the framework itself.

- **Run the Wikipedia chat demo**
  - In your terminal, run: `uv run wikipedia.py`
  - Try the sample questions and observe the outputs in the console.

### 3. Second Example: Copywriting Process with Cycles

This second example, based on the official Semantic Kernel documentation, introduces a more advanced workflow: a process with a feedback loop (a cycle). While the Wikipedia example was a linear pipeline, this copywriting process can loop back on itself until a quality standard is met.

- **Explore the copywriting process**

  - First, review the process diagram from the `README.md` to understand the flow. Notice the loop from "Proofread" back to "Generate Documentation".

    ```mermaid
    graph TD
        A[Input: Product Name] --> B(GatherProductInfoStep);
        B -- product_info --> C(GenerateDocumentationStep);
        C -- generated_docs --> D{ProofreadStep};
        D -- Approved --> E(PublishDocumentationStep);
        D -- Rejected --> C;
        E --> F[Output: Published Documentation];
    ```

  - Open [`src/copywriting/process_framework/main.py`](c:\code\customer\Lufthansa\DigitalHangar\src\copywriting\process_framework\main.py).
  - This process introduces a key concept: **dynamic event routing** to create cycles.

- **Understanding `send_event_to` vs. `emit_event`**

  - **`send_event_to` (Static Routing):**

    - As seen in the `wiki_chat_process.py`, `send_event_to` is used in the `ProcessBuilder` to define a fixed, predictable path. It wires one step's output directly to the next step's input. This is perfect for creating linear pipelines.
    - `info_gathering_step.on_function_result(...).send_event_to(target=docs_generation_step, ...)`

  - **`emit_event` (Dynamic Routing):**
    - Look inside the `ProofreadStep` in `main.py`. The `proofread_documentation` function contains conditional logic:
      ```python
      if formatted_response.meets_expectations:
          await context.emit_event(process_event="documentation_approved", data=docs)
      else:
          await context.emit_event(process_event="documentation_rejected", data=...)
      ```
    - `emit_event` allows a step to decide _at runtime_ which event to fire based on its results. This is the key to enabling complex, non-linear workflows.

- **How the Cycle is Formed**

  - The `ProcessBuilder` is configured to listen for these dynamically emitted events:
    - The `documentation_approved` event moves the process forward to the `PublishDocumentationStep`.
    - The `documentation_rejected` event sends the process **back** to the `GenerateDocumentationStep`, passing along the feedback. This creates the cycle.
  - This pattern is incredibly powerful for scenarios requiring validation, retries, or human-in-the-loop interventions.

- **Other Noteworthy Features**

  - **Structured Output:** The `ProofreadStep` uses a Pydantic model (`ProofreadingResponse`) to force the LLM to return a structured JSON object. This makes the output reliable and easy to parse, which is essential for the conditional logic.
  - **Deliberate Failure for Demonstration:** The proofreading prompt includes a specific, slightly unusual requirement: "Documentation must use emojis to enhance engagement." This is intentionally designed to make the first draft fail, clearly demonstrating the rejection and feedback cycle.

- **Run the copywriting demo**
  - `uv run src/copywriting/process_framework/main.py`
  - **Observe the cycle in action**: Pay close attention to the output. Because of the emoji requirement, the `ProofreadStep` will reject the first draft. You will see the process loop back, apply the feedback, and regenerate the text _with_ emojis to get approval. This is a practical demonstration of the feedback loop.

### 4. Enabling Tracing & Observability with Azure AI Foundry

Observability is critical for understanding and debugging complex AI systems. By enabling tracing, you can visualize the entire flow of your process, inspect the inputs and outputs of each step, and measure performance. This project uses the OpenTelemetry standard to send trace data to Azure AI Studio (which is built on Azure Monitor Application Insights).

- **Core Concepts:**

  - **OpenTelemetry**: An open-source observability framework. It provides standard APIs and SDKs for generating and collecting telemetry data (traces, metrics, logs).
  - **Azure Monitor Exporter**: A library that collects data from the OpenTelemetry SDK in your application and sends it to Azure.
  - **Semantic Kernel Integration**: The SK framework is instrumented with OpenTelemetry. When a global trace provider is configured, the kernel automatically emits detailed traces for operations like function calls and AI requests.

- **Code Walkthrough: How Tracing is Implemented**

  - **Step 1: Configuration (`.env`)**

    - The connection to Azure is established using the `APPLICATION_INSIGHTS_CONNECTION_STRING` in your `.env` file. This is the only secret you need to connect your application to your Azure AI project's monitoring capabilities.

  - **Step 2: Setting up the Trace Exporter (`observability_utils.py`)**

    - Open [`src/wikipedia/process_framework/utils/observability_utils.py`](c:\code\customer\Lufthansa\DigitalHangar\src\wikipedia\process_framework\utils\observability_utils.py).
    - The `set_up_tracing` function contains the core logic:
      - **`AzureMonitorTraceExporter(...)`**: An instance of the exporter is created using the connection string from the environment variables.
      - **`Resource.create(...)`**: A resource is defined to tag all telemetry from this application with a `SERVICE_NAME` (`semantic_kernel_wiki_chat_process`). This is crucial for filtering and identifying your application's traces in Azure AI Studio.
      - **`TracerProvider`**: This is the main entry point to the OpenTelemetry tracing API. It's configured with the resource tags.
      - **`BatchSpanProcessor`**: This processor is added to the `TracerProvider`. It efficiently batches multiple spans (traces) together before sending them to Azure, which is more performant than sending them one by one.
      - **`set_tracer_provider`**: This crucial line sets the configured `TracerProvider` as the global default for the entire application.

  - **Step 3: Initializing Tracing in the Application (`wiki_chat_process.py`)**
    - Open [`src/wikipedia/process_framework/wiki_chat_process.py`](c:\code\customer\Lufthansa\DigitalHangar\src\wikipedia\process_framework\wiki_chat_process.py).
    - At the very top of the script, you'll see the call: `set_up_tracing()`.
    - **Why here?** By calling this function before any other code runs, we ensure that the global tracer provider is registered. From this point forward, any Semantic Kernel operation that occurs will automatically detect the provider and emit detailed traces without any extra code.

- **Viewing the Traces**

  1. **Run the application** after setting your connection string.
  2. **Navigate to your Azure AI Project** in Azure AI Studio.
  3. **Go to the "Traces" section** to find and explore the traces from your application, which will be identified by the service name `semantic_kernel_wiki_chat_process`. You can drill down into each run to see the full execution graph, including timings, inputs, and outputs for each step.

### 5. Running LLM-based Evaluation

Once your application is running, how do you know if it's any good? Evaluation is key to measuring and improving the quality of your AI system. This project uses the `azure-ai-evaluation` SDK to run an "LLM-as-a-judge" evaluation.

- **Core Concepts: What is LLM-as-a-Judge?**

  - Instead of relying on traditional metrics, we use a powerful "judge" LLM (like GPT-4) to assess the quality of our application's responses.
  - We provide the judge with the user's question, the ground truth answer, the retrieved context, and our application's actual response.
  - The judge then scores the response on various quality metrics, such as relevance and groundedness, and even provides a detailed reason for its score.

- **Code Walkthrough: The Evaluation Pipeline**

  - **1. The Test Data (`wiki.jsonl`)**

    - Open [`src/wikipedia/evaluation/wiki.jsonl`](c:\code\customer\Lufthansa\DigitalHangar\src\wikipedia\evaluation\wiki.jsonl).
    - This file contains our "golden dataset"—a set of questions and the ideal, `ground_truth_answer` for each. This is what we'll measure our system against.

  - **2. The Evaluation Script (`evaluate.py`)**

    - Open [`src/wikipedia/evaluation/evaluate.py`](c:\code\customer\Lufthansa\DigitalHangar\src\wikipedia\evaluation\evaluate.py). This is the heart of the evaluation process.
    - **`AzureOpenAIModelConfiguration`**: First, we configure the "judge" LLM. This tells the evaluation SDK which powerful model to use for scoring.
    - **`evaluate()` function**: This is the main function from the SDK. Let's break down its key parameters:
      - **`data`**: Points to our test dataset, `wiki.jsonl`.
      - **`target`**: This is the function we want to evaluate. Here, it's the `get_answer` function from our `WikiChatProcess`. The SDK will call this function for each question in our dataset to get a live response.
      - **`evaluators`**: This dictionary defines the quality metrics we want to measure. For our RAG application, we use:
        - `RelevanceEvaluator`: Is the answer relevant to the user's question?
        - `RetrievalEvaluator`: Was the retrieved context relevant for answering the question?
        - `GroundednessEvaluator`: Is the answer based on the provided context, or is it hallucinating?
      - **`evaluator_config`**: This is the most important part. The `column_mapping` tells the SDK how to connect the data from our dataset and our target function's output to the inputs that the evaluators expect.
        - `${data.question}` maps the `question` column from `wiki.jsonl`.
        - `${target.response}` maps the `response` key from the dictionary returned by our `get_answer` function.
        - `${target.context}` maps the `context` key.

  - **3. The Output (`print_eval.py` and `evaluation_result.json`)**
    - The evaluation script saves the full results as a JSON file.
    - It also uses the helper functions in [`src/wikipedia/evaluation/print_eval.py`](c:\code\customer\Lufthansa\DigitalHangar\src\wikipedia\evaluation\print_eval.py) to print a user-friendly summary in the console, showing the pass/fail status and the reasoning from the LLM judge for each metric.

- **Run the Evaluation**

  - In your terminal, run: `uv run -m src.wikipedia.evaluation.evaluate`
  - Observe the output in the console. You will see a summary table of metrics and a detailed breakdown for each question in the test set.

### 6. (Optional) Alternative: Azure AI Agent Service

So far, we've built a RAG application from the ground up using the SK Process Framework, giving us maximum control. But what if we want to move faster and let a managed service handle the orchestration? That's where the **Azure AI Agent Service** comes in.

- **Core Concepts: A Higher-Level Abstraction**

  - The Agent Service provides a managed, high-level framework for building assistants. Instead of defining each step and the event flow manually, you provide an LLM with a system prompt and a set of tools, and the agent automatically figures out how to use them in a reasoning loop (ReAct).
  - **Key Differences from SK Process Framework:**
    - **Orchestration:** Handled automatically by the agent's built-in ReAct loop. You don't use a `ProcessBuilder`.
    - **State Management:** Conversation history and state are managed automatically within a `thread`.
    - **Tools:** You provide tools (like the pre-built `BingGroundingTool`) directly to the agent, rather than creating custom steps.
    - **Tracing:** Enabled by default in Azure AI Studio, requiring no manual OpenTelemetry setup in your code.

- **Code Walkthrough: The Agent Service Implementation**

  - **1. Prerequisites (`README.md`)**

    - As noted in [`src/wikipedia/agent_service/README.md`](c:\code\customer\Lufthansa\DigitalHangar\src\wikipedia\agent_service\README.md), this approach requires a `GroundingWithBing` connection to be configured in your Azure AI Project. This gives the agent its RAG capability.

  - **2. Creating the Agent (`setup.py`)**

    - Open [`src/wikipedia/agent_service/setup.py`](c:\code\customer\Lufthansa\DigitalHangar\src\wikipedia\agent_service\setup.py).
    - This script programmatically creates a new agent in your AI Project.
    - **`project.agents.create_agent(...)`**: Notice how simple this is. We define the `instructions` (the system prompt), give it a `name`, and provide it with `tools`—in this case, the `BingGroundingTool`.
    - The service handles the rest. There's no need to build a multi-step pipeline for retrieving information and generating an answer.

  - **3. Interacting with the Agent (`agent_service.py`)**
    - Open [`src/wikipedia/agent_service/agent_service.py`](c:\code\customer\Lufthansa\DigitalHangar\src\wikipedia\agent_service\agent_service.py).
    - **`AIProjectClient`**: Connects to our project.
    - **`project.agents.get_agent(...)`**: Retrieves the agent we created.
    - **`project.agents.threads.create()`**: Creates a new conversation thread to manage history.
    - **`project.agents.runs.create_and_process(...)`**: This is the magic. This single call sends the user's message to the agent, which then runs its internal loop: it reasons about the request, decides to use the Bing search tool, gets the results, and formulates a final answer.

- **Run the Agent Service Demo**

  1. **Create the Agent**: You can either create the agent via the Azure AI Studio UI (recommended) or run the setup script: `uv run src/wikipedia/agent_service/setup.py`. Note the **Agent ID** that is printed.
  2. **Update Agent ID**: Open `agent_service.py` and replace the placeholder `agent_id` with your new ID.
  3. **Run the Chat**: `uv run src/wikipedia/agent_service/agent_service.py`.
  4. **Observe the results**: The agent will answer the questions using the Bing grounding tool, providing sources in its response.

- **Interacting with Your Deployed Agent**
  Once your agent is created, it's not just available via the SDK. You can interact with it in multiple ways:

  - **Azure AI Studio Playground**: Navigate to your AI Project in the [Azure AI Studio](https://ai.azure.com/), go to the "Agents" tab, and select your agent. You can chat with it directly in the web-based playground. This is perfect for rapid testing, demonstrations, and no-code interaction.
  - **REST API**: The agent is exposed via a REST API. The Python SDK used in `agent_service.py` is a convenient wrapper around this API. This means you can integrate your agent into any application, regardless of the programming language, by making standard HTTP requests.

### 7. Q&A and Next Steps

- **Discussion: When to use SK Process Framework vs. Agent Service?**

  - **SK Process Framework**: Choose for maximum control, custom logic, and complex, explicit workflows. It's ideal when you need to define every step of the process, manage state in a specific way, or integrate with tools and systems that aren't pre-built for the Agent Service.
  - **Azure AI Agent Service**: Choose for speed and simplicity or multi-agent orchestration. It's perfect for building standard chat assistants and simple RAG applications where a managed ReAct loop and pre-built tools are sufficient. It abstracts away the complexity of orchestration and state management.
  - You can the Agent Service within the Process Framework.

- **Productionization Considerations**

  - **Error Handling**: The code in this workshop is simplified. In a production environment, you would need to add robust error handling, retries, and fallbacks to every step of your process.
  - **CI/CD**: Consider setting up a CI/CD pipeline that runs the evaluation script automatically.

    The `azure-ai-evaluation` SDK can be integrated into a GitHub Actions workflow to run on every push to a branch or on a schedule. This ensures that any changes to your prompts, code, or models are automatically tested against your golden dataset.

    For more details, see the official documentation: [How to run an evaluation in GitHub Action](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/evaluation-github-action?tabs=foundry-project)

  - **Cost and Performance Monitoring**: Use the metrics and traces in Azure AI Studio to monitor the cost and latency of your application. Set up alerts for anomalies.

- **Further Exploration**
  - **Custom Tools**: Try adding your own custom Python functions as tools.
  - **Human-in-the-Loop**: How could you modify the copywriting example to require a manual approval step from a human before publishing? Check: [How-To: Human-in-the-Loop](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/process/examples/example-human-in-loop?pivots=programming-language-python).
  - **More Complex Evaluations**: Explore other metrics in the `azure-ai-evaluation` SDK, such as fluency and coherence.

---

## Appendix: Useful Links

- **Semantic Kernel**

  - [SK Process Framework Documentation](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/process/)
  - [SK Concepts: Observability with AI Foundry](https://learn.microsoft.com/en-us/semantic-kernel/concepts/enterprise-readiness/observability/telemetry-with-azure-ai-foundry-tracing)
  - [Example: Create your first Process](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/process/examples/example-first-process?pivots=programming-language-python)
  - [Example: Using Cycles in a Process](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/process/examples/example-cycles?pivots=programming-language-python)

- **Azure AI Foundry**

  - [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/)
  - [Create an AI Foundry Project](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/create-projects?tabs=ai-foundry)
  - [Trace your application with AI Foundry](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/trace-application)
  - [Evaluate with the Azure AI SDK](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/evaluate-sdk)
  - [Evaluation Metrics for RAG](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/evaluation-metrics-rag)

- **Azure AI Agent Service**

  - [Azure AI Agents Quickstart](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/quickstart?pivots=programming-language-python-azure)
  - [Agent Tracing Concepts](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/tracing)

- **Prompt Flow**
  - [Prompt Flow Documentation](https://learn.microsoft.com/en-us/azure/machine-learning/prompt-flow/)
