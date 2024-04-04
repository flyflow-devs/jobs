import asyncio
import os
import time
from flyflowclient import OpenAI
from scipy.spatial.distance import cosine
import json
from temporalio import activity

@activity.defn
async def get_model_output(model: str, prompt: list) -> str:
    client = OpenAI(base_url="https://api.flyflow.dev/v1", api_key=os.getenv("FLYFLOW_API_KEY"))
    response = client.chat.completions.create(
        model=model,
        messages=prompt,
        tags=["eval"]
    )
    return response.choices[0].message.content

@activity.defn
async def measure_latency(model: str) -> float:
    client = OpenAI(base_url="https://api.flyflow.dev/v1", api_key=os.getenv("FLYFLOW_API_KEY"))
    prompt = [{"role": "user", "content": "What's the meaning of life?"}]
    total_tokens = 0
    start_time = time.time()

    for _ in range(7):
        response = client.chat.completions.create(
            model=model,
            messages=prompt,
            tags=["latency_test"]
        )
        total_tokens += response.usage.total_tokens

    end_time = time.time()
    elapsed_time = end_time - start_time
    tokens_per_second = total_tokens / elapsed_time
    return tokens_per_second

@activity.defn
async def measure_meaning_similarity(reference_output: str, target_output: str) -> float:
    client = OpenAI(base_url="https://api.flyflow.dev/v1", api_key=os.getenv("FLYFLOW_API_KEY"))
    reference_embedding = client.embeddings.create(input=reference_output, model="text-embedding-ada-002").data[0].embedding
    target_embedding = client.embeddings.create(input=target_output, model="text-embedding-ada-002").data[0].embedding
    cosine_similarity = 1 - cosine(reference_embedding, target_embedding)
    return cosine_similarity

@activity.defn
async def measure_structure_similarity(reference_output: str, target_output: str) -> float:
    client = OpenAI(base_url="https://api.flyflow.dev/v1", api_key=os.getenv("FLYFLOW_API_KEY"))
    prompt = [
        {"role": "system", "content": "You are an AI assistant that compares the structural similarity of two text inputs on a scale of 1-100. Output your response as a JSON object with a 'similarity_score' key."},
        {"role": "user", "content": f"Reference output:\n{reference_output}\n\nTarget output:\n{target_output}\n\nCompare the structural similarity of the reference output and the target output on a scale of 1-100. Respond with a JSON object containing the 'similarity_score' key."}
    ]
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=prompt,
        response_format={"type": "json_object"},
        tags=["structure_similarity"]
    )
    json_response = json.loads(response.choices[0].message.content)
    similarity_score = float(json_response["similarity_score"])
    return similarity_score