"""Tests for setup_code initialization parameter."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repl_agent import REPLAgent
import pytest


class TestSetupCode:
    """Test setup_code parameter functionality."""

    def test_setup_code_with_variables_and_functions(self):
        """Test setup_code can define variables and functions."""
        setup = """def helper(x):
    return x * 2
initial_var = 100"""
        agent = REPLAgent(setup_code=setup)
        result = agent.run("helper(21)")
        assert "42" in result
        result = agent.run("initial_var")
        assert "100" in result
        del agent

    def test_setup_code_with_classes(self):
        """Test setup_code can define classes."""
        setup = """class Calculator:
    def add(self, a, b):
        return a + b
calc = Calculator()"""
        agent = REPLAgent(setup_code=setup)
        result = agent.run("calc.add(10, 20)")
        assert "30" in result
        del agent

    def test_setup_code_with_error_handling(self):
        """Test setup_code with try/except blocks."""
        setup = """try:
    import nonexistent_module
    has_module = True
except ImportError:
    has_module = False"""
        agent = REPLAgent(setup_code=setup)
        result = agent.run("has_module")
        assert "False" in result
        del agent

    def test_setup_code_with_imports(self):
        """Test setup_code imports are usable in subsequent runs."""
        setup = "from collections import defaultdict"
        agent = REPLAgent(setup_code=setup)
        result = agent.run("d = defaultdict(int)\nd['key'] += 1\nd['key']")
        assert "1" in result
        del agent
