from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activites import say_hello

@workflow.defn
class HelloWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        return await workflow.execute_activity(
            say_hello, name, start_to_close_timeout=60
        )