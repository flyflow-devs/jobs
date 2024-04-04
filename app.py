import asyncio
import os
from dotenv import load_dotenv
from temporalio.client import Client, TLSConfig
from temporalio.worker import Worker
from activites import say_hello, get_model_output, measure_meaning_similarity, measure_latency, measure_structure_similarity
from workflows import HelloWorkflow, EvaluatorWorkflow

async def main():
    # Load environment variables from .env file
    load_dotenv()

    # Get TLS certificates from environment variables
    client_cert = "\n".join(os.getenv("TEMPORAL_MTLS_TLS_CERT").split("\\n"))
    client_key = "\n".join(os.getenv("TEMPORAL_MTLS_TLS_KEY").split("\\n"))

    # Create a Temporal client with TLS configuration
    client = await Client.connect(
        os.getenv("TEMPORAL_HOST_URL"),
        namespace=os.getenv("TEMPORAL_NAMESPACE"),
        tls=TLSConfig(
            client_cert=client_cert.encode(),
            client_private_key=client_key.encode(),
        ),
    )

    # Create a Temporal worker
    worker = Worker(
        client,
        task_queue="main-queue",
        workflows=[HelloWorkflow, EvaluatorWorkflow],
        activities=[say_hello, get_model_output, measure_meaning_similarity, measure_latency, measure_structure_similarity],
    )

    # Run the worker
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())