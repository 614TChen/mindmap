
from llama_index.llms.deepseek import DeepSeek
from llama_index.core.llms import ChatMessage

# you can also set DEEPSEEK_API_KEY in your environment variables
llm = DeepSeek(model="deepseek-chat", api_key="sk-5f8e86349f4d4f13a616426ef9328074")

messages = [
    ChatMessage(
        role="system", content="You are a pirate with a colorful personality"
    ),
    ChatMessage(
        role="user", content="How many 'r's are in the word 'strawberry'?"
    ),
]

## example 1
# resp = llm.complete("Is 9.9 or 9.11 bigger?")
# print(resp)

## example 2
# resp = llm.chat(messages)
# print(resp)

## example 3
# resp = llm.stream_complete("Is 9.9 or 9.11 bigger?")
# for r in resp:
#     print(r.delta, end="")

## example 4
# resp = llm.stream_chat(messages)
# for r in resp:
#     print(r.delta, end="")