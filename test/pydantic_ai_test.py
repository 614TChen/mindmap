import os
os.environ["DEEPSEEK_API_KEY"] = "sk-5f8e86349f4d4f13a616426ef9328074"

from dataclasses import dataclass

from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field



@dataclass
class SupportDependencies:
    user_name: str

class SupportOutput(BaseModel):
    infomation: str = Field(description='Tell if the user would like to start a new idea. If yes, reply the users by describing the idea. Otherwise, friendlyreply the users.')
    start_mindmap: bool = Field(description='Willing to discuss a new idea?')
    idea_description: str = Field(description='Describe the idea concisely if a new idea is started.')
    node_description: str = Field(description='Name the node of the mindmap if a new idea is started.')

agent = Agent(
    model="deepseek:deepseek-chat",
    deps_type=SupportDependencies,
    output_type=SupportOutput,
    system_prompt=f"",
)

@agent.system_prompt
async def add_user_name(ctx: RunContext[SupportDependencies]) -> str:
    return f"The user's name is {ctx.deps.user_name!r}. You are Eure, a helpful assistant inspire and help the user to build a mindmap about the idea."

deps = SupportDependencies(user_name="Johnny")
results = agent.run_sync("I want to watch a moview", deps=deps)
# results = await agent.run("I want to build a rocket", deps=deps)

print(results.output)