"""Tests for edge cases and special scenarios."""
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


class TestEmptyAndWhitespace:
    """Test handling of empty and whitespace-only code."""

    def test_empty_whitespace_comment_code(self, agent):
        """Test executing empty, whitespace, and comment-only code."""
        # Empty
        result = agent.run("")
        assert "[Execution:" in result

        # Whitespace
        result = agent.run("   \n\n   \t   ")
        assert "[Execution:" in result

        # Comment only
        result = agent.run("# This is just a comment")
        assert "[Execution:" in result


class TestUnicodeHandling:
    """Test unicode and special character handling."""

    def test_unicode_handling(self, agent):
        """Test unicode characters in strings, variables, and output."""
        # Unicode in string literals
        result = agent.run("'Hello 世界 🌍'")
        assert "Hello" in result

        # Unicode in variables
        result = agent.run("emoji = '🚀'\nemoji")
        assert "🚀" in result

        # Unicode in print output
        result = agent.run("print('日本語')")
        assert "日本語" in result


class TestComplexExpressions:
    """Test complex expression evaluation."""

    def test_advanced_expressions(self, agent):
        """Test nested, lambda, and generator expressions."""
        # Nested list comprehensions
        result = agent.run("[[i*j for i in range(3)] for j in range(3)]")
        assert "[[0, 0, 0], [0, 1, 2], [0, 2, 4]]" in result

        # Lambda expressions
        result = agent.run("(lambda x: x**2)(5)")
        assert "25" in result

        # Generator expressions
        result = agent.run("list(x**2 for x in range(5))")
        assert "[0, 1, 4, 9, 16]" in result


class TestSpecialValues:
    """Test handling of special values."""

    def test_special_value_handling(self, agent):
        """Test None, booleans, large numbers, and floats."""
        # None value (not auto-printed)
        result = agent.run("x = None\nx")
        assert result.count("None") <= 1

        # Boolean operations
        result = agent.run("True and False")
        assert "False" in result

        # Large numbers
        result = agent.run("10**50")
        assert "100000000000000000000000000000000000000000000000000" in result


class TestMultilineCode:
    """Test multiline code execution."""

    def test_multiline_code(self, agent):
        """Test multiline functions, comments, and strings."""
        # Multiline function
        code = """def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
factorial(5)"""
        result = agent.run(code)
        assert "120" in result

        # Code with comments
        code = """# Calculate sum
x = 10  # first number
y = 20  # second number
x + y"""
        result = agent.run(code)
        assert "30" in result


class TestErrorRecovery:
    """Test recovery from errors."""

    def test_error_recovery_and_state_preservation(self, agent):
        """Test that agent recovers from errors and preserves state."""
        # Define a variable
        agent.run("x = 100")

        # Execute code that causes an error
        result = agent.run("y = undefined_variable")
        assert "Error:" in result

        # State should be preserved and agent should still work
        result = agent.run("x")
        assert "100" in result

        # New operations should work fine
        result = agent.run("z = 42\nz")
        assert "42" in result
