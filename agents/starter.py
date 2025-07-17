from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field


class SupportOutput(BaseModel):
    infomation: str = Field(description='Tell if the user would like to start a new idea. If yes, reply the users by describing the idea. Otherwise, reply the users normally.')
    start_mindmap: bool = Field(description='Willing to discuss a new idea?')
    idea_description: str = Field(description='Describe the idea concisely if a new idea is started.')
    node_description: str = Field(description='Name the node of the mindmap if a new idea is started.')

starter_agent = Agent(
    model="deepseek:deepseek-chat",
    deps_type=SupportDependencies,
    output_type=SupportOutput,
    system_prompt=f"You are Eure, a helpful assistant inspire and help the user to build a mindmap about the idea.",
)

if __name__ == "__main__":
    results = starter_agent.run_sync("I want to watch a moview")
    print(results.output)
