# openai-repl

A single-file Python REPL that enables LLMs to execute Python code via function calling. The model can iteratively run code, see outputs, and refine its approach to answer questions.

**Supported providers:** OpenAI, Google Gemini (via OpenAI compatibility layer)

Inspired by the [RLM](https://github.com/alexzhang13/rlm) repository.

## Quick Start

```bash
# Install
uv pip install -e .

# Set API key (choose your provider)
export OPENAI_API_KEY="your-openai-key"        # For OpenAI models
export GEMINI_API_KEY="your-gemini-key"        # For Gemini models
```

## Usage

**Basic chat:**

```python
from repl_agent import REPLAgent

# OpenAI
agent = REPLAgent(model="gpt-4o-mini")

# Gemini (auto-detected from model name)
agent = REPLAgent(model="gemini-2.0-flash-exp")

response = agent.chat("Give me the first 10 digits of the 624th Fibonacci number")
print(response)
agent.print_tool_calls()  # See what code the model executed
```

**Direct code execution:**

```python
result = agent.run("2 ** 100")  # Last line auto-prints (Jupyter-style)
print(result)
```

**Load context (for large data):**

```python
agent.load_context(context_json={"data": [1, 2, 3]})
agent.run("sum(context['data'])")  # Access via 'context' variable
```

## Features

- Stateful execution (variables persist across runs)
- Jupyter-style auto-print (last line expressions)
- Isolated temp directories with auto-cleanup
- Context loading for JSON/string data

## Demos

```bash
uv run python demo_fibonacci.py     # Basic computation
uv run python demo_literature.py    # Process large text (Moby Dick)
```

## Tests

```bash
uv run pytest                        # Run all tests
uv run pytest --cov=repl_agent      # With coverage
uv run pytest tests/test_*.py -v    # Specific tests
```
