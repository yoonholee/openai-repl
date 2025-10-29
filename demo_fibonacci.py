from openai import OpenAI

from repl_agent import REPLAgent

query = "Give me the first 10 digits of the 624th Fibonacci number. Respond with only the digits, no other text."
answer = "1144992162"

client = OpenAI()
raw_response = (
    client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": query}],
    )
    .choices[0]
    .message.content
)
print(f"Raw response: {raw_response}")
print(f"Is correct: {answer in raw_response}")

print(f"Query: {query}")
print("-" * 80)
agent = REPLAgent(model="gpt-4o-mini")
response = agent.chat(query)
agent.print_tool_calls()

print(f"Response: {response}")
print(f"Is correct: {answer in response}")
