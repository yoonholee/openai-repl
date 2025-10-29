"""Tests for context loading functionality."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repl_agent import REPLAgent
import pytest


@pytest.fixture
def agent():
    """Create a fresh REPLAgent instance for each test."""
    agent = REPLAgent()
    yield agent
    del agent


class TestContextLoading:
    """Test context loading from JSON and strings."""

    def test_load_json_context(self, agent):
        """Test loading JSON context (dict and list)."""
        data = {"name": "test", "value": 42}
        agent.load_context(context_json=data)
        result = agent.run("context['name']")
        assert "'test'" in result

        # Also test list
        agent2 = REPLAgent()
        agent2.load_context(context_json=[1, 2, 3, 4, 5])
        result2 = agent2.run("sum(context)")
        assert "15" in result2
        del agent2

    def test_load_string_context(self, agent):
        """Test loading string context."""
        text = "Hello, world!"
        agent.load_context(context_str=text)
        result = agent.run("context")
        assert "Hello, world!" in result
