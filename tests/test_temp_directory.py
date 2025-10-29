"""Tests for temporary directory handling and cleanup."""
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


class TestTempDirectoryOperations:
    """Test operations in temporary directory."""

    def test_working_directory_restored(self, agent):
        """Test working directory is restored after execution."""
        original_cwd = os.getcwd()
        agent.run("import os\nprint(os.getcwd())")
        current_cwd = os.getcwd()
        assert original_cwd == current_cwd

    def test_file_operations_in_temp_dir(self, agent):
        """Test file operations work in temp directory."""
        result = agent.run("""
with open('test.txt', 'w') as f:
    f.write('test content')
with open('test.txt', 'r') as f:
    content = f.read()
content
""")
        assert "'test content'" in result


class TestWorkingDirectoryRobustness:
    """Test working directory is always restored."""

    def test_working_directory_restored_on_exception(self, agent):
        """Test working directory is restored even when code raises exception."""
        original = os.getcwd()
        result = agent.run("import os\nos.chdir('/tmp')\nraise ValueError('test')")
        assert os.getcwd() == original
        assert "Error:" in result


class TestTempDirectoryCleanup:
    """Test that temporary directory is cleaned up."""

    def test_temp_dir_cleaned_up(self):
        """Test that temp directory is cleaned up when agent is deleted."""
        agent = REPLAgent()
        temp_dir = agent.temp_dir
        assert os.path.exists(temp_dir)

        # Create some files and subdirs to ensure cleanup works recursively
        agent.run("with open('test.txt', 'w') as f: f.write('test')")
        agent.run("import os\nos.mkdir('subdir')")
        agent.run("with open('subdir/nested.txt', 'w') as f: f.write('nested')")

        del agent
        # Give it a moment for cleanup
        import time
        time.sleep(0.1)

        # Temp directory should be cleaned up
        assert not os.path.exists(temp_dir)
