from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field


class NodeInfo(BaseModel):
    name: str = Field(..., description="The name of the item")
    description: str = Field(None, description="Optional description of the item")

class SupportOutput(BaseModel):
    reply: str = Field(description='Tell if the user would like to start a new idea. If yes, reply the users by describing the idea. Otherwise, reply the users normally.')
    start_mindmap: bool = Field(description='Willing to discuss a new idea?')
    idea_description: str = Field(description='Describe the idea concisely if a new idea is started.')
    node_description: str = Field(description='Name the node of the mindmap if a new idea is started.')
    new_node_list: list[NodeInfo] = Field(description='List the new nodes of the mindmap if a new idea is started.')
    dicuss_next: str = Field(description='Based on the new node list, suggest the user what to discuss next, return the node name.')

starter_agent = Agent(
    model="deepseek:deepseek-chat",
    output_type=SupportOutput,
    system_prompt="You are Eure, a helpful assistant inspire and help the user to build a mindmap about the idea.",
)


def run_starter_agent(user_message: str):
    """运行starter agent并返回结果"""
    try:
        results = starter_agent.run_sync(user_message)
        print(results.output)
        return results.output
    except Exception as e:
        print(f"Starter agent error: {e}")
        return None


if __name__ == "__main__":
    results = run_starter_agent("I want to build a rocket")
    print(results.new_node_list)
