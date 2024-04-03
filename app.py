import asyncio
from dotenv import load_dotenv
from temporalio.client import Client
from temporalio.worker import Worker
from workflows.hello_workflow import HelloWorkflow
from activites.hello_activity import say_hello

async def main():
    # Load environment variables from .env file
    load_dotenv()

    # Create a Temporal client
    client = await Client.connect("localhost:7233")

    # Create a Temporal worker
    worker = Worker(
        client,
        task_queue="hello-task-queue",
        workflows=[HelloWorkflow],
        activities=[say_hello],
    )

    # Run the worker
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())