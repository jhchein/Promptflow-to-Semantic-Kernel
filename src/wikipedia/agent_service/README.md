# RAG Agent with Azure AI Agents and Bing Search

This short demo showcases how to develop the Wiki Chat (RAG) agent using the Azure AI Agent Service. The agent leverages the [Grounding with Bing Search tool](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/bing-grounding) to ground its responses in real-world information.

For a more comprehensive guide, please see the [Azure AI Agents Quickstart](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/quickstart?pivots=programming-language-python-azure).

## Prerequisites

Before you begin, ensure you have the following:

- An existing Azure AI Project.
- An "Azure AI Developer" role assignment for your user identity in the project.
- An Azure Grounding with Bing Search resource.
- A "GroundingWithBing" connection configured in your Azure AI Project.

## 1. Environment Setup

This project uses a `.env` file in the root directory to manage environment variables. As described in the main `README.md`, this file should already exist. Ensure the following variables required for the agent service are present and correctly configured in your `.env` file:

```env
# Azure AI Project Endpoint
PROJECT_ENDPOINT="https://<your-project-name>.services.ai.azure.com/api/projects/<your-project-name>-project"

# Azure AI Project Deployment Name for the model
DEPLOYMENT_NAME="<your-deployment-name>"

# Resource ID for the Bing Search Connection in your AI Project
BING_CONNECTION_ID="/subscriptions/<your-subscription-id>/resourceGroups/<your-resource-group>/providers/Microsoft.CognitiveServices/accounts/<your-ai-project-name>/projects/<your-ai-project-name>-project/connections/GroundingWithBing"
```

## 2. Create the Agent in Azure AI Studio (Recommended)

The recommended approach is to create the agent using the Azure AI Studio, as this provides a visual user experience.

1. Navigate to `ai.azure.com` and select your project.
2. Go to the **Agents** tab and create a new agent.
3. Use the following instructions:
   ```markdown
   You are a chatbot having a conversation with a human.
   ALWAYS retrieve information from wikipedia, NEVER answer based simply on your knowledge.
   Then given the response, create a final answer with references ("SOURCES").
   If you don't know the answer, just say that you don't know. Don't try to make up an answer.
   ALWAYS return a "SOURCES" part in your answer.
   ```
4. Add a **Grounding with Bing** tool via the "Knowledge sources" option.
5. Note the **Agent ID** after creation.

## 3. Run the Agent

The `src/agent_service/agent_service.py` script starts a chat session with your agent.

1.  Open the `src/agent_service/agent_service.py` file.
2.  Locate the following line of code:
    ```python
    agent = project.agents.get_agent(agent_id="<youragentid>")
    ```
3.  Replace `<youragentid>` with the agent ID you noted from the Azure AI Studio.
4.  Save the file.

Now, run the agent service from the root of the repository:

```powershell
uv run src\agent_service\agent_service.py
```

The script will run through a series of pre-defined questions and print the agent's responses to the console.

---

### Alternative: Create Agent via SDK (Optional)

You can also create the agent programmatically using the `src/agent_service/setup.py` script.

**Note:** There is a known issue where the `model` parameter is not correctly set when creating the agent via the SDK. The agent will be created without a model and needs to be manually fixed the first time.

Run the script from the root of the repository:

```powershell
uv run src\agent_service\setup.py
```

After the script completes, it will print a new **Agent ID**. Copy this ID and use it in Step 3 to run
