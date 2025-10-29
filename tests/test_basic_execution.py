"""Tests for basic code execution and expression detection."""
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


class TestSimpleExecution:
    """Test basic code execution."""

    def test_simple_expression(self, agent):
        """Test simple expression evaluation."""
        result = agent.run("2 + 2")
        assert "4" in result

    def test_multiple_statements(self, agent):
        """Test executing multiple statements."""
        result = agent.run("x = 5\ny = 10\nprint(x + y)")
        assert "15" in result

    def test_variable_persistence(self, agent):
        """Test that variables persist across calls."""
        agent.run("x = 42")
        result = agent.run("x")
        assert "42" in result


class TestErrorHandling:
    """Test error handling."""

    def test_syntax_error(self, agent):
        """Test syntax errors are caught."""
        result = agent.run("def foo(\n")
        assert "Error:" in result

    def test_runtime_error(self, agent):
        """Test runtime errors are caught."""
        result = agent.run("x = undefined_variable")
        assert "Error:" in result
        assert "NameError" in result or "undefined" in result


class TestExpressionDetection:
    """Test last-line expression auto-print."""

    def test_expression_autoprint(self, agent):
        """Test expression after statements is auto-printed."""
        result = agent.run("x = 10\ny = 20\nx + y")
        assert "30" in result

    def test_statement_no_autoprint(self, agent):
        """Test statements (def, class, for) don't auto-print."""
        result = agent.run("def foo():\n    return 1")
        # Should only see variable list, not function object printed
        assert "function" not in result.lower() or "[Variables:" in result
