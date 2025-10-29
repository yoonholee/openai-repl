"""Tests for state persistence and isolation."""
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


class TestStatePersistence:
    """Test that state persists across executions."""

    def test_function_persistence(self, agent):
        """Test defined functions persist."""
        agent.run("def double(x):\n    return x * 2")
        result = agent.run("double(21)")
        assert "42" in result

    def test_import_persistence(self, agent):
        """Test imports persist across calls."""
        agent.run("import math")
        result = agent.run("math.pi")
        assert "3.14" in result

    def test_class_persistence(self, agent):
        """Test class definitions persist."""
        agent.run("class MyClass:\n    def __init__(self, val):\n        self.val = val")
        agent.run("obj = MyClass(100)")
        result = agent.run("obj.val")
        assert "100" in result


class TestStateIsolation:
    """Test that different agents have isolated state."""

    def test_state_isolation(self):
        """Test different agents have isolated state."""
        agent1 = REPLAgent()
        agent2 = REPLAgent()
        agent1.run("x = 100")
        result = agent2.run("x")
        assert "Error" in result or "NameError" in result
        del agent1
        del agent2
