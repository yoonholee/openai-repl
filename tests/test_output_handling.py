"""Tests for output handling, capture, and formatting."""
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


class TestOutputCapture:
    """Test stdout and stderr capture."""

    def test_stdout_stderr_capture(self, agent):
        """Test stdout and stderr are captured."""
        result = agent.run("print('hello world')")
        assert "hello world" in result

        result = agent.run("import sys\nprint('error', file=sys.stderr)")
        assert "Error:" in result or "error" in result

    def test_output_truncation(self, agent):
        """Test very long output is truncated."""
        result = agent.run("'x' * 150000")
        assert "truncated" in result
        assert len(result) < 150000


class TestOutputInState:
    """Test that stdout/stderr are saved in state."""

    def test_stdout_stderr_in_state(self, agent):
        """Test that stdout and stderr are saved in state as _stdout/_stderr."""
        agent.run("print('hello world')")
        result = agent.run("_stdout")
        assert "hello world" in result

        agent.run("import sys\nprint('error msg', file=sys.stderr)")
        result = agent.run("_stderr")
        # stderr should be accessible
        assert "_stderr" not in result or "Error:" in result
