"""Tests for security restrictions and blocked built-ins."""
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


class TestBlockedBuiltins:
    """Test that dangerous built-ins are blocked."""

    @pytest.mark.parametrize("code,builtin_name", [
        ("eval('2+2')", "eval"),
        ("exec('x=1')", "exec"),
        ("compile('x=1', '<string>', 'exec')", "compile"),
        ("globals()", "globals"),
        ("locals()", "locals"),
        ("x = input('test')", "input"),
    ])
    def test_dangerous_builtins_blocked(self, agent, code, builtin_name):
        """Test that dangerous built-ins are blocked."""
        result = agent.run(code)
        assert "Error:" in result


class TestSafeBuiltins:
    """Test that safe built-ins still work correctly."""

    def test_common_builtins_work(self, agent):
        """Test common safe built-ins work."""
        # Range and iteration
        result = agent.run("list(range(5))")
        assert "[0, 1, 2, 3, 4]" in result

        # Math operations
        result = agent.run("sum([1, 2, 3])")
        assert "6" in result

        # Type checking
        result = agent.run("isinstance(42, int)")
        assert "True" in result

    def test_file_operations_work(self, agent):
        """Test file operations are allowed."""
        result = agent.run("""
with open('test.txt', 'w') as f:
    f.write('test')
with open('test.txt', 'r') as f:
    content = f.read()
content
""")
        assert "'test'" in result

    def test_imports_work(self, agent):
        """Test imports are allowed."""
        result = agent.run("import json\njson.dumps({'key': 'value'})")
        assert '"key"' in result and '"value"' in result


class TestExceptionHandling:
    """Test that exception classes are available."""

    def test_can_raise_exceptions(self, agent):
        """Test can raise standard exceptions."""
        result = agent.run("raise ValueError('test error')")
        assert "Error:" in result
        assert "ValueError" in result

    def test_can_catch_exceptions(self, agent):
        """Test can catch exceptions."""
        result = agent.run("""
try:
    x = 1 / 0
except ZeroDivisionError:
    caught = True
caught
""")
        assert "True" in result

    def test_exception_types_available(self, agent):
        """Test exception types are accessible."""
        result = agent.run("ValueError")
        assert "Error:" not in result
