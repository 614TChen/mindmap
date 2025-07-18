from dataclasses import dataclass
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field


@dataclass
class ParentNodeInfo:
    description: str

class NodeInfo(BaseModel):
    name: str = Field(..., description="The name of the item")
    description: str = Field(None, description="Optional description of the item")


class SupportOutput(BaseModel):
    # node_description: str = Field(description='Name the node of the mindmap if a new idea is started.')
    buid_new_nodes: bool = Field(description='Does current mindmap node need to be split into new nodes?')
    new_node_list: list[NodeInfo] = Field(description='List the new nodes of the mindmap.')

agent = Agent(
    model="deepseek:deepseek-chat",
    deps_type=ParentNodeInfo,
    output_type=SupportOutput,
    system_prompt=f"You are Eure, a helpful assistant inspire and help the user to build a mindmap about the idea.",
)

if __name__ == "__main__":
    deps = ParentNodeInfo(description="Exploring movie options and preferences.")
    results = agent.run_sync("I want to watch a moview", deps=deps)
    print(results.output)