import os
from pathlib import Path
from pprint import pprint

from azure.ai.evaluation import (
    AzureOpenAIGrader,
    AzureOpenAIModelConfiguration,
    AzureOpenAIStringCheckGrader,
    AzureOpenAITextSimilarityGrader,
    CoherenceEvaluator,
    FluencyEvaluator,
    GroundednessEvaluator,
    GroundednessProEvaluator,
    QAEvaluator,
    RelevanceEvaluator,
    ResponseCompletenessEvaluator,
    RetrievalEvaluator,
    evaluate,
)
from dotenv import load_dotenv
from rich import print

from src.process_framework.wiki_chat_process import get_answer


def shorten_text(text: str, max_length: int = 180) -> str:
    """Shorten text to a maximum length with ellipsis if truncated."""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


# run this as `uv run -m src.evaluation.evaluate`
def main():
    if not load_dotenv(dotenv_path=Path(__file__).parents[2] / ".env", verbose=True):
        print("Failed to load environment variables")
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
        data="src/evaluation/wiki.jsonl",
        target=get_answer,
        evaluators={
            "relevance": RelevanceEvaluator(model_config=model_config, threshold=4),
            "retrieval": RetrievalEvaluator(
                model_config=model_config,
                threshold=3,
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

    print("Evaluation Results:")
    print(" Metrics:")
    metrics = result["metrics"]
    for key, value in metrics.items():
        print(f" - {key}: {value}")

    rows = result["rows"]
    for row in rows:
        print("\n" + "-" * 40 + "\n")
        print(f"   QUESTION: [red]{row['inputs.question']}[/red]")
        print(f"     RESPONSE: [green]{shorten_text(row['outputs.response'])}[/green]")
        print(
            f"     CONTEXT: [blue]{shorten_text(row['outputs.context'])}[/blue]"
        )  # truncate for display
        print(
            f"     GROUND TRUTH: [blue]{shorten_text(row['inputs.ground_truth_answer'])}[/blue]"
        )  # truncate for display
        print("   RELEVANCE:")
        if row["outputs.relevance.relevance_result"] == "pass":
            print("     ✅ Pass")
        else:
            print("     ❌ Fail")
        print(f"     Relevance: [blue]{row['outputs.relevance.relevance']}[/blue]")
        print(
            f"     Relevance Reason: [blue]{shorten_text(row['outputs.relevance.relevance_reason'])}[/blue]"
        )
        print("   RETRIEVAL:")
        if row["outputs.retrieval.retrieval_result"] == "pass":
            print("     ✅ Pass")
        else:
            print("     ❌ Fail")
        print(f"     Retrieval: [blue]{row['outputs.retrieval.retrieval']}[/blue]")
        print(
            f"     Retrieval Reason: [blue]{shorten_text(row['outputs.retrieval.retrieval_reason'])}[/blue]"
        )

    studio_url = result.get("studio_url")
    if studio_url:
        print(f"Studio URL: [link={studio_url}]{studio_url}[/link]")

    # print("\n\n\nFull Result:")
    # pprint(result)


if __name__ == "__main__":
    main()
