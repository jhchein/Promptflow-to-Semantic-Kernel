"""
How to evaluate the process locally. More information: https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/evaluate-sdk
"""

import json
import os

from azure.ai.evaluation import (
    AzureOpenAIModelConfiguration,
    GroundednessEvaluator,
    RelevanceEvaluator,
    RetrievalEvaluator,
    evaluate,
)
from dotenv import load_dotenv
from rich.console import Console

from src.wikipedia.process_framework.wiki_chat_process import get_answer

from .print_eval import print_metrics, print_row

console = Console()

EVAL_DATA_PATH = "src/wikipedia/evaluation/wiki.jsonl"
OUTPUT_PATH = "src/wikipedia/evaluation/evaluation_result.json"


def main() -> None:
    """Run the evaluation pipeline and print results."""
    if not load_dotenv():
        print("Evaluate: Failed to load environment variables")
        return

    endpoint = os.environ.get("ENDPOINT")
    api_key = os.environ.get("API_KEY")
    deployment_name = os.environ.get("DEPLOYMENT_NAME")
    api_version = os.environ.get("AZURE_API_VERSION", "2025-04-01-preview")
    assert endpoint, "Please set the ENDPOINT environment variable"
    assert api_key, "Please set the API_KEY environment variable"
    assert deployment_name, "Please set the DEPLOYMENT_NAME environment variable"
    assert api_version, "Please set the AZURE_API_VERSION environment variable"

    model_config = AzureOpenAIModelConfiguration(
        azure_endpoint=endpoint,
        api_key=api_key,
        azure_deployment=deployment_name,
        api_version=api_version,
    )

    result = evaluate(
        data=EVAL_DATA_PATH,
        target=get_answer,
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
