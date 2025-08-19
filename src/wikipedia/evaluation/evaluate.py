"""
How to evaluate the process locally. More information: https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/evaluate-sdk
"""

import json

from azure.ai.evaluation import (
    AzureOpenAIModelConfiguration,
    GroundednessEvaluator,
    RelevanceEvaluator,
    RetrievalEvaluator,
    evaluate,
)
from src.wikipedia.config import config
from rich.console import Console
from src.wikipedia.process_framework.utils.observability_utils import (
    set_up_logging,
    set_up_metrics,
    set_up_tracing,
)


# This must be done before any other telemetry calls
set_up_logging()
set_up_tracing()
set_up_metrics()

from src.wikipedia.process_framework.wiki_chat_process import get_answer

from .print_eval import print_metrics, print_row

console = Console()

EVAL_DATA_PATH = "src/wikipedia/evaluation/wiki.jsonl"
OUTPUT_PATH = "src/wikipedia/evaluation/evaluation_result.json"


def main() -> None:
    """Run the evaluation pipeline and print results."""

    model_config = AzureOpenAIModelConfiguration(
        azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
        # api_key=config.AZURE_OPENAI_API_KEY,
        azure_deployment=config.AZURE_OPENAI_DEPLOYMENT_NAME,
        api_version=config.AZURE_OPENAI_API_VERSION,
    )

    result = evaluate(
        data=EVAL_DATA_PATH,
        target=get_answer,
        azure_ai_project=config.AZURE_AI_PROJECT_ENDPOINT,  # set to upload to AI Foundry
        evaluators={
            "relevance": RelevanceEvaluator(model_config=model_config, threshold=4),
            "retrieval": RetrievalEvaluator(
                model_config=model_config,
                threshold=3,
            ),
            "groundedness": GroundednessEvaluator(
                model_config=model_config,
                threshold=4,
            ),
        },
        evaluator_config={
            "default": {
                "column_mapping": {
                    "query": "${data.question}",
                    "ground_truth": "${data.ground_truth_answer}",
                    "context": "${target.context}",
                    "response": "${target.response}",
                }
            }
        },
    )

    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f, indent=2)

    console.rule("[bold green]Evaluation Results[/bold green]")
    print_metrics(result["metrics"], console)

    for row in result["rows"]:
        print_row(row, console)


# run this as `uv run -m src.evaluation.evaluate`
if __name__ == "__main__":
    main()
