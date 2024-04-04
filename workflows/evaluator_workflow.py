import asyncio
from typing import List
from temporalio import workflow
from temporalio.workflow import defn

from activites import (
    get_model_output,
    measure_latency,
    measure_meaning_similarity,
    measure_structure_similarity,
)

@defn
class EvaluatorWorkflow:
    @workflow.run
    async def run(self, models: List[str], prompts: List[List[dict]], reference_model: str) -> dict:
        model_outputs = {}
        latencies = {}
        meaning_scores = {}
        structure_scores = {}

        # Get model outputs for each prompt and model
        for model in models:
            model_outputs[model] = []
            for prompt in prompts:
                output = await workflow.execute_activity(
                    get_model_output,
                    model,
                    prompt,
                    start_to_close_timeout=60,
                )
                model_outputs[model].append(output)

        # Get model outputs for the reference model
        reference_outputs = []
        for prompt in prompts:
            output = await workflow.execute_activity(
                get_model_output,
                reference_model,
                prompt,
                start_to_close_timeout=60,
            )
            reference_outputs.append(output)

        # Measure latency for each model
        for model in models:
            latency = await workflow.execute_activity(
                measure_latency,
                model,
                start_to_close_timeout=60,
            )
            latencies[model] = latency

        # Measure meaning and structure similarity for each model against the reference model
        for model in models:
            meaning_scores[model] = []
            structure_scores[model] = []
            for reference_output, target_output in zip(reference_outputs, model_outputs[model]):
                meaning_score, structure_score = await asyncio.gather(
                    workflow.execute_activity(
                        measure_meaning_similarity,
                        reference_output,
                        target_output,
                        start_to_close_timeout=60,
                    ),
                    workflow.execute_activity(
                        measure_structure_similarity,
                        reference_output,
                        target_output,
                        start_to_close_timeout=60,
                    ),
                )
                meaning_scores[model].append(meaning_score)
                structure_scores[model].append(structure_score)

            meaning_scores[model] = sum(meaning_scores[model]) / len(meaning_scores[model])
            structure_scores[model] = sum(structure_scores[model]) / len(structure_scores[model])

        return {
            "model_outputs": model_outputs,
            "latencies": latencies,
            "meaning_scores": meaning_scores,
            "structure_scores": structure_scores,
        }